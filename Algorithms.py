import datetime
from Constants import Constants as const
from Settings import Settings as st
from DbManagement import DbManagement
from OrderManagement import OrderManagement



class Algorithms:
    def __init__(self, db:DbManagement):
        self.db = db 
        self.order_management = OrderManagement(db)

    #Calculates if one attribute is over another for a specific date and ticker
    def __attr1_over_attr2(self, attrOver, attrUnder, dt, ticker):   
        current_attr_over = self.db.retrieve_value_dt(dt,attrOver, ticker)
        current_attr_under = self.db.retrieve_value_dt(dt,attrUnder, ticker)
        
        return current_attr_over > current_attr_under


    def __macd_crossover(self, dt, ticker):
        previous_date = self.db.get_prev_date(dt, ticker)
        prev_macd_stat = self.__attr1_over_attr2(const.MACD,const.SIGNAL,previous_date, ticker)
        current_macd_stat = self.__attr1_over_attr2(const.MACD,const.SIGNAL,dt, ticker) 
        
        return current_macd_stat and not prev_macd_stat

    def __signal_crossover(self, dt, ticker):
        previous_date = self.db.get_prev_date(dt, ticker)
        prev_macd_stat = self.__attr1_over_attr2(const.SIGNAL, const.MACD, previous_date, ticker)
        current_macd_stat = self.__attr1_over_attr2(const.SIGNAL,const.MACD, dt, ticker)    
        return current_macd_stat and not prev_macd_stat

    def __rsi_over_limit(self, dt, ticker):
        above_threshold = False
        current_date = dt
        for i in range(0, 10):
            current_date = self.db.get_prev_date(current_date, ticker) 
            if(self.db.retrieve_value_dt(current_date, const.EMA_RSI, ticker) > st.RSI_UPPER_BOUND):
                above_threshold = True

        return above_threshold


    def __rsi_under_limit(self, dt, ticker):
        below_threshold = False
        current_date = dt
        for i in range(0, 10):
            current_date = self.db.get_prev_date(current_date, ticker)
            if(self.db.retrieve_value_dt(current_date , const.EMA_RSI, ticker) < st.RSI_LOWER_BOUND):
                below_threshold = True
        return below_threshold

    #Checks if the MACD line is under the Zero line
    def __macd_under_zero_line(self,dt, ticker):
        return self.db.retrieve_value_dt(dt,const.MACD, ticker) < 0


    #Returns true if buy signal is found for specific date, else False
    def buy_signal(self, dt:datetime, ticker:str):
        #trend_condition = self.__attr1_over_attr2(const.CLOSE,const.EMA_200,dt, ticker)
        macd_cross_over = self.__macd_crossover(dt, ticker)    
        under_zero_line = self.__macd_under_zero_line(self.db.get_prev_date(dt, ticker),ticker)    
        return macd_cross_over and under_zero_line and self.__rsi_under_limit(dt, ticker)

    #Returns true if sell signal is found for specific date, else False
    def sell_signal(self, ticker:str, dt:datetime): 
        #trend_condition = self.__attr1_over_attr2(const.CLOSE,const.EMA_200,dt, ticker)
        signal_cross_over = self.__signal_crossover(dt,ticker)
        over_zero_line = not self.__macd_under_zero_line(self.db.get_prev_date(dt, ticker),ticker)
        return  signal_cross_over and over_zero_line and self.__rsi_over_limit(dt,ticker) 


    #Buying strategy for algorithm
    def buy_strategy(self, ticker = "Data"):
        previous_row = self.db.get_previous_row(ticker)
        limit_holdings = self.order_management.active_tickers[ticker] < st.TICKER_MAX_HOLDINGS
        buy_signal = self.buy_signal(previous_row[const.DATETIME].tolist()[0],ticker)
        if(buy_signal and limit_holdings):
            self.order_management.buy_order(ticker)



    #Sell strategy for algorithm
    def sell_strategy(self):
        for index, row in self.order_management.active_holdings.iterrows():
            ticker = row.get(0,"Ticker")
            if(self.db.get_previous_row(ticker).size != 0):
                if(self.sell_signal(ticker)):
                    self.order_management.sell_order(row["Order id"])
                    

                
            
            


    

    

