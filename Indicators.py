from numpy import NaN 
from pandas.core.frame import DataFrame
import pandas as pd
from pandas.core.reshape.concat import concat
class Indicators:
    


    def emaInit(self,data:DataFrame,windowSize:int,attribute ='Close')->DataFrame:
        close = data[attribute].to_numpy()
        return self.emaTemplate(data,sum(close[0:windowSize])/windowSize,windowSize,0)
        
    def updateEma(self,data:DataFrame,windowSize:int,initialEma)->DataFrame:
        return self.emaTemplate(data,initialEma,windowSize,1)
    
    def emaTemplate(self,data:DataFrame,initialEma,windowSize:int,listRange:int,attribute = 'Close'):
        emaList = []
        close = data[attribute].to_numpy()
        emaList.append(initialEma)
        SMOOTHING = 2/(1+windowSize)
        for index in range(1-listRange,close.size):
            emaList.append(self.__ema(emaList[index - 1 + listRange],close[index],windowSize))
        res = pd.DataFrame(emaList[listRange:],columns=['Ema %s'%windowSize])
        return res

    def __ema(self,prevEma:int,currClose:int,windowSize:int): 
        SMOOTHING =  2/(1+windowSize)
        return prevEma * (1-SMOOTHING) + currClose*SMOOTHING
        
    def rsiInit(self,data:DataFrame,period:int):
        diff = (data['Close'] - data['Close'].shift(periods=1)).shift(periods=-1)
        rsiList = [NaN]*(period-1)
        diffList = diff.tolist()
        slidingWindow = diffList[0:period]
        currAvgLoss = -(sum([number for number in slidingWindow if number < 0])/period)
        currAvgGain = (sum([number for number in slidingWindow if number > 0])/period)
        rs = currAvgGain/currAvgLoss
        rsiList.append(100-100/(1+rs))
        for x in range(period,diffList.__len__()):
            if(diffList[x] < 0):
                currAvgLoss = (currAvgLoss*(period-1) - diffList[x])/period
                currAvgGain = currAvgGain*(period-1)/period
            else:
                currAvgGain = (currAvgGain*(period-1) + diffList[x])/period
                currAvgLoss = currAvgLoss*(period-1)/period
            
            rs = currAvgGain/currAvgLoss
            rsiList.append(100-100/(1+rs))
        rsiList = [NaN] + rsiList[0:rsiList.__len__() - 1]
        res = pd.DataFrame(rsiList,columns=['Rsi %s'%period])  
        return res

    def macdInit(self,data:DataFrame) -> DataFrame:
        MACD_line = self.emaInit(data,12).rename(columns={"Ema 12":"MACD Line"}).subtract(self.emaInit(data,26).rename(columns={"Ema 26":"MACD Line"}))
        signalLine = self.emaTemplate(MACD_line,sum(MACD_line['MACD Line'].to_numpy()[0:9])/9,9,0,'MACD Line').rename(columns={"Ema 9":"Signal Line"})
        MACD_Histogram = MACD_line.rename(columns={"MACD Line":"MACD Histogram"}).subtract(signalLine.rename(columns={"Signal Line":"MACD Histogram"}))
        return pd.concat([MACD_line,signalLine,MACD_Histogram],axis=1)
        
        

    def SmoothRsiInit(self,data:DataFrame,rsiPeriod,emaWindow):
        rsi = self.rsiInit(data,rsiPeriod)[rsiPeriod:]
        rsiList = [NaN]*(rsiPeriod)
        columnName = "Ema %s(Rsi %s)"%(emaWindow,rsiPeriod)
        initialEmaValue = sum(rsi["Rsi %s"%rsiPeriod].to_numpy()[0:emaWindow])/emaWindow
        smoothRsiRes = self.emaTemplate(rsi,initialEmaValue,emaWindow,0,"Rsi %s"%rsiPeriod).rename(
                        columns={"Ema %s"%emaWindow:columnName})[columnName].to_list()
        
        res = pd.DataFrame(rsiList + smoothRsiRes,columns=["Ema %s(Rsi %s)"%(emaWindow,rsiPeriod)])  
        print(res)
        return res
