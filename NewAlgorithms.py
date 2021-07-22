from numpy import double
from pandas.core.frame import DataFrame
from DbManagement import DbManagement
from Constants import Constants as const
import datetime

class NewAlgorithms:
    stop_loss, stop_loss_mid, take_profit, current_buy = None,None,None,None
    profit,sellDates,sellClosings,buyDates,buyClosings= [],[],[],[],[]
    CURRENT_POSITION: str = const.POSITION_NONE



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
        previous_date = self.getPreviousDate(dt)

        prev_macd_stat = self.attr1_over_attr2(const.MACD_INDEX,const.SIGNAL_INDEX,previous_date)
        current_macd_stat = self.attr1_over_attr2(const.MACD_INDEX,const.SIGNAL_INDEX,dt) 
        return current_macd_stat and not prev_macd_stat
    

    def macd_under_zero_line(self,dt):
        return self.retrieve_value_dt(dt,const.MACD_INDEX) < 0

    def getPreviousDate(self,dt):
        previousIndex = self.retrieve_value_dt(dt,const.INDEX)  - 1     
        return self.retrieveValue(self.db.getRowAtIndex(previousIndex),const.DATETIME)

    def short_long_ema_cross(self,dt:datetime): #check
        previous_date = self.getPreviousDate(dt)


        curr_ema_stat = self.attr1_over_attr2(const.EMA_Short_INDEX,const.EMA_Long_INDEX,dt)
        prev_ema_stat = self.attr1_over_attr2(const.EMA_Short_INDEX,const.EMA_Long_INDEX,previous_date)

        return curr_ema_stat and not prev_ema_stat



##############################################################################################################################
    def strategy(self, dt):
        current_close = self.retrieve_value_dt(dt,const.CLOSE_INDEX)
        
        if(self.CURRENT_POSITION == const.POSITION_NONE):
            trend_condition = self.attr1_over_attr2(const.CLOSE_INDEX,const.EMA_200_INDEX,dt)
            macd_condition = self.macd_crossover(dt) and self.macd_under_zero_line(dt)
            #print("%s %s %s ##################### %s #### %s"%(macd_condition,trend_condition,dt,self.retrieveValue(self.db.getRowAD(dt),const.MACD_DIFF_INDEX)))

            

            if(trend_condition and macd_condition):

                self.current_buy = current_close
                self.stop_loss = self.retrieve_value_dt(dt,const.EMA_200_INDEX)

                risk = current_close - self.stop_loss
                self.take_profit = current_close + risk * const.RR_RATIO
                self.stop_loss_mid = current_close + risk

                self.CURRENT_POSITION = const.POSITION_HOLD

                self.buyDates.append(dt -datetime.timedelta(hours=2))
                self.buyClosings.append(self.current_buy)
                print("BUYING at %s(close: %s, stopLoss: %s, takeProfit = %s"%(self.db.getRowAD(dt)[const.DATETIME].tolist()[0],current_close,self.stop_loss,self.take_profit))


        else:
            if(current_close >= self.stop_loss_mid and not self.stop_loss == self.current_buy):
                self.stop_loss = self.current_buy
            
            #current_close >= self.take_profit or current_close <= self.stop_loss or dt.hour == 21 and dt.minute == 60-const.TICKER_INTERVAL
            if((self.short_long_ema_cross(dt)  or dt.hour == 21 and dt.minute == 60-const.TICKER_INTERVAL) or current_close >= self.take_profit):
                self.CURRENT_POSITION = const.POSITION_NONE
                earning = current_close - self.current_buy
                self.profit.append(earning)

                self.sellDates.append(dt -datetime.timedelta(hours=2))
                self.sellClosings.append(current_close)

                print("SELLING at %s with %s profit (close: %s, stopLoss: %s, takeProfit = %s"%(self.db.getRowAD(dt)[const.DATETIME].tolist()[0],earning,current_close,self.stop_loss,self.take_profit))
                print("######################################################################")


            


    

    

