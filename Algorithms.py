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



    def __init__(self,db:DbManagement):
        self.db = db 
        

##### Strategy 1 works well when trend is mostly positive, but fails at stopping when curve dont recover after drop
#####
    def strategy1(self,dt:datetime) -> bool:
        
        if(self.CURRENT_POSITION == const.POSITION_NONE):
            if(self.__emaShortLongCrossAD(dt)): self.crossDate = dt
            if(self.__rsiOverMarginAD(dt) and self.__indiciesFromCrossOverAD(dt) <= 2 and not self.__isInstanceAfterNewDate(dt)):
                
                self.CURRENT_POSITION = const.POSITION_HOLD
                self.CURRENT_BUY = self.db.getRowAD(dt)["Close"].tolist()[0]

                self.buyDates.append(dt -datetime.timedelta(hours=2))
                self.buyClosings.append(self.CURRENT_BUY)
                print("BUYING at %s"%self.db.getRowAD(dt)[const.DATETIME].tolist()[0])

        elif(self.CURRENT_POSITION == const.POSITION_HOLD):
            emaCrossAndRsiDrop:bool = self.__emaLongShortCrossAD(dt) and self.__rsi5UnderMarginAD(dt)
            attriDeriv:bool =  self.__attributeDerivativeAD(const.EMA_Long_INDEX,dt) < 0
            buyBelowClose = self.CURRENT_BUY < self.db.getRowAD(dt)["Close"].tolist()[0]

            if(emaCrossAndRsiDrop or attriDeriv < 0 and buyBelowClose):
                self.CURRENT_POSITION = const.POSITION_NONE
                closing = self.db.getRowAD(dt)["Close"].tolist()[0]
                earning = closing - self.CURRENT_BUY
                
                self.profit.append(earning)
                self.sellDates.append(dt -datetime.timedelta(hours=2))
                self.sellClosings.append(closing)
                if(earning > 0): self.nbrWin += 1 
                else: self.nbrLoss +=1
                
                print("SELLING at %s with %s profit"%(self.db.getRowAD(dt)[const.DATETIME].tolist()[0],earning))
                print("######################################################################")
    


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
        currDf = self.db.getPreviousRow()
        prevDf = self.db.getRowAtIndex(self.__retrieveValue(currDf,const.INDEX) - 1)

        emaValues = self.__initEmaValues(currDf,prevDf)
        if(emaValues(0) <= emaValues(2) and emaValues(1) >= emaValues(3)):
            return True
        else: return False



    def __emaShortLongCrossAD(self,dt:datetime) -> bool: #check
        currDf = self.db.getPreviousRow()
        prevDf = self.db.getRowAtIndex(self.__retrieveValue(currDf,const.INDEX) - 1)

        emaValues = self.__initEmaValues(currDf,prevDf)
        if(emaValues[0] >= emaValues[2] and emaValues[1] <= emaValues[3]):
            return True
        else: return False



    def __attributeDerivativeAD(self,index,dt:datetime) -> double: #check
            derivative = self.__retrieveValue(self.currInstance[index]) - self.__retrieveValue(self.prevInstance[index]) # TimeUnit MarketAPI.Period()
            return derivative



    def __retrieveValue(self,df:DataFrame,attr:str):
        return df[attr].to_list()[0]
        


    def __initEmaValues(self,currDf,PrevDf):
        prevEmaLong = self.__retrieveValue(PrevDf,const.EMA_Long_INDEX)
        currEmaLong = self.__retrieveValue(currDf,const.EMA_Long_INDEX)
        prevEmaShort = self.__retrieveValue(PrevDf,const.EMA_Short_INDEX)
        currEmaShort = self.__retrieveValue(currDf,const.EMA_Short_INDEX)
        return (prevEmaLong,currEmaLong,prevEmaShort,currEmaShort)