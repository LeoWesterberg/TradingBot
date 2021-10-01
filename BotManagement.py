import datetime, time,pandas as pd
from Algorithms import Algorithms

from pandas.core.frame import DataFrame
from DbManagement import DbManagement
from Indicators import Indicators
from MarketAPI import MarketAPI
from Constants import Constants as const
from Test import Test

class BotManagement:

    def __init__(self, db:DbManagement, algorithms:Algorithms):
        self.market_api = MarketAPI()
        self.indicator = Indicators()
        self.db = db 
        self.algorithms = algorithms
    
    #Extracts data from database and initialize bot
    def initialize_run_bot(self):
        order_manag = self.algorithms.order_management
        active_holdings =  order_manag.active_holdings
        
        active_holdings = self.db.get_table("ACTIVE HOLDINGS")
        order_manag.previous_holdings = self.db.get_table("PREV HOLDINGS")
        for index, row  in active_holdings.iterrows():
            ticker = row.get(0,"Ticker")
            if ticker in order_manag.active_tickers:
                order_manag.active_tickers[ticker] += 1
            else:
                order_manag.active_tickers[ticker] = 1
    
    #Core part of program, which calls initialization methods and request updates
    # and state between a time interval
    def run_bot(self) -> None:
        quit = False
        while(quit != True):
            print("Backtest[press 0] | Deploy[press 1] | Quit[press 2] | Reset Bot[Press 3]")
            choise = input()
            while(choise not in ['0', '1', '2' ,'3']):
                print("Invalid option, try again!")
                choise = input()
           
            if(choise == '0'):
                test = Test(self.db, self.algorithms)
                test.backTest()

            elif(choise == '1'): 
                self.run_deploy()
                
            elif(choise == '2'):
                exit()

            elif(choise == '3'):
                self.reset_bot()



    def run_deploy(self):
        while(True):
                last_update:datetime = None        
                try:
                    self.initialize_run_bot()
                    while(True):
                        self.update_bot()                            
                        date = self.db.get_previous_row(const.TICKERS[0]).at[0,const.DATETIME]
                        if(date != last_update):
                            print("Updated at date: %s"%date)
                            last_update = date
                            for ticker in const.TICKERS:
                                date_row = self.db.get_row_at_date(date,ticker)
                                if(date_row.size != 0):
                                    self.algorithms.buy_strategy(date,False,ticker)
                                    self.algorithms.sell_strategy(date, False)
                        time.sleep(60)
                        print(".")    
                except KeyboardInterrupt:
                    self.db.reset(self.algorithms.order_management.active_holdings.drop(columns='index'), "ACTIVE HOLDINGS")
                    self.db.reset(self.algorithms.order_management.previous_holdings.drop(columns='index'), "PREV HOLDINGS")

    


    #Resets database and recalculates historical indicator values
    def reset_bot(self):
        for ticker in const.TICKERS:
            data = self.market_api.get_data(ticker)
            indicator_data_frame = pd.concat([data,self.indicator.rsi_init(data, const.RSI_PERIOD),
                                                self.indicator.ema_init(data, const.LONG_EMA),
                                                self.indicator.ema_init(data, const.SHORT_EMA),
                                                self.indicator.ema_init(data, 100),
                                                self.indicator.ema_init(data, 200),
                                                self.indicator.macd_init(data, 26, 12, 9),
                                                self.indicator.smooth_rsi_init(data, const.RSI_PERIOD, const.RSI_SMOOTH_EMA_PERIOD)], axis=1)
            self.db.reset(indicator_data_frame, ticker)
        return self


    #Update database with indicators from timeperiod of previous row in database
    #until current time
    def update_bot(self) -> None:
        for ticker in const.TICKERS:
            
            request_date = self.__get_value(const.DATETIME,ticker)
            prev_indicators:list = list(map(lambda x:self.__get_value(x, ticker),const.ACTIVE_INDICATORS))
            
            data:DataFrame = self.market_api.get_data_since(request_date, ticker).iloc[1: , :]
            if(data.size == 0):
                continue

            result:DataFrame = DataFrame()


            def __new_ema(attribute:str, data=data):
                window_size = int(attribute.split(" ")[1])
                return self.indicator.update_ema(data,window_size,prev_indicators[self.__get_indicator_index(attribute)])
            

            def __new_ema_rsi(ema_window):
                rsi = __new_rsi()
                column_name = "Ema %s(Rsi %s)"%(ema_window, const.RSI_PERIOD)
                prev_ema_rsi = prev_indicators[self.__get_indicator_index(const.RSI_SMOOTH)]
                smooth_rsi_res = self.indicator.update_ema(rsi, ema_window, prev_ema_rsi, const.RSI)
                smooth_rsi_res = smooth_rsi_res.rename(columns={"Ema %s"%ema_window:column_name})
                return smooth_rsi_res


            def __new_rsi():
                dataSet = self.db.get_last_nth_rows(150, ticker).iloc[::-1].drop(columns=['index'] + const.ACTIVE_INDICATORS).append(data)
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
                    curr_ema_long = result[const.EMA_Long]
                    curr_ema_short = result[const.EMA_Short]
                    macd_line = DataFrame(curr_ema_short.subtract(curr_ema_long),columns=["MACD"])
                    result = pd.concat([result,macd_line],axis=1)
                    
                elif(indicator == "Signal"): #Must calculate MACD line first
                    prev_signal = prev_indicators[self.__get_indicator_index(const.SIGNAL)]
                    signal = self.indicator.update_ema(result,9,prev_signal,const.MACD)
                    signal = signal.rename(columns={"Ema 9":const.SIGNAL})
                    result = pd.concat([result,signal],axis=1)
                
                elif(indicator == "MACD Diff"):
                    curr_macd = result[const.MACD]
                    curr_signal = result[const.SIGNAL]
                    macd_histo = DataFrame(curr_macd.subtract(curr_signal),columns=[const.MACD_DIFF])
                    result = pd.concat([result,macd_histo],axis=1)

                    
            data.reset_index(inplace=True)
            last_index = self.__get_value(const.INDEX,ticker)
            res = pd.concat([data.drop(columns='index'),result],axis=1)
            res.index = range(last_index+1,last_index+len(res)+1)
            self.db.append_row(res, "%s"%ticker)



    def __get_value(self,attr:str,ticker) -> DataFrame:
        return self.db.get_previous_row(ticker).at[0, attr]

    def __get_indicator_index(self, attribute:str) -> int:
        return const.ACTIVE_INDICATORS.index(attribute)



        

