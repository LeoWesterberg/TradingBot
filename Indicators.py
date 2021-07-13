from numpy import NaN 
from pandas.core.frame import DataFrame
import pandas as pd
class Indicators:
    


    def emaInit(self,data:DataFrame,windowSize:int)->DataFrame:
        close = data['Close'].to_numpy()
        return self.emaTemplate(data,sum(close[0:windowSize])/windowSize,windowSize,0)
        
    def updateEma(self,data:DataFrame,windowSize:int,initialEma)->DataFrame:
        return self.emaTemplate(data,initialEma,windowSize,1)
    
    def emaTemplate(self,data:DataFrame,initialEma,windowSize:int,listRange:int):
        emaList = []
        close = data['Close'].to_numpy()
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


