import streamlit as st 
import gc
from app.data_sourcing import Data_Sourcing, data_update
from tensorflow.keras.models import load_model

gc.collect()


def main(app_data):
    st.sidebar.subheader('Interval:')
    interval = st.sidebar.selectbox('', ('1 Minute', '3 Minute', '5 Minute', '15 Minute', '30 Minute', '1 Hour', '6 Hour', '12 Hour', '1 Day', '1 Week'), index = 8)
    

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