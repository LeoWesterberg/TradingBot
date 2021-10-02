from numpy import NaN 
from pandas.core.frame import DataFrame
import pandas as pd

class Indicators:

    # WANTED TO GET TO LEARN THE MATHEMATICS BEHIND THE INDICATORS AND 
    # THEREFORE THEY ARE CODED MANUALLY AND NOT BY USING PANDAS MODULE FUNCTIONS
    
    def ema_init(self, data:DataFrame, window_size:int, attribute:str = "Close") -> DataFrame:
            initial_value = data[attribute][0:window_size].ewm(span=window_size, adjust=False).mean().values[0]
            return self.__emaTemplate(data, initial_value, window_size, 0, attribute)



    def update_ema(self,data:DataFrame, window_size:int, initial_ema:float, attribute:str = "Close") -> DataFrame:
        return self.__emaTemplate(data, initial_ema, window_size, 1,attribute)
    

    def rsi_init(self, data:DataFrame, period:int, attribute:str = 'Close') -> DataFrame:
        diff_attr = (data[attribute] - data[attribute].shift(periods=1)).shift(periods=-1)
        rsi_list = ([NaN]*(period-1))
        diff_list = diff_attr.tolist()
        sliding_window = diff_list[0:period]

        curr_avg_loss = -(sum([number for number in sliding_window if number < 0])/period)
        curr_avg_gain = (sum([number for number in sliding_window if number > 0])/period)

        rs = curr_avg_gain/curr_avg_loss
        rsi_list.append(100-100/(1+rs))

        for x in range(period,diff_list.__len__()):

            if(diff_list[x] < 0):
                curr_avg_loss = (curr_avg_loss*(period-1) - diff_list[x])/period
                curr_avg_gain = curr_avg_gain*(period-1)/period
            else:
                curr_avg_gain = (curr_avg_gain*(period-1) + diff_list[x])/period
                curr_avg_loss = curr_avg_loss*(period-1)/period
            
            rs = curr_avg_gain/curr_avg_loss
            rsi_list.append(100-100/(1+rs))

        rsi_list = [NaN] + rsi_list[0:rsi_list.__len__() - 1]
        res = pd.DataFrame(rsi_list,columns=['Rsi %s'%period])  
        return res



    def macd_init(self, data:DataFrame, macd_long_ema:int, macd_short_ema:int, signal_window:int) -> DataFrame:
        ema12 = self.ema_init(data, macd_short_ema).rename(columns = {"Ema %s"%macd_short_ema:"MACD"})
        ema26 = self.ema_init(data, macd_long_ema).rename(columns = {"Ema %s"%macd_long_ema:"MACD"})
        macd_line = ema12.subtract(ema26)

        signal_line = self.ema_init(macd_line, signal_window,"MACD").rename(columns = {"Ema %s"%signal_window:"Signal"})
        macd_histogram = macd_line.rename(columns = {"MACD":"MACD Diff"}).subtract(signal_line.rename(columns = {"Signal":"MACD Diff"}))
        return pd.concat([macd_line, signal_line, macd_histogram], axis=1)
        


    def smooth_rsi_init(self, data:DataFrame, rsiPeriod:int, ema_window:int) -> DataFrame:
        rsi = self.rsi_init(data,rsiPeriod)[rsiPeriod:]
        rsi_list = [NaN]*(rsiPeriod)

        column_name = "Ema %s(Rsi %s)"%(ema_window, rsiPeriod)
        smooth_rsi_res = self.ema_init(rsi,ema_window,"Rsi %s"%rsiPeriod)
        smooth_rsi_res = smooth_rsi_res.rename(columns={"Ema %s"%ema_window:column_name})[column_name].to_list()

        column_name = "Ema %s(Rsi %s)"%(ema_window, rsiPeriod)
        return pd.DataFrame(rsi_list + smooth_rsi_res, columns=[column_name])

    

    def __emaTemplate(self,data:DataFrame, initial_ema:float, window_size:int, template_diff:int, attribute:str = "Close") -> DataFrame:
        ema_list = []
        attribute = data[attribute].to_numpy()
        ema_list.append(initial_ema)
        SMOOTHING = 2 / (1 + window_size)
        
        for index in range(1-template_diff, attribute.size):
            ema_list.append(self.__ema(ema_list[index - 1 + template_diff], attribute[index], window_size))

        res = pd.DataFrame(ema_list[template_diff:],columns=['Ema %s'%window_size])
        return res



    def __ema(self,prev_ema:int,curr_close:int,window_size:int) -> float: 
        SMOOTHING =  2/(1+window_size)
        return prev_ema * (1-SMOOTHING) + curr_close*SMOOTHING
        
