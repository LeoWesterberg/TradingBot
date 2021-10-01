import datetime
from pandas.core.frame import DataFrame
from scipy.signal import find_peaks

from Constants import Constants as const
from DbManagement import DbManagement
from OrderManagement import OrderManagement



class Algorithms:
    def __init__(self, db:DbManagement):
        self.db = db 
        self.order_management = OrderManagement(db)

    
    #Retrieves the first value from a dataframe given its column name
    def __retrieve_value(self, df:DataFrame, attr:str):
        return df[attr].to_list()[0]


    #Retrieves value from database given a certain date and attribute name
    def __retrieve_value_dt(self, dt, attr:str, ticker):
        return self.db.get_row_at_date(dt, ticker)[attr].to_list()[0]


    #Calculates if one attribute is over another for a specific date and ticker
    def __attr1_over_attr2(self, attrOver, attrUnder, dt, ticker):    
        current_attr_over = self.__retrieve_value_dt(dt,attrOver, ticker)
        current_attr_under = self.__retrieve_value_dt(dt,attrUnder, ticker)
        
        return current_attr_over > current_attr_under


    #Calculates if a macd crossover has occured for a specific date and ticker
    def __macd_crossover(self, dt, ticker):
        previous_date = self.__get_previous_date(dt, ticker)
        prev_macd_stat = self.__attr1_over_attr2(const.MACD,const.SIGNAL,previous_date, ticker)
        current_macd_stat = self.__attr1_over_attr2(const.MACD,const.SIGNAL,dt, ticker) 
        
        return current_macd_stat and not prev_macd_stat


    #Calculates if there has been a signal crossover for a specific date and ticker. Not
    #used in the current algorithm, but stays for future use.
    def __signal_crossover(self, dt):
        previous_date = self.__get_previous_date(dt)
        prev_macd_stat = self.__attr1_over_attr2(const.SIGNAL,const.MACD,previous_date)
        current_macd_stat = self.__attr1_over_attr2(const.SIGNAL,const.MACD,dt) 
        
        return current_macd_stat and not prev_macd_stat
    

    #Calculates the inclination of the secant, with specified window size for a 
    # specific attribute, date and ticker
    def __attr_secant(self,dt,attr,window, ticker):
        prev_date = self.__get_previous_date(dt)

        for i in range(1,window):
            prev_date = self.__get_previous_date(prev_date)

        return self.__retrieve_value_dt(dt,attr, ticker) - self.__retrieve_value_dt(prev_date,attr, ticker)


    #Checks if the MACD line is under the Zero line
    def __macd_under_zero_line(self,dt, ticker):
        return self.__retrieve_value_dt(dt,const.MACD, ticker) < 0

    def __macd_under_signal_line(self,dt, ticker):
        return self.__retrieve_value_dt(dt,const.MACD, ticker) < self.__retrieve_value_dt(dt,const.SIGNAL, ticker)


    #Returns the value from dataframe for the previous date given the a date.
    def __get_previous_date(self,dt, ticker):
        previousIndex = self.__retrieve_value_dt(dt,const.INDEX, ticker)  - 1     

        return self.__retrieve_value(self.db.get_row_at_index(previousIndex,ticker),const.DATETIME)


    #Checks if shorter EMA value crosses the Longer EMA value. Is not used in the current active
    #algorithm. For future development of algorithm
    def __short_long_ema_cross(self,dt:datetime, ticker): #check
        previous_date = self.__get_previous_date(dt, ticker)
        curr_ema_stat = self.__attr1_over_attr2(const.EMA_Short,const.EMA_Long,dt, ticker)
        prev_ema_stat = self.__attr1_over_attr2(const.EMA_Short,const.EMA_Long,previous_date, ticker)
        
        return curr_ema_stat and not prev_ema_stat


    #Calculates all the pullback indicies.  Is used in future development in the algorithm
    #trying to set the stoploss at nearest pullback value
    def all_pullback_indicies(self, ticker):
        data = self.db.get_table(ticker)
        smooth_closings = data[const.CLOSE].values
        return find_peaks(-smooth_closings,distance=10,width=4)[0]
    

    #Returns pullback at a specific date
    def __pullback_value_dt(self,dt,search_range, ticker):
        data = self.db.get_row_at_date(dt, ticker)

        for i in range(search_range):
            dt = self.__get_previous_date(dt,ticker)
            data = data.append(self.db.get_row_at_date(dt,ticker))

        data = data.iloc[::-1]  
        smooth_closings = data[const.CLOSE].values
        dt_closing = self.__retrieve_value(self.db.get_row_at_date(dt, ticker),const.CLOSE)
        nearby_peaks = find_peaks(-smooth_closings, distance=10, prominence= dt_closing * 0.001)[0]
       
        return -1 if len(nearby_peaks) == 0 else ([data[const.CLOSE].to_list()[i] for i in nearby_peaks][-1])

        


    #Initializer for sell order setup and delegates it to the order_management object
    def __initialize_sell_order(self, order_id, test_mode,dt) -> None:
        if(not test_mode): 
            self.order_management.sell_order(order_id,test_mode)
        else:
            self.order_management.sell_order(order_id,test_mode, dt)

        

    #Calculates stoploss, risk and the takeprofit value and
    # initializes the buy order, delegating it to the order_management object
    def __initialize_buy_order(self, dt, current_close:float, ticker, test_mode) -> None:
        stop_loss = self.__retrieve_value_dt(dt,const.EMA_200, ticker)  #if (stop_loss == -1 or stop_loss < current_close) else stop_loss  
        risk = abs(current_close - stop_loss)
        take_profit = current_close + risk * const.RR_RATIO
        print("%s: \t Time =  %s \t Buy = %s"%(ticker, dt, "{:.12f}".format(current_close)))
        if(not test_mode): 
            self.order_management.buy_order(stop_loss, take_profit, ticker, test_mode)
        else:
            self.order_management.buy_order(stop_loss, take_profit, ticker, test_mode, dt)



    #Returns true if buy signal is found for specific date, else False
    def __buy_signal(self, dt:datetime, ticker:str):
        gen_trend_condition = self.__attr1_over_attr2(const.CLOSE,const.EMA_200,dt, ticker)
        macd_condition2 = self.__macd_under_signal_line(dt, ticker)
        #macd_condition = self.__macd_crossover(dt, ticker) and self.__macd_under_zero_line(dt, ticker)
        
        return gen_trend_condition and macd_condition2 # and local_trend_condition):


    #Returns true if sell signal is found for specific date, else False
    def __sell_signal(self, ticker:str, dt:datetime): 
         
        return  not self.__macd_under_signal_line(dt, ticker)


    #Buying strategy for algorithm
    def buy_strategy(self, dt, test_mode, ticker = "Data"):
        current_close = self.__retrieve_value_dt(dt,const.CLOSE,ticker)

        if(self.__buy_signal(dt, ticker) and self.order_management.active_tickers[ticker] < const.TICKER_MAX_HOLDINGS):
            self.__initialize_buy_order(dt,current_close, ticker, test_mode)


    #Sell strategy for algorithm
    def sell_strategy(self,dt, test_mode):
        for index, row in self.order_management.active_holdings.iterrows(): #
            ticker = row.get(0,"Ticker")

            if(self.db.get_row_at_date(dt, ticker).size != 0):
                current_close = self.__retrieve_value_dt(dt,const.CLOSE, ticker)

                if(self.__sell_signal(ticker, dt)): #self.__sell_signal(row["Stop loss"],row["Profit take"], current_close, dt)):
                    self.__initialize_sell_order(row["Order id"],test_mode,dt)
                    print("%s: \t Time = %s \t Sell = %s  \t diff = %s \t diff(%%): %s"%(ticker,dt,"{:.13f}".format(current_close),"{:.13f}".format(current_close - row["Buy"]),"{:.13f}".format(100*current_close/row["Buy"] - 100)))
                    

                
            
            


            


    

    

