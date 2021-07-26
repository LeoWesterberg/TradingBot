import datetime
from pandas.core.frame import DataFrame
import yfinance as yf
from Constants import Constants as const


class MarketAPI:
    def __init__(self):
        self.interval = '%sm'%const.TICKER_INTERVAL
        self.period='%sd'%const.TICKER_PERIOD
        self.stock = const.STOCK



    def get_data(self, stock:str) -> DataFrame:
        data = yf.download(tickers = stock, period = self.period, interval = self.interval)
        data = self.__apply_settings(data).rename(columns = {'Date': 'Datetime'})
        return data



    def get_data_since(self, start:datetime) -> DataFrame:
        data = yf.download(tickers = self.stock, start = start, interval = self.interval)
        data = self.__apply_settings(data).rename(columns = {'Date': 'Datetime'})
        return data



    def __apply_settings(self, data:DataFrame) -> DataFrame:
        data = data.tz_convert('Europe/Oslo',level=0)
        data.reset_index(inplace=True)
        return data

        

    
    
 


    