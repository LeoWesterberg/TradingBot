from pandas.core.frame import DataFrame
from DbManagement import DbManagement
from Indicators import Indicators
from MarketAPI import MarketAPI
import pandas as pd
from Constants import Constants as const

class InitializeBot:

    def __init__(self, db:DbManagement, indicator:Indicators, market_api:MarketAPI):
        self.market_api = market_api
        self.db = db
        self.indicator = indicator
    


    def reset_bot(self) -> None:
        data = self.market_api.get_data(self.market_api.stock)
        indicator_data_frame = pd.concat([data,self.indicator.rsi_init(data, const.RSI_PERIOD),
                                               self.indicator.ema_init(data, const.LONG_EMA),
                                               self.indicator.ema_init(data, const.SHORT_EMA),
                                               self.indicator.ema_init(data, 100),
                                               self.indicator.ema_init(data, 200),
                                               self.indicator.macd_init(data, 26, 12, 9),
                                               self.indicator.smooth_rsi_init(data, const.RSI_PERIOD, const.RSI_SMOOTH_EMA_PERIOD)], axis=1)
        self.db.reset(indicator_data_frame,"Data")



# WORK TO DO ON UPDATE BOT
    def update_bot(self) -> None:
        previous_row = self.db.get_previous_row()

        prev_short_ema = self.__retrieveValue(previous_row,const.EMA_Short_INDEX)
        prev_long_ema = self.__retrieveValue(previous_row,const.EMA_Long_INDEX)
        prev_index = self.__retrieveValue(previous_row,const.INDEX)
        request_date = self.__retrieveValue(previous_row,const.DATETIME)
        data:DataFrame = self.market_api.get_data_since(request_date).iloc[1: , :]
        
        # CALCULATING NEW EMAS BASED ON PREVIOUS ONES
        newShortEma = self.indicator.update_ema(data,const.SHORT_EMA,prev_short_ema)
        newLongEma = self.indicator.update_ema(data,const.LONG_EMA,prev_long_ema)   
        dropColumns = ['index'] + const.ACTIVE_INDICATORS

        # CALCULATING NEW RSI VALUE BASED ON PREVIOUS 150(DUE TO INCREASING ACCURACY) ROWS
        newRsi:DataFrame =self.indicator.rsi_init(self.db.get_last_nth_rows(150).iloc[::-1].drop(columns=['index']+const.ACTIVE_INDICATORS).append(data),5)[150:]
        newRsi.reset_index(inplace=True)

        #CONFIGURING AND CONCATENATING RESULTS AND ADDING TO DATABASE
        data.reset_index(inplace=True)
        res = pd.concat([data.drop(columns='index'),newRsi.drop(columns='index'),prev_short_ema,prev_long_ema],axis=1)
        res.index = range(prev_index+1,prev_index+len(res)+1)
        self.db.append_row(res)



    def __retrieveValue(self,df:DataFrame,attr:str) -> DataFrame:
        return df[attr].to_list()[0]



        

