import datetime
from pandas.core.frame import DataFrame
import yfinance as yf
from Constants import Constants as const
import pytz


class MarketAPI:
    def __init__(self):
        self.interval = '%sm'%const.TICKER_INTERVAL
        self.period='%sd'%const.TICKER_PERIOD
        self.stock = const.STOCK



    def get_data(self, stock:str) -> DataFrame:
        data = yf.download(tickers = stock, period = self.period, interval = self.interval,threads=True)
        data = self.__apply_settings(data).rename(columns = {'Date': 'Datetime'})
        now = datetime.datetime.now().astimezone(pytz.timezone('Europe/Oslo'))
        data = data[(now - data["Datetime"]).dt.total_seconds()/60 > 5]       
        return data

    def get_data_since(self, start:datetime, stock:str) -> DataFrame:
        data:DataFrame = yf.download(tickers = stock, start = start, interval = self.interval)
        if(data.size == 0):
            return DataFrame()
        data = self.__apply_settings(data).rename(columns = {'Date': 'Datetime'})
        now = datetime.datetime.now().astimezone(pytz.timezone('Europe/Oslo'))
        data = data[(now - data["Datetime"]).dt.total_seconds()/60 > 5]       
        return data



    def __apply_settings(self, data:DataFrame) -> DataFrame:
        data = data.tz_convert('Europe/Oslo',level=0)
        data.reset_index(inplace=True)
        return data

        

    
    
 


    