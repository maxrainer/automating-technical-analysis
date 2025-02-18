from flask import Flask, jsonify, request

app = Flask(__name__)
markets = ['BTC','ETH']

@app.route('/markets')
def get_markets():
    return jsonify(markets)