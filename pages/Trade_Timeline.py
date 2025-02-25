import streamlit as st 
import gc
from app.data_sourcing import Data_Sourcing, data_update
from app.graph import Visualization
from app.indicator_analysis import Indications
from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np
import time
from bokeh.plotting import figure

exchange = 'Binance'
market = 'USDT'
indication = 'Predicted'
intervals = ['1 Minute', '3 Minute', '5 Minute', '15 Minute', '30 Minute', '1 Hour', '6 Hour', '12 Hour', '1 Day', '1 Week']
#intervals = ['1 Hour', '6 Hour', '12 Hour', '1 Day', '1 Week']


def compute_model(equity, interval):
    analysis = Visualization(exchange, interval, equity, indication, action_model, price_model, market)
    analysis_days = Indications(exchange, interval, equity, market)
    return analysis, analysis_days

def get_data_source():
    data_source = pd.read_csv('market_data/binance_reporting_long.txt')
    equitys = data_source['Currency']
    if equitys.size == 0: 
        st.markdown("no Equity, exit now")
        exit
    return equitys

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

@st.fragment
def get_menu_left():
    st.subheader('Crypto:')
    st.session_state.equity = st.selectbox('', ds)
    st.subheader('Trading Volatility:')
    st.session_state.risk = st.selectbox('', ('Low', 'Medium', 'High'), index = 1)

def build_result_dict(analysis, analysis_days, interval, count):
    result = {}
    result['count'] = count
    result['interval'] = interval
    result['current_price'] = float(analysis.df['Adj Close'][-1])
    result['prediction_price'] = float(analysis.requested_prediction_price)
    result['prediction_percentage'] = float(((result['prediction_price']/result['current_price'])*100)-100)
    risks = {'Low': [analysis_days.df['S1'].values[-1], analysis_days.df['R1'].values[-1]], 
            'Medium': [analysis_days.df['S2'].values[-1], analysis_days.df['R2'].values[-1]],   
            'High': [analysis_days.df['S3'].values[-1], analysis_days.df['R3'].values[-1]],}
    result['buy_price']= format_usd(risks[st.session_state.risk][0])
    result['sell_price']= format_usd(risks[st.session_state.risk][1])
    result['prediction_actions'] = analysis.requested_prediction_action
    result['changes']= float((analysis.df['Adj Close'].pct_change()[-1]) * 100)
    confidence = get_confidence(analysis)
    result['confidences']= confidence
    margin = ((float(risks[st.session_state.risk][1]) / float(risks[st.session_state.risk][0])*100)-100)
    result['margins']= f'{float(margin):,.2f}'
    return result

@st.fragment
def get_dataframe(result_list):
    event = st.dataframe(
        result_list,
        hide_index=True,
        column_order=('count','interval','prediction_price',
                      'prediction_percentage','confidences','prediction_actions',
                      'buy_price','sell_price','margins'),
        column_config={
            "count": "#",
            "interval": "Interval",
            "prediction_actions": "Action",
            "prediction_price": "Forecast",
            "prediction_percentage": st.column_config.NumberColumn(
                "Change",
                format="%.2f%%"
            ),
            "confidences": st.column_config.NumberColumn(
                "P (*)",
                format="%.2f%%"
            ),
            "buy_price": "Buy Limit",
            "sell_price": "Sell Limit",
            "margins": st.column_config.NumberColumn(
                "Margin",
                format="%.2f%%"
            )
        }
    )

def get_linechart(result_list):
    forecast = []
    counts = []
    currents = []
    buy_limits = []
    sell_limits = []
    count = 1
    for r in result_list:
        forecast.append(r['prediction_price'])
        currents.append(result_list[0]['current_price'])
        sell_limits.append(r['sell_price'])
        buy_limits.append(r['buy_price'])
        counts.append(count)
        count += 1
    p = figure(width=450, height=350, title="Forecast", x_axis_label = "intervals", y_axis_label="USD")
    p.line(counts, forecast, legend_label="Prediction", line_width=4)
    p.line(counts, currents, legend_label="Current", line_color="grey", line_width=2 )
    p.line(counts, buy_limits, legend_label="Buy Limit", line_color="green", line_width=1)
    p.line(counts, sell_limits, legend_label="Sell Limit", line_color="red", line_width=1)
    
    p.legend.location = "top_left"
    p.legend.title = st.session_state.equity
    st.bokeh_chart(p)

def main(ds):
    result_list = []
    with st.sidebar:
        get_menu_left()
        st.button('Start')

    st.title(f'Trading Timeline for Coin {st.session_state.equity}')
    st.markdown(f'Data Sourced from {exchange}')

    _interval_percentage = float(1.0/len(intervals))
    progress_bar = st.progress(0, "Collection & processing data.")
    percentage_complete = float(0.0)
    count = 1
    for interval in intervals:
        percentage_complete = float(percentage_complete + _interval_percentage)
        try:
            analysis, analysis_days= compute_model(st.session_state.equity, interval)
            result_list.append(build_result_dict(analysis, analysis_days, interval, count))
        except:
            pass
        count += 1
        progress_bar.progress(percentage_complete, text=f'Interval **{interval}** done')
            
    progress_bar.empty()
    get_linechart(result_list)
    get_dataframe(result_list)


if __name__ == '__main__':
    import warnings
    import gc
    warnings.filterwarnings("ignore") 
    ds = get_data_source()
    action_model = load_model("models/action_prediction_model.h5")
    price_model = load_model("models/price_prediction_model.h5")

    gc.collect()
    main(ds)