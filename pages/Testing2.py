import streamlit as st 
import gc
from app.data_sourcing import Data_Sourcing, data_update
from app.graph import Visualization
from app.indicator_analysis import Indications
from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np
import time

exchange = 'Binance'
market = 'USDT'
indication = 'Predicted'
# to be changed
risk='Medium'


def get_data_source():
    data_source = pd.read_csv('market_data/binance_reporting.txt')
    equitys = data_source['Currency']
    if equitys.size == 0: 
        st.markdown("no Equity, exit now")
        exit
    return equitys

def equity_to_link(equity):
    return "https://www.binance.com/en/trade/" + equity + "_USDC?_from=markets&type=spot"

def compute_model(equitys, interval):
    analysis = []
    analysis_days = []
    binance_urls = []
    coins = []

    _to_be_deleted = []
    _equity_percentage = 100/equitys.size
    progress_bar = st.progress(0, "Awaiting first carrier pigeon. Please don't shoot.")
    percentage_complete = 0
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
            coins.append(equity)

    progress_bar.empty()
    for d in _to_be_deleted:
        equitys = equitys.drop(d)
    return analysis, analysis_days, binance_urls, coins

def format_usd(usd):
    if (float(usd) < 0):
        usd = f'{float(usd):,.8f}'
    elif (float(usd) >= 100):
        usd = f'{float(usd):,.2f}'
    else:   
        usd = f'{float(usd):,.6f}'
    return usd 

def analyze(ds, analysis, analysis_days):
    ds['current_prices'] = []
    ds['requested_prediction_prices'] = []
    ds['prediction_percentage'] = []
    ds['changes'] = []
    ds['requested_prediction_actions'] = []
    ds['buy_prices'] = []
    ds['sell_prices'] = []
    ds['margins'] = []

    count = 0
    for analyse in analysis: 
        current_price = float(analyse.df['Adj Close'][-1])
        requested_prediction_price = float(analysis[count].requested_prediction_price)
        prediction_percentage = (float((requested_prediction_price/current_price)*100)-100)
        risks = {'Low': [analysis_days[count].df['S1'].values[-1], analysis_days[count].df['R1'].values[-1]], 
            'Medium': [analysis_days[count].df['S2'].values[-1], analysis_days[count].df['R2'].values[-1]],   
            'High': [analysis_days[count].df['S3'].values[-1], analysis_days[count].df['R3'].values[-1]],}
        ds['buy_prices'].append(format_usd(risks[risk][0]))
        ds['sell_prices'].append(format_usd(risks[risk][1]))
        ds['current_prices'].append(format_usd(current_price))
        ds['requested_prediction_prices'].append(format_usd(requested_prediction_price))
        ds['prediction_percentage'].append(f'{float(prediction_percentage):,.2f}')
        ds['changes'].append(float(analyse.df['Adj Close'].pct_change()[-1]) * 100)
        ds['requested_prediction_actions'].append(analyse.requested_prediction_action)
        margin = ((float(risks[risk][1]) / float(risks[risk][0])*100)-100)
        ds['margins'].append(f'{float(margin):,.2f}')
        count += 1
    return ds

def get_panda_dataframe(ds):
    panda_frame = pd.DataFrame(
        {
            "coin": ds['binance_urls'],
            "action": ds['requested_prediction_actions'],
            "current": ds['current_prices'],
            "change": ds['changes'],
            "prediction": ds['requested_prediction_prices'],
            "prediction_percentage": ds['prediction_percentage'],
            "buy": ds['buy_prices'],
            "sell": ds['sell_prices'],
            "margin": ds['margins']
        }
    )
    return panda_frame

@st.fragment
def get_dataframe(pdf, ds):
    event = st.dataframe(
        pdf,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "coin": st.column_config.LinkColumn(
                "Coin",
                help="trading link to binance.com",
                display_text=r"https://www.binance.com/en/trade/(.*?)_USDC.*"
            ),
            "action": "Action",
            "current": "Current($)",
            "change":  st.column_config.NumberColumn(
                    "Past",
                    format="%.2f%%"
            ),
            "prediction": "Forecast($)",
            "prediction_percentage": st.column_config.NumberColumn(
                "Future",
                format="%.2f%%"
            ),
            "buy": "Buy Limit",
            "sell": "Sell Limit",
            "margin": st.column_config.NumberColumn(
                "Margin",
                format="%.2f%%"
            )
        }
    )
    if event.selection['rows']:
        order_dialog(ds, event.selection['rows'][0])
        
@st.dialog("Execute Order")
def order_dialog(ds, row):
    st.markdown(f"Trigger Limit Orders for Coin {ds['coins'][row]} on {exchange}.")
    st.markdown(f"Predicted Price in {st.session_state.interval.replace(',','')} is ${ds['requested_prediction_prices'][row]}")
    order_coin_amount = st.number_input("amount", value=1)
    col1, col2 = st.columns(2)
    with(col1):
        limit_buy = st.text_input("Buy Limit Order", value=float(ds['buy_prices'][row].replace(",",""),))
        st.write("Total buy price: $", float(limit_buy * order_coin_amount))
    with(col2):
        buy_select = st.button("Buy", )
    limit_sell = st.text_input("Sell Limit", value=float(ds['sell_prices'][row].replace(",",""),))
    st.write("The current number is ", limit_sell)

def main(ds):
    exchange = 'Binance'
    st.sidebar.subheader('Interval:')
    st.session_state.interval = st.sidebar.selectbox('', ('1 Minute', '3 Minute', '5 Minute', '15 Minute', '30 Minute', '1 Hour', '6 Hour', '12 Hour', '1 Day', '1 Week'), index = 8)

    st.title(f'AI Driven Reporting.')
    st.subheader(f'Data Sourced from {exchange}')

    equitys = get_data_source()
    analysis, analysis_days, ds['binance_urls'], ds['coins'] = compute_model(equitys, st.session_state.interval)
    ds = analyze(ds, analysis, analysis_days)
    panda_dataframe = get_panda_dataframe(ds)
    get_dataframe(panda_dataframe, ds)

if __name__ == '__main__':
    import warnings
    import gc
    warnings.filterwarnings("ignore") 
    ds = {}

    action_model = load_model("models/action_prediction_model.h5")
    price_model = load_model("models/price_prediction_model.h5")

    gc.collect()
    main(ds)