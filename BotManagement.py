import time,pandas as pd
from Algorithms import Algorithms
from pandas.core.frame import DataFrame
from DbManagement import DbManagement
from Indicators import Indicators
from MarketAPI import MarketAPI
from Constants import Constants as const
from Settings import Settings as st
from Test import Test
import time, sys


class BotManagement:

    def __init__(self):
        self.market_api = MarketAPI()
        self.indicator = Indicators()
        self.db = DbManagement()
        self.algorithms = Algorithms(self.db)
    
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
            print("Backtest [press 0] | Deploy [press 1] | Apply settings [Press 2] | Exit [Press Ctrl + c]")
            choise = input()
            while(choise not in ['0', '1', '2' ,'3']):
                print("Invalid option, try again!")
                choise = input()
           
            if(choise == '0'):
                try:
                    test = Test(self.db, self.algorithms)
                    test.backTest()
                except KeyboardInterrupt:
                    print("Interrupted Testing")

            elif(choise == '1'): 
                self.run_deploy()
                
            elif(choise == '2'):
                self.reset_bot()




    def run_deploy(self):
        while(True):
                try:
                    self.initialize_run_bot()
                    print("Updated at date: %s"%(self.db.get_previous_row(st.TICKERS[0]).at[0,const.DATETIME]))
                    while(True):
                        update_tickers = list(filter(lambda elem: elem[1], self.update_bot().items())) 
                        if(len(update_tickers) != 0):
                            print("\nUpdated at date: %s"%(self.db.get_previous_row(update_tickers[0][0]).at[0,const.DATETIME]))
                            for ticker in update_tickers:
                                ticker = ticker[0]
                                self.algorithms.buy_strategy(ticker)
                                self.algorithms.sell_strategy()
                        
                        time.sleep(60)
                        print(".", end =" ")   
                        sys.stdout.flush()
                        
                except KeyboardInterrupt:
                    self.algorithms.order_management.active_holdings.reset_index(drop=True,inplace=False)
                    self.algorithms.order_management.previous_holdings.reset_index(drop=True,inplace=False)
                    self.db.reset(self.algorithms.order_management.active_holdings, "ACTIVE HOLDINGS")
                    self.db.reset(self.algorithms.order_management.previous_holdings.drop(columns='index'), "PREV HOLDINGS")
                    print("Interruption of deployed bot")
                    break
    


    #Resets database and recalculates historical indicator values
    def reset_bot(self):
        for ticker in st.TICKERS:
            data = self.market_api.get_data(ticker)
            indicator_data_frame = pd.concat([data,self.indicator.rsi_init(data, st.RSI_PERIOD),
                                                self.indicator.ema_init(data, st.LONG_EMA),
                                                self.indicator.ema_init(data, st.SHORT_EMA),
                                                self.indicator.ema_init(data, 100),
                                                self.indicator.ema_init(data, 200),
                                                self.indicator.macd_init(data, 26, 12, 9),
                                                self.indicator.smooth_rsi_init(data, st.RSI_PERIOD, st.RSI_SMOOTH_EMA_PERIOD)], axis=1)
            self.db.reset(indicator_data_frame, ticker)
        return self


    #Update database with indicators from timeperiod of previous row in database
    #until current time
    def update_bot(self):
        has_update = {}
        for ticker in st.TICKERS:
            
            request_date = self.db.get_last_value(const.DATETIME,ticker)
            prev_indicators:list = list(map(lambda x:self.db.get_last_value(x, ticker),const.ACTIVE_INDICATORS))
            
            data:DataFrame = self.market_api.get_data_since(request_date, ticker).iloc[1: , :]
            if(data.size == 0):
                has_update[ticker] = False
                continue
            result:DataFrame = DataFrame()
            has_update[ticker] = True


            def __update_ema(attribute:str, data=data):
                window_size = int(attribute.split(" ")[1])
                return self.indicator.update_ema(data,window_size,prev_indicators[self.get_indicator_index(attribute)])
            

            def __update_ema_rsi(ema_window):
                column_name = "Ema %s(Rsi %s)"%(ema_window, st.RSI_PERIOD)
                prev_ema_rsi = prev_indicators[self.get_indicator_index(const.RSI_SMOOTH)]
                smooth_rsi_res = self.indicator.update_ema(__update_rsi(), ema_window, prev_ema_rsi, const.RSI)
                smooth_rsi_res = smooth_rsi_res.rename(columns={"Ema %s"%ema_window:column_name})
                return smooth_rsi_res


            def __update_rsi():
                dataSet = self.db.get_last_nth_rows(150, ticker).iloc[::-1].drop(columns=['index'] + const.ACTIVE_INDICATORS).append(data)
                new_rsi = self.indicator.rsi_init(dataSet,st.RSI_PERIOD)[150:]
                new_rsi.reset_index(inplace=True)
                new_rsi = new_rsi.drop(columns='index')
                return new_rsi
                
                
            for indicator in const.ACTIVE_INDICATORS:
                indicator_type = indicator.split(" ")[0]

                if(indicator_type == "Ema"):

                    if(indicator.split(" ").__len__() > 2): #Temporarly hardcoded  
                        result = pd.concat([result,__update_ema_rsi(3)],axis=1)

                    else:
                        result = pd.concat([result,__update_ema(indicator)],axis=1)
                        
                elif(indicator_type == "Rsi"):
                    result = pd.concat([result,__update_rsi()],axis=1)
                
                elif(indicator == "MACD"): #Must calculate Ema indexes first
                    curr_ema_long = result[const.EMA_Long]
                    curr_ema_short = result[const.EMA_Short]
                    macd_line = DataFrame(curr_ema_short.subtract(curr_ema_long),columns=["MACD"])
                    result = pd.concat([result,macd_line],axis=1)
                    
                elif(indicator == "Signal"): #Must calculate MACD line first
                    prev_signal = prev_indicators[self.get_indicator_index(const.SIGNAL)]
                    signal = self.indicator.update_ema(result,9,prev_signal,const.MACD)
                    signal = signal.rename(columns={"Ema 9":const.SIGNAL})
                    result = pd.concat([result,signal],axis=1)
                
                elif(indicator == "MACD Diff"):
                    curr_macd = result[const.MACD]
                    curr_signal = result[const.SIGNAL]
                    macd_histo = DataFrame(curr_macd.subtract(curr_signal),columns=[const.MACD_DIFF])
                    result = pd.concat([result,macd_histo],axis=1)

                    
            data.reset_index(inplace=True)
            last_index = self.db.get_last_value(const.INDEX,ticker)
            res = pd.concat([data.drop(columns='index'),result],axis=1)
            res.index = range(last_index+1,last_index+len(res)+1)
            self.db.append_row(res, "%s"%ticker)
        return has_update
    
    def get_indicator_index(self, attribute:str) -> int:
        return const.ACTIVE_INDICATORS.index(attribute)
