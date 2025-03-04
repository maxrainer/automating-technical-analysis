import json
from flask import Flask, jsonify, request
from app.auto_helper import Auto_Helper
from app.api_predictions import Api_Predictions
from api.binance_api import BinanceAPI

app = Flask(__name__)

#json dict apikey, apisecret
@app.route('/apikey', methods=['POST'])
def set_apikey():
    if request.method == 'POST':
        data = request.json
        binanceAPI.set_keys(data['apikey'], data['apisecret'])
        return "OK"

@app.route('/clearkey', methods=['GET'])
def clear_apikey():
    binanceAPI.clear_keys()
    return "OK"

@app.route('/endpoint', methods=['POST'])
def set_endpoint():
    if request.method == 'POST':
        data = request.json
        binanceAPI.set_endpoint(data['endpoint'])
        return "OK"

#json dict coin==list, interval
@app.route('/coin_action', methods=['POST'])
def get_coin_action():
    if request.method == 'POST':
        data = request.json
        action = ap.get_coinlist_action(data['coin'], data['interval'])
        return jsonify(action)

# json dict coin, usd
@app.route('/buy', methods=['POST'])
def get_buy():
    if request.method == 'POST':
        data = request.json
        coin = data['coin']
        symbol = coin + symbolUSD
        usd = float(data['usd'])
        order = binanceAPI.general_order(symbol, 'BUY', 'MARKET', usd)
        return jsonify(order)

# json dict coin, usd
@app.route('/sell', methods=['POST'])
def get_sell():
    if request.method == 'POST':
        data = request.json
        coin = data['coin']
        symbol = coin + symbolUSD
        usd = float(data['usd'])
        order = binanceAPI.general_order(symbol, 'SELL', 'MARKET', usd)
        return jsonify(order)

if __name__ == '__main__':  
   ap = Api_Predictions()
   binanceAPI = BinanceAPI()
   symbolUSD = 'USDC'
   app.run(host="0.0.0.0", port=5050, debug=False)  