from tensorflow.keras.models import load_model
from app.graph import Visualization
from app.indicator_analysis import Indications

class Api_Predictions():
    def __init__(self):
        self.exchange = 'Binance'
        self.market = 'USDT'
        self.indication = 'Predicted'
        self.inverval = '30 Minute'
        self.coin = 'BTC'
        self.action_model = load_model("models/action_prediction_model.h5")
        self.price_model = load_model("models/price_prediction_model.h5")

    def get_single_action(self, coin, interval):
        analysis = self.compute_analysis(coin, interval)
        return analysis.requested_prediction_action
    
    def get_coinlist_action(self, coin_list, interval):
        result = {}
        for coin in coin_list:       
            action = self.get_single_action(coin, interval)
            result[coin] = action
        return result

    def compute_analysis(self, coin, interval):
        analysis = Visualization(self.exchange, interval, coin, self.indication, self.action_model, self.price_model, self.market)
        return analysis