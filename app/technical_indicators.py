from app.data_sourcing import Data_Sourcing

class Technical_Calculations(Data_Sourcing):
    
    def __init__(self, exchange, interval, asset, market = None):  
        self.future_price = 30
        self.fast_length = 12
        self.slow_length = 26
        self.signal_smoothing = 9
        self.short_run = 20
        self.long_run = 50
        self.rsi_period = 14
        
        super().__init__(exchange)
        super(Technical_Calculations, self).intervals(interval)
        super(Technical_Calculations, self).apis(asset, market)

    def Moving_Average_Convergence_Divergence(self):
        ema1 = self.df['Adj Close'].ewm(span = self.fast_length, adjust = False).mean()
        ema2 = self.df['Adj Close'].ewm(span = self.slow_length, adjust = False).mean()

        self.df['MACD'] = ema1 - ema2
        self.df['MACDS'] = self.df['MACD'].ewm(span = self.signal_smoothing, adjust = False).mean()
        self.df['MACDH'] = self.df['MACD'] - self.df['MACDS']

    def Relative_Strength_Index(self):
        change = self.df['Adj Close'].diff(1)
        gain = change.mask(change < 0, 0)
        loss = change.mask(change > 0, 0)
        average_gain = gain.ewm(com = self.rsi_period - 1, min_periods = self.rsi_period).mean()
        average_loss = loss.ewm(com = self.rsi_period - 1, min_periods = self.rsi_period).mean()
        rs = abs(average_gain / average_loss)

        self.df['RSI'] = 100 - (100 / (1 + rs))

    def Slow_Stochastic(self):
        low_stochastic = self.df['Low'].rolling(window = self.rsi_period).min()
        high_stochastic = self.df['High'].rolling(window = self.rsi_period).max()

        fast_k = 100 * ((self.df['Adj Close'] - low_stochastic) / (high_stochastic - low_stochastic) )
        self.df['SR_K'] = fast_k.rolling(window = 3).mean()
        self.df['SR_D'] = self.df['SR_K'].rolling(window = 3).mean()

    def Moving_Averages(self):
        self.df['SMA'] = self.df['Adj Close'].rolling(self.short_run).mean()
        self.df['LMA'] = self.df['Adj Close'].rolling(self.long_run).mean()

    def Pivot_Point(self): 
        self.df['P'] = (self.df['Adj Close'] + self.df['High'] + self.df['Low']) / 3
        self.df['R1'] = (self.df['P'] * 2) - self.df['Low']
        self.df['R2'] = self.df['P'] + (self.df['High'] - self.df['Low'])
        self.df['R3'] = self.df['High'] + 2 * (self.df['P'] - self.df['Low'])
        self.df['S1'] = (self.df['P'] * 2) - self.df['High']
        self.df['S2'] =self.df['P'] - (self.df['High'] - self.df['Low'])
        self.df['S3'] = self.df['Low'] - 2 * (self.df['High'] - self.df['P'])

    def On_Balance_Volume(self):
        self.df['OBV'] = 0
        self.df.loc[((self.df['Volume'].shift(-1)) < (self.df['Volume'])), 'OBV'] = self.df['OBV'] + self.df['Volume'].shift(-1)
        self.df.loc[((self.df['Volume'].shift(-1)) > (self.df['Volume'])), 'OBV'] = self.df['OBV'] - self.df['Volume'].shift(-1)
        self.df.loc[((self.df['Volume'].shift(-1)) == (self.df['Volume'])), 'OBV'] = self.df['OBV'] + 0
        self.df['OBV'].fillna(0, inplace = True)

    def Price_Analysis(self):
        self.df['HL_PCT'] = (self.df['High'] - self.df['Low']) / self.df['Adj Close'] * 100.0
        self.df['PCT_CHG'] = (self.df['Adj Close'] - self.df['Open']) / self.df['Open'] * 100.0
        self.df['Future_Adj_Close'] = self.df['Adj Close'].shift(-self.future_price)
        self.df['Future_Adj_Close'].fillna(0, inplace = True)