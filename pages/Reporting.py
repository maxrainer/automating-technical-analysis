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
    exchange = 'Binance'
    market = 'USDT'
    indication = 'Predicted'
    # to be changed
    equity = 'BTC'
    risk='Medium'

    st.sidebar.subheader('Interval:')
    interval = st.sidebar.selectbox('', ('1 Minute', '3 Minute', '5 Minute', '15 Minute', '30 Minute', '1 Hour', '6 Hour', '12 Hour', '1 Day', '1 Week'), index = 8)


    analysis = Visualization(exchange, interval, equity, indication, action_model, price_model, market)
    analysis_day = Indications(exchange, '1 Day', equity, market)

    requested_date = analysis.df.index[-1]
    current_price = float(analysis.df['Adj Close'][-1])
    change = float(analysis.df['Adj Close'].pct_change()[-1]) * 100
    requested_prediction_price = float(analysis.requested_prediction_price)
    requested_prediction_action = analysis.requested_prediction_action
    risks = {'Low': [analysis_day.df['S1'].values[-1], analysis_day.df['R1'].values[-1]], 
            'Medium': [analysis_day.df['S2'].values[-1], analysis_day.df['R2'].values[-1]],   
            'High': [analysis_day.df['S3'].values[-1], analysis_day.df['R3'].values[-1]],}

    buy_price = float(risks[risk][0])
    sell_price = float(risks[risk][1])

    # st.markdown(buy_price)

    current_price = f'{float(current_price):,.8f}'
    requested_prediction_price = f'{float(requested_prediction_price):,.8f}'
    buy_price = f'{float(buy_price):,.8f}'
    sell_price = f'{float(sell_price):,.8f}'

    df1 = pd.DataFrame(
        {
            "Coin": [equity],
            "Predicted Action": [str(analysis.requested_prediction_action)],
            "Current Price": [current_price],
            "Prediction Price": [requested_prediction_price],
            "Buy Price": [buy_price],
            "Sell Price": [sell_price]
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