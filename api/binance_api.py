import requests
import json
import hmac
import hashlib
import time
import base64
import yaml
import math
from urllib.parse import urlencode

# default endpoint
# testing 'https://testnet.binance.vision/'
# real trading endpoint: https://api.binance.com/

class BinanceAPI():
    def __init__(self):
        self.api_key = ""
        self.api_secret = ""
        self.url = ''
        self.payload = {}
        self.session = requests.Session()
        self.endpoint = 'https://testnet.binance.vision/'
    
    def __init__(self, endpoint='', api_key='', api_secret=''):
        self.api_key = api_key
        self.endpoint = endpoint
        self. api_secret = api_secret
        self.payload = {}
        self.session = requests.Session()
        self.url = ''

    def set_keys(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
    
    def set_endpoint(self, endpoint):
        self.endpoint = endpoint
    
    def clear_keys(self):
        self.api_key = ""
        self.api_secret = ""

    def url_builder(self, url):
        self.payload = {}
        self.url = self.endpoint + url
    
    def get_timestamp(self):
        return int(time.time() * 1000)
    
    def hashing(self, query_string):
        signature = hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        return signature
    
    def get_signature(self, payload):
        query_string = urlencode(payload, True)
        signature = self.hashing(query_string)
        return signature
        
    def GET_hello(self):
        self.url_builder("api/v3/ping")
        response = requests.get(self.url)
        print(response)

    def GET_account_info(self):
        self.url_builder('api/v3/account')
        self.session.headers.update({'X-MBX-APIKEY': self.api_key})
        self.session.headers.update({'Content-Type': 'application/json'})
        self.payload['recvWindow']= '5000'
        self.payload['timestamp'] = self.get_timestamp()
        self.payload['signature'] = self.get_signature(self.payload)
        response = self.session.get(self.url, params=self.payload)
        print(response.content)
    
    def general_order(self, symbol, side, type, usd=0, qty=0):
        self.url_builder('api/v3/order')
        self.session.headers.update({'X-MBX-APIKEY': self.api_key})
        self.session.headers.update({'Content-Type': 'application/json;charset=utf-8"'})
        self.payload['symbol'] = symbol
        self.payload['side']= side
        self.payload['type']= type
        if usd != 0: 
            self.payload['quoteOrderQty']= str(usd)
        elif qty != 0:
            self.payload['quantity']= str(qty)
        self.payload['timestamp']= self.get_timestamp() 
        self.payload['signature'] = self.get_signature(self.payload)
        response = self.session.post(self.url, params=self.payload)
        return response.json()
    
    def GET_current_price(self, symbol):
        self.url_builder('api/v3/ticker/price')
        self.session.headers.update({'Content-Type': 'application/json;charset=utf-8"'})
        self.payload['symbol'] = symbol
        print(symbol)
        response = self.session.get(self.url, params=self.payload)
        print (response.json())
        data = response.json()
        return data['price']

    def getAccountInfo(self):
        self.url_builder('api/v3/account')
        self.session.headers.update({'Content-Type': 'application/json;charset=utf-8"'})
        self.session.headers.update({'X-MBX-APIKEY': self.api_key})
        self.session.headers.update({'Content-Type': 'application/json;charset=utf-8"'})
        self.payload['timestamp']= self.get_timestamp() 
        self.payload['signature'] = self.get_signature(self.payload)
        response = self.session.get(self.url, params=self.payload)
        data = response.json()
        return data
    
    def sign_request(self):
        if self.payload:
            signature = self.get_signature(self.payload)
            self.payload['signature']= signature
 
    def POST_order_test(self):
        self.general_order('BNBUSDC', 'sell', 'market', 5)     
        self.sign_request()
        response = self.session.post(self.url, params=self.payload)
        print(response.json())
        return response

    def LIMIT_order(self, symbol, side, quantity):
        self.general_order(symbol, side, 'LIMIT', quantity)
        self.payload['TimeInForce']= 'GTC'
        self.payload['stoploa']

    def getSellQty(self, qty, coin):
        if qty == 0:
            return 0
        coin_lot_size = self.getExchangeInfo(coin)
        if qty < coin_lot_size['minQty']: 
            return 0
        result_qty = self.truncate(qty, coin_lot_size['dec'])
        return result_qty

    def getExchangeInfo(self, coin):
        with open("api/exchangeInfo.yml", 'r') as stream:
            try:
                exchange_info = yaml.safe_load(stream)
                coin_lot_size = exchange_info['lot_size'][coin]
                return coin_lot_size
            except yaml.YAMLError as exc:
                print(exc)
    
    def truncate(self, f, n):
        return math.floor(f * 10 ** n) / 10 ** n