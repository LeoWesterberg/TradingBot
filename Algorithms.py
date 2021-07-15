from numpy import double
from pandas.core.frame import DataFrame
from DbManagement import DbManagement
from Constants import Constants as const
import datetime

class Algorithms:
    RSI_MARGIN = (const.RSI_LOWER_BOUND,const.RSI_UPPER_BOUND)
    CURRENT_POSITION: str = const.POSITION_NONE
    CURRENT_BUY,crossDate,nbrWin,nbrLoss = -1,-1,0,0
    profit,sellDates,sellClosings,buyDates,buyClosings= [],[],[],[],[]
    rsiTickDate = -1
    last10Closings = []




    def __init__(self,db:DbManagement):
        self.db = db 
        

##### Strategy 1 works well when trend is mostly positive, but fails at stopping when curve dont recover after drop
#####
    def strategy1(self,dt:datetime) -> bool:
        
        if(self.CURRENT_POSITION == const.POSITION_NONE):
           
            if(self.__emaShortLongCrossAD(dt)): 
                self.crossDate = dt

            if(self.__rsiOverMarginAD(dt) and self.__indiciesFromCrossOverAD(dt) <= 1 and not self.__isInstanceAfterNewDate(dt)):
                self.CURRENT_POSITION = const.POSITION_HOLD
                self.CURRENT_BUY = self.db.getRowAD(dt)["Close"].tolist()[0]

                self.buyDates.append(dt -datetime.timedelta(hours=2))
                self.buyClosings.append(self.CURRENT_BUY)
                print("BUYING at %s"%self.db.getRowAD(dt)[const.DATETIME].tolist()[0])

        elif(self.CURRENT_POSITION == const.POSITION_HOLD):
            
            if(self.__closeEmaLongCrossAD(dt)): 
                self.crossDate = dt


            crossLess = self.__rsi5UnderMarginAD(dt) and self.__indiciesFromCrossOverAD(dt) <= 1
            attriDeriv:bool =  self.__attributeDerivativeAD(const.EMA_Long_INDEX,dt) < 0
            buyBelowClose = self.CURRENT_BUY < self.db.getRowAD(dt)["Close"].tolist()[0]
            if(crossLess or attriDeriv < 0 and buyBelowClose):
                self.CURRENT_POSITION = const.POSITION_NONE
                closing = self.db.getRowAD(dt)["Close"].tolist()[0]
                earning = closing - self.CURRENT_BUY
                self.crossDate = -1
                self.profit.append(earning)
                self.sellDates.append(dt -datetime.timedelta(hours=2))
                self.sellClosings.append(closing)
                if(earning > 0): self.nbrWin += 1 
                else: self.nbrLoss +=1
                
                print("SELLING at %s with %s profit"%(self.db.getRowAD(dt)[const.DATETIME].tolist()[0],earning))
                print("######################################################################")
    

    def strategy2(self,dt):
        MACDLine = self.__getAttrDfAtDate(dt,const.MACD_INDEX)
        MACDDiff= self.__getAttrDfAtDate(dt,const.MACD_DIFF_INDEX)
        signalLine= self.__getAttrDfAtDate(dt,const.SIGNAL_INDEX)
        smoothRsi = self.__getAttrDfAtDate(dt,const.RSI_SMOOTH_INDEX)

        if(self.CURRENT_POSITION == const.POSITION_NONE):
            if(smoothRsi >= const.RSI_UPPER_BOUND):
                self.rsiTickDate = dt
            #print("%s %s %s"%(MACDDiff, self.__attributeDerivativeAD(const.MACD_DIFF_INDEX,dt), self.__timeSinceRsiTick(dt)))
            cond = MACDDiff > 0 and self.__attributeDerivativeAD(const.MACD_DIFF_INDEX,dt) > 0 and self.__timeSinceRsiTick(dt) <= 1
            if(cond and not self.__isInstanceAfterNewDate(dt) or self.MACDCrossesSignal and smoothRsi >50):
                self.rsiTickDate = -1
                self.CURRENT_POSITION = const.POSITION_HOLD
                self.CURRENT_BUY = self.db.getRowAD(dt)["Close"].tolist()[0]
                self.buyClosings.append(self.CURRENT_BUY)
                self.buyDates.append(dt-datetime.timedelta(hours=2))
                print("BUYING at %s"%self.db.getRowAD(dt)[const.DATETIME].tolist()[0])
                
        elif(self.CURRENT_POSITION == const.POSITION_HOLD):
            if(smoothRsi <= const.RSI_LOWER_BOUND):
                self.rsiTickDate = dt
            cond = MACDDiff < 0 and self.__attributeDerivativeAD(const.MACD_DIFF_INDEX,dt) < 0 and self.__timeSinceRsiTick(dt) <= 1
            if(cond or self.signalCrossesMACD(dt) and  smoothRsi < 50):
                self.negClosingsInARow = 0
                self.CURRENT_POSITION = const.POSITION_NONE
                closing = self.db.getRowAD(dt)["Close"].tolist()[0]
                earning = closing - self.CURRENT_BUY
                if(self.last10Closings.__len__()< 5):
                    self.last10Closings.append(closing)
                else:
                    self.last10Closings.pop(0)
                    self.last10Closings.append(closing)
                self.crossDate = -1
                self.profit.append(earning)
                self.sellDates.append(dt-datetime.timedelta(hours=2)) #-datetime.timedelta(hours=2)
                self.sellClosings.append(closing)
                if(earning > 0): self.nbrWin += 1 
                else: self.nbrLoss +=1
                
                print("SELLING at %s with %s profit"%(self.db.getRowAD(dt)[const.DATETIME].tolist()[0],earning))
                print("######################################################################")
    





    def signalCrossesMACD(self,dt):
        currDf = self.db.getRowAD(dt)
        prevDf = self.db.getRowAtIndex(self.__retrieveValue(currDf,const.INDEX) - 1)
        currMacdDiff = self.__retrieveValue(prevDf,const.MACD_DIFF_INDEX)
        prevMACD = self.__retrieveValue(prevDf,const.MACD_INDEX)
        currMACD = self.__retrieveValue(currDf,const.MACD_INDEX)
        prevSignal = self.__retrieveValue(prevDf,const.SIGNAL_INDEX)
        currSignal = self.__retrieveValue(currDf,const.SIGNAL_INDEX)
        return (prevMACD > prevSignal and currMACD <= currSignal and currMacdDiff > 0)

    def MACDCrossesSignal(self,dt):
        currDf = self.db.getRowAD(dt)
        prevDf = self.db.getRowAtIndex(self.__retrieveValue(currDf,const.INDEX) - 1)
        currMacdDiff = self.__retrieveValue(prevDf,const.MACD_DIFF_INDEX)
        prevMACD = self.__retrieveValue(prevDf,const.MACD_INDEX)
        currMACD = self.__retrieveValue(currDf,const.MACD_INDEX)
        prevSignal = self.__retrieveValue(prevDf,const.SIGNAL_INDEX)
        currSignal = self.__retrieveValue(currDf,const.SIGNAL_INDEX)
        return (prevMACD > prevSignal and currMACD <= currSignal and currMacdDiff > 0)

    def __timeSinceRsiTick(self,dt):
        if(self.rsiTickDate == -1):
            return 10 #Only requiresddnf number larger than 5
        else:
            return self.__attrDistBetweenDates(const.INDEX,const.INDEX,dt,self.rsiTickDate)




    def __attrDistBetweenDates(self,attr1,attr2,date1,date2):
            return (self.db.getRowAD(date1)[attr1] - self.db.getRowAD(date2)[attr2]).tolist()[0]



    def __indiciesFromCrossOverAD(self,dt:datetime):
        if(self.crossDate == -1):
            return 10 #Only requiresddnf number larger than 3
        else:
            return self.__attrDistBetweenDates(const.INDEX,const.INDEX,dt,self.crossDate)



    def __isInstanceAfterNewDate(self,dt:datetime):
        indexBefore = self.db.getRowAD(dt)[const.INDEX].tolist()[0] - 1
        prevDatetime = self.db.getRowAtIndex(indexBefore)[const.DATETIME].tolist()[0]
        if(abs(prevDatetime.hour - dt.hour > 1)):
            return True
        else:
            return False
            


    def __rsi5MarginTempAD(self,margin:int,rev:int,dt:datetime):
        currInstance = self.db.getRowAD(dt)[const.RSI_INDEX].tolist()[0]
        if(rev*currInstance <= rev*self.RSI_MARGIN[margin]):
            return True
        else: return False



    def __rsiOverMarginAD(self,dt:datetime): #check
        return self.__rsi5MarginTempAD(1,-1,dt)
    


    def __rsi5UnderMarginAD(self,dt:datetime): #check
        return self.__rsi5MarginTempAD(0,1,dt)



    def __emaLongShortCrossAD(self,dt:datetime): #check
        currDf = self.db.getRowAD(dt)
        prevDf = self.db.getRowAtIndex(self.__retrieveValue(currDf,const.INDEX) - 1)

        emaValues = self.__initEmaValues(currDf,prevDf)
        if(emaValues[0] <= emaValues[2] and emaValues[1] >= emaValues[3]):
            return True
        else: return False

    def __closeEmaLongCrossAD(self,dt:datetime): #check
        currDf = self.db.getRowAD(dt)
        prevDf = self.db.getRowAtIndex(self.__retrieveValue(currDf,const.INDEX) - 1)

        emaValues = self.__initCloseEmaValues(currDf,prevDf)
        if(emaValues[0] <= emaValues[2] and emaValues[1] >= emaValues[3]):
            return True
        else: return False



    def __emaShortLongCrossAD(self,dt:datetime) -> bool: #check
        currDf = self.db.getRowAD(dt)
        prevDf = self.db.getRowAtIndex(self.__retrieveValue(currDf,const.INDEX) - 1)

        emaValues = self.__initEmaValues(currDf,prevDf)
        if(emaValues[3] >= emaValues[2] and emaValues[1] <= emaValues[0]):
            return True
        else: return False



    def __attributeDerivativeAD(self,index,dt:datetime) -> double: #check
        currDf = self.db.getRowAD(dt)
        prevDf = self.db.getRowAtIndex(self.__retrieveValue(currDf,const.INDEX) - 1)
        derivative = self.__retrieveValue(currDf,index) - self.__retrieveValue(prevDf,index) # TimeUnit MarketAPI.Period()
        return derivative



    def __retrieveValue(self,df:DataFrame,attr:str):
        return df[attr].to_list()[0]
        
    def __getAttrDfAtDate(self,dt,index):
        return self.db.getRowAD(dt)[index].to_list()[0]


    def __initEmaValues(self,currDf,PrevDf):
        prevEmaLong = self.__retrieveValue(PrevDf,const.EMA_Long_INDEX)
        currEmaLong = self.__retrieveValue(currDf,const.EMA_Long_INDEX)
        prevEmaShort = self.__retrieveValue(PrevDf,const.EMA_Short_INDEX)
        currEmaShort = self.__retrieveValue(currDf,const.EMA_Short_INDEX)
        return (prevEmaLong,currEmaLong,prevEmaShort,currEmaShort)

    def __initCloseEmaValues(self,currDf,PrevDf):
        prevClose = self.__retrieveValue(PrevDf,const.CLOSE_INDEX)
        currClose = self.__retrieveValue(currDf,const.CLOSE_INDEX)
        prevEmaLong = self.__retrieveValue(PrevDf,const.EMA_Long_INDEX)
        currEmaLong = self.__retrieveValue(currDf,const.EMA_Long_INDEX)
        return (currEmaLong,currClose,prevEmaLong,prevClose)