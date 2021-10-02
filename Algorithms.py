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


    def __macd_under_signal_line(self,dt, ticker):
        return self.db.retrieve_value_dt(dt,const.MACD, ticker) < self.db.retrieve_value_dt(dt,const.SIGNAL, ticker)


    #Returns true if buy signal is found for specific date, else False
    def buy_signal(self, dt:datetime, ticker:str):
        trend_condition = self.__attr1_over_attr2(const.CLOSE,const.EMA_200,dt, ticker)
        macd_condition = self.__macd_under_signal_line(dt, ticker)
        #macd_condition = self.__macd_crossover(dt, ticker) and self.__macd_under_zero_line(dt, ticker)
        
        return trend_condition and macd_condition # and local_trend_condition):


    #Returns true if sell signal is found for specific date, else False
    def sell_signal(self, ticker:str, dt:datetime): 
        macd_condition = self.__macd_under_signal_line(dt, ticker)
        trend_condition = self.__attr1_over_attr2(const.CLOSE,const.EMA_200,dt, ticker)
        return  not macd_condition or not trend_condition


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
                    

                
            
            


            


    

    

