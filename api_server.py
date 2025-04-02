#import json
from flask import Flask, jsonify, request, abort
#from app.auto_helper import Auto_Helper
from app.api_predictions import Api_Predictions
from api.binance_api import BinanceAPI

app = Flask(__name__)

# #json dict apikey, apisecret
# @app.route('/apikey', methods=['POST'])
# def set_apikey():
#     if request.method == 'POST':
#         data = request.json
#         binanceAPI.set_keys(data['apikey'], data['apisecret'])
#         return "OK"

# @app.route('/clearkey', methods=['GET'])
# def clear_apikey():
#     binanceAPI.clear_keys()
#     return "OK"

# @app.route('/endpoint', methods=['POST'])
# def set_endpoint():
#     if request.method == 'POST':
#         data = request.json
#         binanceAPI.set_endpoint(data['endpoint'])
#         return "OK"

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
        url = data['url']
        api_key = data['apikey']
        api_secret = data['apisecret']
        bAPI = BinanceAPI(endpoint=url, api_key=api_key, api_secret=api_secret)
        symbol = coin + symbolUSD
        usd = float(data['usd'])
        order = bAPI.general_order(symbol, 'BUY', 'MARKET', usd)
        return jsonify(order)

@app.route('/price', methods=['POST'])
def get_price():
    if request.method == 'POST':
        data = request.json
        coin = data['coin']
        url = data['url']
        bAPI = BinanceAPI(endpoint=url)
        symbol = coin + symbolUSD
        price = bAPI.GET_current_price(symbol)
        return jsonify(price)

# json dict coin, usd
# sells a specific coin amount in usd
@app.route('/sell', methods=['POST'])
def get_sell():
    if request.method == 'POST':
        data = request.json
        coin = data['coin']
        url = data['url']
        api_key = data['apikey']
        api_secret = data['apisecret']
        symbol = coin + symbolUSD
        usd = float(data['usd'])
        bAPI = BinanceAPI(endpoint=url, api_key=api_key, api_secret=api_secret)
        order = bAPI.general_order(symbol, 'SELL', 'MARKET', usd=usd)
        return jsonify(order)

@app.route('/sellall', methods=['POST'])
def get_sellall():
    if request.method == 'POST':
        data = request.json
        coin = data['coin']
        url = data['url']
        api_key = data['apikey']
        api_secret = data['apisecret']
        symbol = coin + symbolUSD
        bAPI = BinanceAPI(endpoint=url, api_key=api_key, api_secret=api_secret)
        accountInfo = bAPI.getAccountInfo()
        balances = accountInfo['balances']
        asset = next(item for item in balances if item["asset"] == coin)
        qty = float(asset['free'])
        qty_sell = bAPI.getSellQty(qty, coin)
        if qty_sell > 0:
            order = bAPI.general_order(symbol, 'SELL', 'MARKET', qty=qty_sell)
            return jsonify(order)
        return ("empty")

if __name__ == '__main__':  
   ap = Api_Predictions()
#    binanceAPI = BinanceAPI()
   symbolUSD = 'USDC'
   app.run(host="0.0.0.0", port=5050, debug=False)  