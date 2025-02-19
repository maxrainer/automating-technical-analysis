import streamlit as st 
import gc
from app.data_sourcing import Data_Sourcing, data_update
from app.graph import Visualization
from app.indicator_analysis import Indications
from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np

gc.collect()


def main(app_data):
    analysis, analysis_days = []
    current_prices, requested_prediction_prices, changes, requested_prediction_actions = []
    buy_prices, sell_prices = []
    exchange = 'Binance'
    market = 'USDT'
    indication = 'Predicted'
    # to be changed
 #   equity = 'BTC'
    risk='Medium'
    equitys = ['BTC', 'SOL']
    

    st.sidebar.subheader('Interval:')
    interval = st.sidebar.selectbox('', ('1 Minute', '3 Minute', '5 Minute', '15 Minute', '30 Minute', '1 Hour', '6 Hour', '12 Hour', '1 Day', '1 Week'), index = 8)

    for equity in equitys: 
        analysis.append(Visualization(exchange, interval, equity, indication, action_model, price_model, market))
        analysis_days.append(Indications(exchange, '1 Day', equity, market))

    # analysis = Visualization(exchange, interval, equity, indication, action_model, price_model, market)
    # analysis_day = Indications(exchange, '1 Day', equity, market)
    count = 0
    for analyse in analysis: 
        current_price = float(analyse.df['Adj Close'][-1])
        requested_prediction_price = float(analyse.requested_prediction_price)
        risks = {'Low': [analysis_days[count].df['S1'].values[-1], analysis_days[count].df['R1'].values[-1]], 
            'Medium': [analysis_days[count].df['S2'].values[-1], analysis_days[count].df['R2'].values[-1]],   
            'High': [analysis_days[count].df['S3'].values[-1], analysis_days[count].df['R3'].values[-1]],}
        buy_prices.append(f'{float(risks[risk][0]):,.8f}')
        sell_prices.append(f'{float(risks[risk][1]):,.8f}')
        current_prices.append(f'{float(analyse.df['Adj Close'][-1]):,.8f}')
        changes.append(float(analyse.df['Adj Close'].pct_change()[-1]) * 100)
        requested_prediction_prices.append(f'{float(analyse.requested_prediction_price):,.8f}')
        requested_prediction_actions.append(str(analyse.requested_prediction_action))
        count += 1

    # requested_date = analysis.df.index[-1]
    # current_price = float(analysis.df['Adj Close'][-1])
    # change = float(analysis.df['Adj Close'].pct_change()[-1]) * 100
    # requested_prediction_price = float(analysis.requested_prediction_price)
    # requested_prediction_action = analysis.requested_prediction_action
    # risks = {'Low': [analysis_day.df['S1'].values[-1], analysis_day.df['R1'].values[-1]], 
    #         'Medium': [analysis_day.df['S2'].values[-1], analysis_day.df['R2'].values[-1]],   
    #         'High': [analysis_day.df['S3'].values[-1], analysis_day.df['R3'].values[-1]],}

    # buy_price = float(risks[risk][0])
    # sell_price = float(risks[risk][1])

    # st.markdown(buy_price)

    # current_price = f'{float(current_price):,.8f}'
    # requested_prediction_price = f'{float(requested_prediction_price):,.8f}'
    # buy_price = f'{float(buy_price):,.8f}'
    # sell_price = f'{float(sell_price):,.8f}'

    df1 = pd.DataFrame(
        {
            "Coin": [equitys],
            "Predicted Action": [requested_prediction_actions],
            "Current Price": [current_prices],
            "Prediction Price": [requested_prediction_prices],
            "Buy Price": [buy_prices],
            "Sell Price": [sell_prices]
        }
    )
    st.table(df1)
    st.markdown(f'test')



if __name__ == '__main__':
    import warnings
    import gc
    warnings.filterwarnings("ignore") 

    action_model = load_model("models/action_prediction_model.h5")
    price_model = load_model("models/price_prediction_model.h5")

    app_data = Data_Sourcing()
    gc.collect()

    main(app_data = app_data)