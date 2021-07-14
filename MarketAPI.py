from pandas.core.frame import DataFrame
import pytz
import yfinance as yf
from Constants import Constants as const



class MarketAPI:
    inverval = '2m'
    tz = pytz.timezone('Europe/Oslo')
    def __init__(self, stock = const.STOCK):
        self.interval = '5m'
        self.period='5d'
        self.stock = stock

    def getData(self,stock):
        data = yf.download(tickers=stock, period=self.period,interval=self.interval)
        data = self.applySettings(data)
        return data

    def applySettings(self,data:DataFrame):
        data = data.tz_convert('Europe/Oslo',level=0)
        data.reset_index(inplace=True)
        return data

    def getDataSince(self, start):
        data = yf.download(tickers=self.stock,start=start,interval=self.interval)
        data = self.applySettings(data).rename(columns={'Date': 'Datetime'})
        return data
        

    
    
 


    