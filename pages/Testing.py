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
    st.session_state.analysis = []
    st.session_state.analysis_days = []
    st.session_state.binance_urls = []

    _to_be_deleted = []
    _equity_percentage = 100/equitys.size
    progress_bar = st.progress(0, "Awaiting first carrier pigeon. Please don't shoot.")
    percentage_complete = 0
    for equity in equitys: 
        percentage_complete = int(percentage_complete + _equity_percentage)
        if percentage_complete > 100: 
            percentage_complete = 100
        try:
            st.session_state.analysis.append(Visualization(exchange, interval, equity, indication, action_model, price_model, market))
            st.session_state.analysis_days.append(Indications(exchange, '1 Day', equity, market))
        except: 
            progress_bar.progress(percentage_complete, text=f'SHOT BY HUNTER! **{equity}** is dead')
            _to_be_deleted.append(pd.Index(equitys).get_loc(equity))
        else: 
            progress_bar.progress(percentage_complete, text=f'Carrier pigeon arrived for **{equity}**')
            st.session_state.binance_urls.append(equity_to_link(equity))
    progress_bar.empty()
    for d in _to_be_deleted:
        equitys = equitys.drop(d)

def analyze(analysis, analysis_days):
    st.session_state.current_prices = []
    st.session_state.requested_prediction_prices = []
    st.session_state.changes = []
    st.session_state.requested_prediction_actions = []
    st.session_state.buy_prices = []
    st.session_state.sell_prices = []
    st.session_state.margins = []

    count = 0
    for analyse in analysis: 
        st.write(analyse)
        current_price = float(analyse.df['Adj Close'][-1])
        requested_prediction_price = float(analysis[count].requested_prediction_price)
        risks = {'Low': [analysis_days[count].df['S1'].values[-1], analysis_days[count].df['R1'].values[-1]], 
            'Medium': [analysis_days[count].df['S2'].values[-1], analysis_days[count].df['R2'].values[-1]],   
            'High': [analysis_days[count].df['S3'].values[-1], analysis_days[count].df['R3'].values[-1]],}
        st.session_state.buy_prices.append(f'{float(risks[risk][0]):,.6f}')
        st.session_state.sell_prices.append(f'{float(risks[risk][1]):,.6f}')
        st.session_state.current_prices.append(f'{float(current_price):,.6f}')
        st.session_state.requested_prediction_prices.append(f'{float(requested_prediction_price):,.6f}')
        st.session_state.changes.append(float(analyse.df['Adj Close'].pct_change()[-1]) * 100)
        st.session_state.requested_prediction_actions.append(analyse.requested_prediction_action)
        margin = ((float(risks[risk][1]) / float(risks[risk][0])*100)-100)
        st.session_state.margins.append(f'{float(margin):,.2f}')

def get_dataset():
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(
            {
                "coin": st.session_state.equitys,
                "action": st.session_state.requested_prediction_actions,
                "prediction": st.session_state.requested_prediction_prices,
                "buy": st.session_state.buy_prices,
                "sell": st.session_state.sell_prices
            }
        )
    return st.session_state.df

@st.fragment
def get_dataframe(dataset):
    event = st.dataframe(
        st.session_state.df,
        key = "data",
        on_select="rerun",
        selection_mode="single-row"
    )
    if event.selection['rows']:
        order_dialog(event.selection['rows'][0])
        
@st.dialog("Execute Order")
def order_dialog(row):
    st.markdown(f'Trigger Limit Orders for Coin {st.session_state.equitys[row]} on {exchange}.')
    limit_buy = st.text_input("Buy Limit", value=float(st.session_state.buy_prices[row].replace(",",""),))
    st.write("The current number is ", limit_buy)
    limit_sell = st.text_input("Sell Limit", value=float(st.session_state.sell_prices[row].replace(",",""),))
    st.write("The current number is ", limit_sell)

def main():
    exchange = 'Binance'
    st.sidebar.subheader('Interval:')
    interval = st.sidebar.selectbox('', ('1 Minute', '3 Minute', '5 Minute', '15 Minute', '30 Minute', '1 Hour', '6 Hour', '12 Hour', '1 Day', '1 Week'), index = 8)

    st.title(f'AI Driven Reporting.')
    st.subheader(f'Data Sourced from {exchange}')

    st.session_state.equitys = get_data_source()
    compute_model(st.session_state.equitys, interval)
    analyze(st.session_state.analysis, st.session_state.analysis_days)
    st.session_state.df = get_dataset()
    get_dataframe(st.session_state.df)

if __name__ == '__main__':
    import warnings
    import gc
    warnings.filterwarnings("ignore") 

    action_model = load_model("models/action_prediction_model.h5")
    price_model = load_model("models/price_prediction_model.h5")

    gc.collect()
    main()