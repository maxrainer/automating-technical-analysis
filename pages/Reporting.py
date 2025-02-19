import streamlit as st 
import gc
from app.data_sourcing import Data_Sourcing, data_update
from app.graph import Visualization
from app.indicator_analysis import Indications
from tensorflow.keras.models import load_model

gc.collect()


def main(app_data):
    exchange = 'Binance'
    market = 'USDT'
    indication = 'Predicted'
    # to be changed
    equity = 'BTC'


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
    
    current_price = f'{float(current_price):,.8f}'
    requested_prediction_price = f'{float(requested_prediction_price):,.8f}'
    buy_price = f'{float(buy_price):,.8f}'
    sell_price = f'{float(sell_price):,.8f}'

    st.markdown(f'Action: {str(analysis.requested_prediction_action)}')
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