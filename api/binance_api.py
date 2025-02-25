import requests
import json
import hmac
import hashlib
import time
import base64
from urllib.parse import urlencode

class BinanceAPI():
    def __init__(self):
        self.api_key = "ttSJV6QsryMiplHGhp6eTIy1UE9nDIKGqRkGuWY5jrBbU93QMEPK7KTCpr8YsUcv"
        self.api_secret = "jAIwvZyNzhRI9WVCgI5VEjj72CUJavjkhvLvAzBzT7mTEkcvypYNacGMROXrw6Vn"
        self.url = ''
        self.payload = {}
        self.session = requests.Session()
        self.endpoint = 'https://testnet.binance.vision/'

    def url_builder(self, url):
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
    
    def general_order(self, symbol, side, type, quantity):
        self.url_builder('api/v3/order/test')
        self.session.headers.update({'X-MBX-APIKEY': self.api_key})
        self.session.headers.update({'Content-Type': 'application/json;charset=utf-8"'})
        self.payload['symbol'] = symbol
        self.payload['side']= side
        self.payload['type']= type
        self.payload['computeCommissionRates']= 'true'
        self.payload['quantity']= str(quantity)
        self.payload['timestamp']= self.get_timestamp() 
    
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
