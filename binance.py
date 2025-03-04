from api.binance_api import BinanceAPI
from app.auto_helper import Auto_Helper
import time

if __name__ == '__main__':
    coin_list = ['BTC', 'SOL']
    ah = Auto_Helper()
    ah.get_candidates(coin_list, risk='Medium')
    # bi =  BinanceAPI()
    # bi.POST_order_test()

