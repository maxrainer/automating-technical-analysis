from api.binance_api import BinanceAPI
import time

if __name__ == '__main__':
    bi =  BinanceAPI()
    bi.POST_order_test()

