from app.graph import Visualization
from app.indicator_analysis import Indications
from tensorflow.keras.models import load_model
from concurrent.futures import ThreadPoolExecutor
from time import sleep

class Auto_Helper():
    def __init__(self):
        self.exchange = 'Binance'
        self.market = 'USDT'
        self.indication = 'Predicted'
        self.intervals = ['1 Hour', '6 Hour', '12 Hour']
        self.max_threads = 12
        self.action_model = load_model("models/action_prediction_model.h5")
        self.price_model = load_model("models/price_prediction_model.h5")

    def get_candidates(self, coin_list, risk='Medium'):
        if not coin_list:
            return
        coin_results, to_be_deleted = self.get_candidate_predictions(coin_list, risk)
        for del_coin in to_be_deleted:
            del coin_results[del_coin]
        candidate_results = self.calc_candidates(coin_results)
        print (candidate_results)
        return candidate_results

    def get_confidence(self, analysis):
        accuracy_threshold = {analysis.score_action: 75., analysis.score_price: 75.}
        confidence = ""
        for score, threshold in accuracy_threshold.items():
            if float(score) >= threshold:
                confidence = float(score)
        return confidence

    def calc_candidates(self, coin_results):
        candidate_results = {}
        for coin, interval_dict in coin_results.items():
            current_price = float(interval_dict['1 Hour']['analysis'].df['Adj Close'][-1])
            future_price1 = float(interval_dict['1 Hour']['analysis'].requested_prediction_price)
            future_price6 = float(interval_dict['6 Hour']['analysis'].requested_prediction_price)
            future_price12 = float(interval_dict['12 Hour']['analysis'].requested_prediction_price)
            percentage1= float(((future_price1 / current_price) * 100) - 100)
            percentage6= float(((future_price6 / current_price) * 100) - 100)
            percentage12= float(((future_price12 / current_price) * 100) - 100)
            action1 = interval_dict['1 Hour']['analysis'].analysis.requested_prediction_action
            action6 = interval_dict['6 Hour']['analysis'].analysis.requested_prediction_action
            action12 = interval_dict['12 Hour']['analysis'].analysis.requested_prediction_action
            confidence1 = self.get_confidence(interval_dict['1 Hour']['analysis_days'])
            confidence6 = self.get_confidence(interval_dict['6 Hour']['analysis_days'])
            confidence12 = self.get_confidence(interval_dict['12 Hour']['analysis_days'])
            # find candidates
            if not 0.1 < percentage1 < percentage6 < percentage12: next
            if (action1 == 'Sell' or action6 == 'Sell' or action12=='Sell'): next
            if (confidence1 < 90.0) or (confidence6 < 90.0) or (confidence12 < 90.0): next
            candidate_results[coin] = interval_dict
        return candidate_results

    #coin_result['coin']['interval']['analysis']
    #coin_result['coin']['interval']['analysis_days']
    def get_candidate_predictions(self, coin_list, risk='Medium'):
        coin_results = {}
        to_be_deleted = []
        if not coin_list:
            return
        pool = ThreadPoolExecutor(max_workers=self.max_threads)
        threads = []
        for coin in coin_list:
            for interval in self.intervals:
                threads.append(pool.submit(self.compute_model, coin, interval))
        
        for t in threads:
            while not t.done():
                sleep(0.5)
            try:
                analysis, analysis_days, coin, interval = t.result()
                if not coin_results[coin]:
                    coin_results[coin] = []
                coin_results[coin][interval]['analysis'] = analysis
                coin_results[coin][interval]['analysis_days'] = analysis_days
            except Exception as error: 
                print("error" + str(error))
#                to_be_deleted.append(coin)
        return coin_results, to_be_deleted
    
    def compute_model(self, coin, interval):
        analysis = Visualization(self.exchange, interval, coin, self.indication, self.action_model, self.price_model, self.market)
        analysis_days = Indications(self.exchange, interval, coin, self.market)
        return analysis, analysis_days, coin, interval
