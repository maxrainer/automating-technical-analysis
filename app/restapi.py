from flask import Flask, jsonify, request

app = Flask(__name__)
markets = ['BTC','ETH']

@app.route('/markets')
def get_markets():
    return jsonify(markets)

class Rest_API():
    def __init__(self):
        app.run(host='0.0.0.0', port=1111, debug=True)