import datetime, pytz, yfinance as yf

from pandas.core.frame import DataFrame
from Constants import Constants as const



class MarketAPI:
    def __init__(self):
        self.interval = '%sm'%const.TICKER_INTERVAL
        self.period='%sd'%const.TICKER_PERIOD



    def get_data(self, ticker:str) -> DataFrame:
        data = yf.download(tickers = ticker, period = self.period, interval = self.interval,threads=True, progress=False, show_errors= False)
        data = self.__apply_settings(data).rename(columns = {'Date': 'Datetime'})
        now = datetime.datetime.now().astimezone(pytz.timezone('Europe/Oslo'))
        data = data[(now - data[const.DATETIME]).dt.total_seconds()/60 > const.TICKER_INTERVAL]       
        return data



    def get_data_since(self, start:datetime, ticker:str) -> DataFrame:
        data:DataFrame = yf.download(tickers = ticker, start = start, interval = self.interval, progress=False, show_errors= False)

        if(data.size == 0):
            return DataFrame()

        data = self.__apply_settings(data).rename(columns = {'Date': 'Datetime'})
        now = datetime.datetime.now().astimezone(pytz.timezone('Europe/Oslo'))
        data = data[(now - data[const.DATETIME]).dt.total_seconds()/60 > const.TICKER_INTERVAL]       
        return data



    def __apply_settings(self, data:DataFrame) -> DataFrame:
        data = data.tz_convert('Europe/Oslo',level=0)
        data.reset_index(inplace=True)
        return data

        

    
    
 


    