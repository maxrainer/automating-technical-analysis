import streamlit as st 
import gc
from app.data_sourcing import Data_Sourcing, data_update
from app.graph import Visualization
from app.indicator_analysis import Indications
from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from time import sleep

exchange = 'Binance'
market = 'USDT'
indication = 'Predicted'


def get_data_source():
    if st.session_state.source_file == 'Short':
        data_source = pd.read_csv('market_data/binance_reporting_short.txt')
    elif st.session_state.source_file == 'Medium':
        data_source = pd.read_csv('market_data/binance_reporting.txt')
    #all
    else:
        data_source = pd.read_csv('market_data/binance_reporting_long.txt')


    equitys = data_source['Currency']
    if equitys.size == 0: 
        st.markdown("no Equity, exit now")
        exit
    return equitys

def equity_to_link(equity):
    return "https://www.binance.com/en/trade/" + equity + "_USDC?_from=markets&type=spot"

def get_lock(lock):
    while lock: 
        sleep(0.1)
    lock = True

def release_lock(lock):
    lock = False

def compute_per_equity(equity, equitys, analysis, analysis_days, binance_urls, to_be_deleted, interval, lock):
    try:
        vis = Visualization(exchange, interval, equity, indication, action_model, price_model, market)
        ind = Indications(exchange, interval, equity, market)
    except Exception as error: 
        print("error" + str(error))
        to_be_deleted.append(pd.Index(equitys).get_loc(equity))
    else: 
        get_lock(lock)
        analysis.append(vis)
        analysis_days.append(ind)
        binance_urls.append(equity_to_link(equity))
        release_lock(lock)
    return equity

def compute_model(equitys, interval):
    max_threads = 30
    analysis = []
    analysis_days = []
    binance_urls = []
    coins = []

    to_be_deleted = []
    _equity_percentage = float(1.0/float(equitys.size))
    progress_bar = st.progress(0, "Awaiting first carrier pigeon. Please don't shoot.")
    percentage_complete = float(0.0)
    pool = ThreadPoolExecutor(max_workers=max_threads)
    threads = []

    for equity in equitys:
        threads.append(pool.submit(compute_per_equity, equity, equitys, analysis, analysis_days, binance_urls, to_be_deleted, interval, lock=False))

    for t in threads:
        percentage_complete = float(percentage_complete + _equity_percentage)
        while not t.done():
            sleep(1)
        equity = t.result()
        progress_bar.progress(percentage_complete, text=f'Carrier pigeon arrived for **{equity}**')

    progress_bar.empty()
    for d in to_be_deleted:
        equitys = equitys.drop(d)
    return analysis, analysis_days, binance_urls, coins

def format_usd(usd):
    if float(usd) >= 100:
        usd = f'{float(usd):,.2f}'
    elif float(usd) >= 10:   
        usd = f'{float(usd):,.6f}'
    else:
        usd = f'{float(usd):,.8f}'
    return usd 

def get_confidence(analysis):
    accuracy_threshold = {analysis.score_action: 75., analysis.score_price: 75.}
    confidence = ""
    for score, threshold in accuracy_threshold.items():
        if float(score) >= threshold:
            confidence = float(score)
    return confidence

def analyze(ds, analysis, analysis_days):
    ds['current_prices'] = []
    ds['requested_prediction_prices'] = []
    ds['prediction_percentage'] = []
    ds['changes'] = []
    ds['requested_prediction_actions'] = []
    ds['buy_prices'] = []
    ds['sell_prices'] = []
    ds['margins'] = []
    ds['confidences'] = []

    count = 0
    for analyse in analysis: 
        current_price = float(analyse.df['Adj Close'][-1])
        requested_prediction_price = float(analysis[count].requested_prediction_price)
        prediction_percentage = (float((requested_prediction_price/current_price)*100)-100)
        risks = {'Low': [analysis_days[count].df['S1'].values[-1], analysis_days[count].df['R1'].values[-1]], 
            'Medium': [analysis_days[count].df['S2'].values[-1], analysis_days[count].df['R2'].values[-1]],   
            'High': [analysis_days[count].df['S3'].values[-1], analysis_days[count].df['R3'].values[-1]],}
        ds['buy_prices'].append(format_usd(risks[st.session_state.risk][0]))
        ds['sell_prices'].append(format_usd(risks[st.session_state.risk][1]))
        confidence = get_confidence(analyse)
        ds['confidences'].append(confidence)
        ds['current_prices'].append(format_usd(current_price))
        ds['requested_prediction_prices'].append(format_usd(requested_prediction_price))
        ds['prediction_percentage'].append(f'{float(prediction_percentage):,.2f}')
        ds['changes'].append(float(analyse.df['Adj Close'].pct_change()[-1]) * 100)
        ds['requested_prediction_actions'].append(analyse.requested_prediction_action)
        margin = ((float(risks[st.session_state.risk][1]) / float(risks[st.session_state.risk][0])*100)-100)
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
            "confidence": ds['confidences'],
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
            "current": "Current $",
            "change":  st.column_config.NumberColumn(
                    "Past",
                    format="%.2f%%"
            ),
            "prediction": "Forecast",
            "prediction_percentage": st.column_config.NumberColumn(
                "Future",
                format="%.2f%%"
            ),
            "confidence": st.column_config.NumberColumn(
                "P (*)",
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

def execute_order(limit, amount, take_profit, stop_loss):
    st.write("executed")

@st.dialog("Execute Order")
def order_dialog(ds, row):
    st.markdown(f"**Trigger Limit Orders for Coin** {ds['coins'][row]} on {exchange}.")
    st.markdown(f"**Predicted Price in {st.session_state.interval.replace(',','')} is:** ${ds['requested_prediction_prices'][row]}")

    limit_buy = st.text_input("Buy Limit Order", value=float(ds['buy_prices'][row].replace(",",""),))
    order_coin_amount = st.text_input("Amount", value=float(1))
    st.write("Total buy price: $", float(float(limit_buy) * float(order_coin_amount)))
    st.markdown(f'TP/SL')
    col1, col2 = st.columns(2)
    with col1:
        take_profit = st.text_input("TP Limit", value=float(ds['sell_prices'][row].replace(",",""),))
    with col2:
        stop_loss = st.text_input("Stop Loss Offset %", value=2.0)
    if st.button("Place Order"):
        execute_order()

@st.fragment
def get_menu_left():
    st.subheader('Coin List:')
    st.session_state.source_file = st.selectbox('', ('Short', 'Medium', 'all'), index=0)
    st.subheader('Interval:')
    st.session_state.interval = st.selectbox('', ('1 Minute', '3 Minute', '5 Minute', '15 Minute', '30 Minute', '1 Hour', '6 Hour', '12 Hour', '1 Day', '1 Week'), index = 8)
    st.subheader('Trading Volatility:')
    st.session_state.risk = st.selectbox('', ('Low', 'Medium', 'High'), index = 1)

def main(ds):
    exchange = 'Binance'
    with st.sidebar:
        get_menu_left()
        st.button('Start')

    st.title(f'AI Driven Reporting.')
    st.markdown(f'Data Sourced from {exchange}')

    equitys = get_data_source()
    analysis, analysis_days, ds['binance_urls'], ds['coins'] = compute_model(equitys, st.session_state.interval)
    ds = analyze(ds, analysis, analysis_days)

    requested_date = analysis[0].df.index[-1]
    st.write(f'**Prediction Date & Time (UTC):** {str(requested_date)}')
    st.write(f'**Time frame forecast:** {st.session_state.interval}')
    st.write(f'(*) Probability/Confidence forecast will occur')

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