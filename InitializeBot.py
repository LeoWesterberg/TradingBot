from numpy import NaN
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
        for ticker in const.TICKERS:
            data = self.market_api.get_data(ticker)
            indicator_data_frame = pd.concat([data,self.indicator.rsi_init(data, const.RSI_PERIOD),
                                                self.indicator.ema_init(data, const.LONG_EMA),
                                                self.indicator.ema_init(data, const.SHORT_EMA),
                                                self.indicator.ema_init(data, 100),
                                                self.indicator.ema_init(data, 200),
                                                self.indicator.macd_init(data, 26, 12, 9),
                                                self.indicator.smooth_rsi_init(data, const.RSI_PERIOD, const.RSI_SMOOTH_EMA_PERIOD)], axis=1)
            self.db.reset(indicator_data_frame, "%s"%ticker)



    def update_bot(self) -> None:
        for ticker in const.TICKERS:
            
            request_date = self.__get_value(const.DATETIME)
            prev_indicators:list = list(map(lambda x:self.__get_value(x),const.ACTIVE_INDICATORS))
            
            data:DataFrame = self.market_api.get_data_since(request_date, ticker).iloc[1: , :]
            result:DataFrame = DataFrame()

            def __new_ema(attribute:str, data=data):
                window_size = int(attribute.split(" ")[1])
                return self.indicator.update_ema(data,window_size,prev_indicators[self.get_indicator_index(attribute)])
            
            def __new_ema_rsi(ema_window):
                rsi = __new_rsi()
                column_name = "Ema %s(Rsi %s)"%(ema_window, const.RSI_PERIOD)
                prev_ema_rsi = prev_indicators[self.get_indicator_index(const.RSI_SMOOTH_INDEX)]
                smooth_rsi_res = self.indicator.update_ema(rsi, ema_window, prev_ema_rsi, const.RSI_INDEX)
                smooth_rsi_res = smooth_rsi_res.rename(columns={"Ema %s"%ema_window:column_name})
                return smooth_rsi_res

            def __new_rsi():
                dataSet = self.db.get_last_nth_rows(150).iloc[::-1].drop(columns=['index'] + const.ACTIVE_INDICATORS).append(data)
                new_rsi = self.indicator.rsi_init(dataSet,const.RSI_PERIOD)[150:]
                new_rsi.reset_index(inplace=True)
                new_rsi = new_rsi.drop(columns='index')
                return new_rsi
                
                
            for indicator in const.ACTIVE_INDICATORS:
                indicator_type = indicator.split(" ")[0]

                if(indicator_type == "Ema"):

                    if(indicator.split(" ").__len__() > 2): #Temporarly hardcoded  
                        result = pd.concat([result,__new_ema_rsi(3)],axis=1)

                    else:
                        result = pd.concat([result,__new_ema(indicator)],axis=1)
                        

                elif(indicator_type == "Rsi"):
                    result = pd.concat([result,__new_rsi()],axis=1)
                
                elif(indicator == "MACD"): #Must calculate Ema indexes first
                    curr_ema_long = result[const.EMA_Long_INDEX]
                    curr_ema_short = result[const.EMA_Short_INDEX]
                    macd_line = DataFrame(curr_ema_short.subtract(curr_ema_long),columns=["MACD"])
                    result = pd.concat([result,macd_line],axis=1)
                    
                elif(indicator == "Signal"): #Must calculate MACD line first
                    prev_signal = prev_indicators[self.get_indicator_index(const.SIGNAL_INDEX)]
                    signal = self.indicator.update_ema(result,9,prev_signal,const.MACD_INDEX)
                    signal = signal.rename(columns={"Ema 9":const.SIGNAL_INDEX})
                    result = pd.concat([result,signal],axis=1)
                
                elif(indicator == "MACD Diff"):
                    curr_macd = result[const.MACD_INDEX]
                    curr_signal = result[const.SIGNAL_INDEX]
                    macd_histo = DataFrame(curr_macd.subtract(curr_signal),columns=[const.MACD_DIFF_INDEX])
                    result = pd.concat([result,macd_histo],axis=1)

                    
                
            data.reset_index(inplace=True)
            last_index = self.__get_value(const.INDEX)
            res = pd.concat([data.drop(columns='index'),result],axis=1)
            res.index = range(last_index+1,last_index+len(res)+1)
            self.db.append_row(res, "%s"%ticker)



    def __get_value(self,attr:str) -> DataFrame:
        return self.db.get_previous_row()[attr].to_list()[0]

    def get_indicator_index(self, attribute:str):
        return const.ACTIVE_INDICATORS.index(attribute)



        

