from numpy import NaN 
from pandas.core.frame import DataFrame
import pandas as pd

class Indicators:
    


    def emaInit(self,data:DataFrame,windowSize:int,attr = "Close")->DataFrame:
            initialValueList = data[attr].to_numpy()
            return self.__emaTemplate(data,sum(initialValueList[0:windowSize])/windowSize,windowSize,0,attr)



    def updateEma(self,data:DataFrame,windowSize:int,initialEma)->DataFrame:
        return self.__emaTemplate(data,initialEma,windowSize,1)
    


    def rsiInit(self,data:DataFrame,period:int, attr:str = 'Close'):

        diffAttr = (data[attr] - data[attr].shift(periods=1)).shift(periods=-1)
        rsiList = ([NaN]*(period-1))
        diffList = diffAttr.tolist()
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

    def macdInit(self,data:DataFrame,macdLongEma,macdShortEma,signalEmaWindow) -> DataFrame:
        ema12 = self.emaInit(data,macdShortEma).rename(columns={"Ema %s"%macdShortEma:"MACD"})
        ema26 = self.emaInit(data,macdLongEma).rename(columns={"Ema %s"%macdLongEma:"MACD"})
        MACD_line = ema12.subtract(ema26)

        signalLine = self.emaInit(MACD_line,signalEmaWindow,"MACD").rename(columns={"Ema %s"%signalEmaWindow:"Signal"})
        MACD_Histogram = MACD_line.rename(columns={"MACD":"MACD Diff"}).subtract(signalLine.rename(columns={"Signal":"MACD Diff"}))
        return pd.concat([MACD_line,signalLine,MACD_Histogram],axis=1)
        

    def SmoothRsiInit(self,data:DataFrame,rsiPeriod,emaWindow):
        rsi = self.rsiInit(data,rsiPeriod)[rsiPeriod:]
        rsiList = [NaN]*(rsiPeriod)
        columnName = "Ema %s(Rsi %s)"%(emaWindow,rsiPeriod)
        smoothRsiRes = self.emaInit(rsi,emaWindow,"Rsi %s"%rsiPeriod)
        smoothRsiRes = smoothRsiRes.rename(columns={"Ema %s"%emaWindow:columnName})[columnName].to_list()
        columnName = "Ema %s(Rsi %s)"%(emaWindow,rsiPeriod)
        return pd.DataFrame(rsiList + smoothRsiRes,columns=[columnName])

    

        
###################################### PRIVATE FUNCTIONS ############################################
    def __emaTemplate(self,data:DataFrame,initialEma,windowSize:int,templateDiff:int,attr:str = "Close"):
        emaList = []
        attr = data[attr].to_numpy()
        emaList.append(initialEma)
        SMOOTHING = 2/(1+windowSize)
        
        for index in range(1-templateDiff,attr.size):
            emaList.append(self.__ema(emaList[index - 1 + templateDiff],attr[index],windowSize))

        res = pd.DataFrame(emaList[templateDiff:],columns=['Ema %s'%windowSize])
        return res



    def __ema(self,prevEma:int,currClose:int,windowSize:int): 
        SMOOTHING =  2/(1+windowSize)
        return prevEma * (1-SMOOTHING) + currClose*SMOOTHING
        
