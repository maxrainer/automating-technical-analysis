import streamlit as st 
import gc
from app.data_sourcing import Data_Sourcing, data_update
from app.graph import Visualization
from app.indicator_analysis import Indications
from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np

gc.collect()

def equity_to_link(equity):
    return "https://www.binance.com/en/trade/" + equity + "_USDC?_from=markets&type=spot"

def main(app_data):
    analysis = []
    analysis_days = []
    current_prices = []
    requested_prediction_prices = []
    changes = []
    requested_prediction_actions = []
    buy_prices = []
    sell_prices = []
    margins = []
    binance_urls = []

    
    exchange = 'Binance'
    market = 'USDT'
    indication = 'Predicted'
    # to be changed
    risk='Medium'

    data_source = pd.read_csv('market_data/binance_reporting.txt')
    equitys = data_source['Currency']
    if equitys.size == 0: 
        st.markdown("no Equity, exit now")
        exit
    
    st.sidebar.subheader('Interval:')
    interval = st.sidebar.selectbox('', ('1 Minute', '3 Minute', '5 Minute', '15 Minute', '30 Minute', '1 Hour', '6 Hour', '12 Hour', '1 Day', '1 Week'), index = 8)

    st.title(f'AI Driven Reporting.')
    st.subheader(f'Data Sourced from {exchange}.')

    _to_be_deleted = []
    _equity_percentage = 100/equitys.size
    progress_bar = st.progress(0, "Awaiting first carrier pigeon. Please don't shoot.")
    percentage_complete = 0
 #   for percentage_complete in range(100):
    for equity in equitys: 
        percentage_complete = int(percentage_complete + _equity_percentage)
        if percentage_complete > 100: 
            percentage_complete = 100
        try:
            analysis.append(Visualization(exchange, interval, equity, indication, action_model, price_model, market))
            analysis_days.append(Indications(exchange, '1 Day', equity, market))
        except: 
            progress_bar.progress(percentage_complete, text=f'SHOT BY HUNTER! **{equity}** is dead')
            _to_be_deleted.append(pd.Index(equitys).get_loc(equity))
        else: 
            progress_bar.progress(percentage_complete, text=f'Carrier pigeon arrived for **{equity}**')
            binance_urls.append(equity_to_link(equity))
    progress_bar.empty()
    for d in _to_be_deleted:
        equitys = equitys.drop(d)

    count = 0
    for analyse in analysis: 
        current_price = float(analyse.df['Adj Close'][-1])
        requested_prediction_price = float(analysis[count].requested_prediction_price)
        risks = {'Low': [analysis_days[count].df['S1'].values[-1], analysis_days[count].df['R1'].values[-1]], 
            'Medium': [analysis_days[count].df['S2'].values[-1], analysis_days[count].df['R2'].values[-1]],   
            'High': [analysis_days[count].df['S3'].values[-1], analysis_days[count].df['R3'].values[-1]],}
        buy_prices.append(f'{float(risks[risk][0]):,.8f}')
        sell_prices.append(f'{float(risks[risk][1]):,.8f}')
        current_prices.append(f'{float(current_price):,.8f}')
        requested_prediction_prices.append(f'{float(requested_prediction_price):,.8f}')
        changes.append(float(analyse.df['Adj Close'].pct_change()[-1]) * 100)
        requested_prediction_actions.append(analyse.requested_prediction_action)
        margin = (1-(float(risks[risk][1]) / float(risks[risk][0])))*100
        margins.append(f'{float(margin)}')

        count += 1

    df1 = pd.DataFrame(
        {
            "coin": binance_urls,
            "action": requested_prediction_actions,
            "current": current_prices,
            "prediction": requested_prediction_prices,
            "change": changes,
            "buy": buy_prices,
            "sell": sell_prices,
            "margin": margins
        },
    )
    requested_date = analysis[0].df.index[-1]
    st.markdown(f'**Prediction Date & Time (UTC):** {str(requested_date)}.')

    event = st.dataframe(
        df1,
        hide_index=True,
        width=1200,
        column_order=["coin", "action", "current", "change", "prediction", "buy", "sell"],
        column_config={
            "coin": st.column_config.LinkColumn(
                "Coin",
                help="trading link to binance.com",
                display_text=r"https://www.binance.com/en/trade/(.*?)_USDC.*"
            ),
            "action": "Action",
            "current": "Current Price",
            "change":  st.column_config.NumberColumn(
                    "Change(%)",
                    format="%.2f",
            ),
            "prediction": "Predicted Price",
            "buy": "Buy Price",
            "sell": "Sell Price",
            "margin": "Margin( %)"
        }
    )

if __name__ == '__main__':
    import warnings
    import gc
    warnings.filterwarnings("ignore") 

    action_model = load_model("models/action_prediction_model.h5")
    price_model = load_model("models/price_prediction_model.h5")

    app_data = Data_Sourcing()
    gc.collect()

    main(app_data = app_data)