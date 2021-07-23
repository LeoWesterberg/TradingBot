from numpy import double, empty
from pandas.core.frame import DataFrame
from DbManagement import DbManagement
from Constants import Constants as const
import datetime
from Order import Order
from scipy.signal import find_peaks



class NewAlgorithms:
    current_orders = []  
    profit = 0
    past_orders = []


    def __init__(self, db:DbManagement):
        self.db = db 


    def retrieveValue(self, df:DataFrame, attr:str):
        return df[attr].to_list()[0]

    def retrieve_value_dt(self, dt, attr:str):
        return self.db.getRowAD(dt)[attr].to_list()[0]


    def attr1_over_attr2(self, attrOver, attrUnder, dt):    
        current_attr_over = self.retrieve_value_dt(dt,attrOver)
        current_attr_under = self.retrieve_value_dt(dt,attrUnder)
        
        return current_attr_over > current_attr_under


    def macd_crossover(self, dt):
        previous_date = self.get_previous_date(dt)

        prev_macd_stat = self.attr1_over_attr2(const.MACD_INDEX,const.SIGNAL_INDEX,previous_date)
        current_macd_stat = self.attr1_over_attr2(const.MACD_INDEX,const.SIGNAL_INDEX,dt) 
        return current_macd_stat and not prev_macd_stat
    
    def signal_crossover(self, dt):
        previous_date = self.get_previous_date(dt)

        prev_macd_stat = self.attr1_over_attr2(const.SIGNAL_INDEX,const.MACD_INDEX,previous_date)
        current_macd_stat = self.attr1_over_attr2(const.SIGNAL_INDEX,const.MACD_INDEX,dt) 
        return current_macd_stat and not prev_macd_stat
    

    def attr_secant(self,dt,attr,window):
        
        prev_date = self.get_previous_date(dt)
        for i in range(1,window):
            prev_date = self.get_previous_date(prev_date)
        return self.retrieve_value_dt(dt,attr) - self.retrieve_value_dt(prev_date,attr)



    def macd_under_zero_line(self,dt):
        return self.retrieve_value_dt(dt,const.MACD_INDEX) < 0

    def get_previous_date(self,dt):
        previousIndex = self.retrieve_value_dt(dt,const.INDEX)  - 1     
        return self.retrieveValue(self.db.getRowAtIndex(previousIndex),const.DATETIME)

    def short_long_ema_cross(self,dt:datetime): #check
        previous_date = self.get_previous_date(dt)


        curr_ema_stat = self.attr1_over_attr2(const.EMA_Short_INDEX,const.EMA_Long_INDEX,dt)
        prev_ema_stat = self.attr1_over_attr2(const.EMA_Short_INDEX,const.EMA_Long_INDEX,previous_date)

        return curr_ema_stat and not prev_ema_stat


    def all_pullback_indicies(self):
        data = self.db.tableToDataFrame()
        smooth_closings = data[const.EMA_Short_INDEX].values
        return find_peaks(-smooth_closings,distance=10,prominence=self.retrieveValue(self.db.getPreviousRow(),const.CLOSE_INDEX) * 0.001)[0]
    
    def recent_pullback_value(self,dt,search_range):
        data = self.db.getRowAD(dt)
        for i in range(search_range):
            dt = self.get_previous_date(dt)
            data = data.append(self.db.getRowAD(dt))

        data = data.iloc[::-1]  
        smooth_closings = data[const.EMA_Short_INDEX].values
        nearby_peaks = find_peaks(-smooth_closings,distance=10,prominence=self.retrieveValue(self.db.getRowAD(dt),const.CLOSE_INDEX) * 0.001)[0]
        
        return -1 if  len(nearby_peaks) == 0 else ([data[const.CLOSE_INDEX].to_list()[i] for i in nearby_peaks][-1])

        
        






##############################################################################################################################
    def strategy(self, dt):

        current_close = self.retrieve_value_dt(dt,const.CLOSE_INDEX)
        
    
        gen_trend_condition = self.attr1_over_attr2(const.CLOSE_INDEX,const.EMA_200_INDEX,dt)
        macd_condition = self.macd_crossover(dt) and self.macd_under_zero_line(dt)
        local_trend_condition = self.attr_secant(dt,const.CLOSE_INDEX,5)  < 0

        if(gen_trend_condition and macd_condition and len(self.current_orders) == 0 and local_trend_condition):
            print(local_trend_condition)
                
            stop_loss = self.recent_pullback_value(dt,search_range=15)
            stop_loss = self.retrieve_value_dt(dt,const.EMA_200_INDEX) if (stop_loss == -1 or stop_loss < current_close) else stop_loss
            
            risk = current_close - stop_loss
            take_profit = current_close + risk * const.RR_RATIO
            stop_loss_mid = current_close + risk

            order = Order(dt,current_close,stop_loss,take_profit,stop_loss_mid)
            self.current_orders.append(order)

            print("BUYING at %s (%s,%s)"%(self.db.getRowAD(dt)[const.DATETIME].tolist()[0],order.stop_loss,order.profit_take))
            
            


        for i in self.current_orders: 

            #if(current_close > i.stop_loss_mid and not i.second_profit_take):
             #   i.second_profit_take = True
            #    i.stop_loss = i.buy_closing
            #    i.profit_take = i.profit_take * 4/3
            
            if(current_close >= i.profit_take or current_close <= i.stop_loss ): #or dt.hour == 21 and dt.minute == 60-const.TICKER_INTERVAL
                earning = current_close - i.buy_closing
                i.sell_date = dt
                i.sell_closing = current_close
                i.active = False
                self.profit += earning
                self.current_orders.remove(i)

                ############## ONLY FOR TEST ################
                self.past_orders.append(i)
                #############################################

                if(current_close >= i.profit_take):
                    print("SELLING at %s with %s profit (CLOSING: %s, DUE: PROFIT_TAKE)"%(self.db.getRowAD(dt)[const.DATETIME].tolist()[0],earning,current_close))
                elif(i.stop_loss == i.buy_closing and current_close < i.stop_loss_mid):
                    print("SELLING at %s with %s profit (CLOSING: %s, DUE: STOP_LOSS_MID)"%(self.db.getRowAD(dt)[const.DATETIME].tolist()[0],earning,current_close))
                elif(current_close < i.stop_loss):
                    print("SELLING at %s with %s profit (CLOSING: %s, DUE: STOP_LOSS)"%(self.db.getRowAD(dt)[const.DATETIME].tolist()[0],earning, current_close))
                print("######################################################################")

            


    

    

