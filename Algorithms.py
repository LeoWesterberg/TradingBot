import datetime
from pandas.core.frame import DataFrame
from scipy.signal import find_peaks

from DbManagement import DbManagement
from Constants import Constants as const
from OrderManagement import OrderManagement



class Algorithms:
    
    def __init__(self, db:DbManagement):
        self.db = db 
        self.order_management:OrderManagement = OrderManagement()


    def __retrieve_value(self, df:DataFrame, attr:str):
        return df[attr].to_list()[0]



    def __retrieve_value_dt(self, dt, attr:str, ticker):
        return self.db.get_row_at_date(dt, ticker)[attr].to_list()[0]



    def __attr1_over_attr2(self, attrOver, attrUnder, dt, ticker):    
        current_attr_over = self.__retrieve_value_dt(dt,attrOver, ticker)
        current_attr_under = self.__retrieve_value_dt(dt,attrUnder, ticker)
        
        return current_attr_over > current_attr_under



    def __macd_crossover(self, dt, ticker):
        previous_date = self.__get_previous_date(dt, ticker)
        prev_macd_stat = self.__attr1_over_attr2(const.MACD_INDEX,const.SIGNAL_INDEX,previous_date, ticker)
        current_macd_stat = self.__attr1_over_attr2(const.MACD_INDEX,const.SIGNAL_INDEX,dt, ticker) 
        
        return current_macd_stat and not prev_macd_stat


    
    def __signal_crossover(self, dt):
        previous_date = self.__get_previous_date(dt)
        prev_macd_stat = self.__attr1_over_attr2(const.SIGNAL_INDEX,const.MACD_INDEX,previous_date)
        current_macd_stat = self.__attr1_over_attr2(const.SIGNAL_INDEX,const.MACD_INDEX,dt) 
        
        return current_macd_stat and not prev_macd_stat
    


    def __attr_secant(self,dt,attr,window, ticker):
        prev_date = self.__get_previous_date(dt)

        for i in range(1,window):
            prev_date = self.__get_previous_date(prev_date)

        return self.__retrieve_value_dt(dt,attr, ticker) - self.__retrieve_value_dt(prev_date,attr, ticker)



    def __macd_under_zero_line(self,dt, ticker):
        return self.__retrieve_value_dt(dt,const.MACD_INDEX, ticker) < 0



    def __get_previous_date(self,dt, ticker):
        previousIndex = self.__retrieve_value_dt(dt,const.INDEX, ticker)  - 1     
        
        return self.__retrieve_value(self.db.get_row_at_index(previousIndex,ticker),const.DATETIME)



    def __short_long_ema_cross(self,dt:datetime, ticker): #check
        previous_date = self.__get_previous_date(dt, ticker)
        curr_ema_stat = self.__attr1_over_attr2(const.EMA_Short_INDEX,const.EMA_Long_INDEX,dt, ticker)
        prev_ema_stat = self.__attr1_over_attr2(const.EMA_Short_INDEX,const.EMA_Long_INDEX,previous_date, ticker)
        
        return curr_ema_stat and not prev_ema_stat



    def __all_pullback_indicies(self, ticker):
        data = self.db.get_table(ticker)
        smooth_closings = data[const.EMA_Short_INDEX].values
        last_closing = self.__retrieve_value(self.db.get_previous_row(ticker),const.CLOSE_INDEX)
        return find_peaks(-smooth_closings,distance=5,prominence= last_closing * 0.001)[0]
    


    def __recent_pullback_value(self,dt,search_range, ticker):
        data = self.db.get_row_at_date(dt, ticker)

        for i in range(search_range):
            dt = self.__get_previous_date(dt,ticker)
            data = data.append(self.db.get_row_at_date(dt,ticker))

        data = data.iloc[::-1]  
        smooth_closings = data[const.CLOSE_INDEX].values
        dt_closing = self.__retrieve_value(self.db.get_row_at_date(dt, ticker),const.CLOSE_INDEX)
        nearby_peaks = find_peaks(-smooth_closings, distance=10, prominence= dt_closing * 0.001)[0]
       
        return -1 if len(nearby_peaks) == 0 else ([data[const.CLOSE_INDEX].to_list()[i] for i in nearby_peaks][-1])



    def __initialize_sell_order(self, order_id) -> None:
        self.order_management.sell_order(order_id)
        


    def __initialize_buy_order(self, dt, current_close:float, ticker) -> None:
        stop_loss = self.__retrieve_value_dt(dt,const.EMA_200_INDEX, ticker) #if (stop_loss == -1 or stop_loss < current_close) else stop_loss  
        risk = current_close - stop_loss
        take_profit = current_close + risk * const.RR_RATIO
        self.order_management.buy_order(stop_loss, take_profit,ticker)



    def __buy_signal(self, dt, ticker):
        gen_trend_condition = self.__attr1_over_attr2(const.EMA_Short_INDEX,const.EMA_200_INDEX,dt, ticker)
        macd_condition = self.__macd_crossover(dt, ticker) and self.__macd_under_zero_line(dt, ticker)
        
        return gen_trend_condition and macd_condition # and local_trend_condition):



    def __sell_signal(self,stop_loss,take_profit, current_close): 
        return current_close >= take_profit or current_close <= stop_loss #or dt.hour == 21 and dt.minute == 60-const.TICKER_INTERVAL



    def buy_strategy(self, dt, ticker = "Data"):
        current_close = self.__retrieve_value_dt(dt,const.CLOSE_INDEX,ticker)

        if(self.__buy_signal(dt, ticker)):
            self.__initialize_buy_order(dt,current_close, ticker)
            print("%s: Buying at time %s"%(ticker,dt))



    def sell_strategy(self,dt):
        for index, row in self.order_management.current_holdings.iterrows():
            stock = row.get(0,"ticker")
            if(self.db.get_row_at_date(dt, stock).size != 0):
                current_close = self.__retrieve_value_dt(dt,const.CLOSE_INDEX, stock)
                if(self.__sell_signal(row["Stop loss"],row["Profit take"], current_close)):
                    self.__initialize_sell_order(row["Order id"])
                    if(row["Profit take"] < current_close):
                        print("%s: Selling at time %s with profit %s"%(stock,dt,current_close - row["Profit take"]))
                    else:
                        print("%s: Selling at time %s with loss %s"%(stock,dt,row["Stop loss"] - current_close))
                        
                    

                
            
            


            


    

    

