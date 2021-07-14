from numpy import double
from DbManagement import DbManagement
from Constants import Constants as const
import datetime

class Algorithms:
    RSI_MARGIN = (30,60)
    CURRENT_POSITION: str = const.POSITION_NONE
    CURRENT_BUY,crossDate,nbrWin,nbrLoss = -1,-1,0,0
    profit,sellDates,sellClosings,buyDates,buyClosings= [],[],[],[],[]



    def __init__(self,db:DbManagement):
        self.db = db 
        
    def strat1(self):
        self.strat1AtDate(self.db.getPreviousRow[const.DATETIME])

    def attributeDerivative(self,index):
        return self.attributeDerivativeAtDate(index,self.db.getPreviousRow[const.DATETIME])
        

    def emaCrossOver(self):
        return self.emaLongToShortCrossAT(self.db.getPreviousRow[const.DATETIME])
        
    
    def ema5OverEma12(self) -> bool:
        return self.ema5DistToEma12AtDate(self.db.getPreviousRow[const.DATETIME])
    
    def ema5DistToEma12(self):
        return self.ema5DistToEma12(self.db.getPreviousRow[const.DATETIME])

    def rsi5MarginTemp(self,margin:int,rev:int):
        return self.rsi5MarginTempAtDate(margin,rev,self.db.getPreviousRow[const.DATETIME])
    
    
    def rsi5OverMargin(self):
        return self.rsiOverMarginAtDate(self.db.getPreviousRow[const.DATETIME])
    
    def rsi5UnderMargin(self):
        return self.rsi5UnderMarginAtDate(self.db.getPreviousRow[const.DATETIME])
############################################## AT DATE ###############################################
    def strat1AtDate(self,dt:datetime) -> bool:
        if(self.CURRENT_POSITION == const.POSITION_NONE):
            if(self.emaShortToLongCrossAT(dt)):
                self.crossDate = dt
            if(self.rsiOverMarginAtDate(dt) and self.indiciesFromCrossOverAtDate(dt) <= 2): #Possible canidate for buy signal
                if(self.isInstanceAfterNewDate(dt)):
                    return
                self.CURRENT_POSITION = const.POSITION_HOLD
                self.CURRENT_BUY = self.db.getRowAtDate(dt)["Close"].tolist()[0]
                self.buyDates.append(dt -datetime.timedelta(hours=2))
                #print(dt)
                self.buyClosings.append(self.CURRENT_BUY)
                print("BUYING at %s"%self.db.getRowAtDate(dt)[const.DATETIME].tolist()[0])

        elif(self.CURRENT_POSITION == const.POSITION_HOLD):
            if(self.emaLongToShortCrossAT(dt) and self.rsi5UnderMarginAtDate(dt) or self.attributeDerivativeAtDate(const.EMA_Long_INDEX,dt) < 0
            and self.CURRENT_BUY < self.db.getRowAtDate(dt)["Close"].tolist()[0] ):
                self.CURRENT_POSITION = const.POSITION_NONE
                closing = self.db.getRowAtDate(dt)["Close"].tolist()[0]
                earning = closing - self.CURRENT_BUY
                self.profit.append(earning)
                self.sellDates.append(dt -datetime.timedelta(hours=2))
                self.sellClosings.append(closing)
                if(earning > 0): self.nbrWin += 1 
                else: self.nbrLoss +=1
                
                print("SELLING at %s with %s profit"%(self.db.getRowAtDate(dt)[const.DATETIME].tolist()[0],earning))
                print("######################################################################")
    


    def ema5DistToEma12AtDate(self,dt:datetime) -> bool: #check
        return (self.db.getRowAtDate(dt)[const.EMA_Long_INDEX] - self.db.getRowAtDate(dt)[const.EMA_Short_INDEX]).tolist()[0]

    def highBelowLongEmaAtDate(self,dt:datetime) -> bool: #check
        return (self.db.getRowAtDate(dt)[const.HIGH_INDEX].tolist()[0] < self.db.getRowAtDate(dt)[const.EMA_Long_INDEX]).tolist()[0]

    def lowBelowLongEmaAtDate(self,dt:datetime):
        return (self.db.getRowAtDate(dt)[const.LOW_INDEX].tolist()[0] < self.db.getRowAtDate(dt)[const.EMA_Long_INDEX]).tolist()[0]

    def indiciesFromCrossOverAtDate(self,dt:datetime):
        if(self.crossDate == -1):
            return 1000 #large number larger than 3
        else:
            return self.db.getRowAtDate(dt)["index"].tolist()[0] - self.db.getRowAtDate(self.crossDate)["index"].tolist()[0]
        
    def isInstanceAfterNewDate(self,dt:datetime):
        indexBefore = self.db.getRowAtDate(dt)[const.INDEX].tolist()[0] - 1
        prevDatetime = self.db.getRowAtIndex(indexBefore)[const.DATETIME].tolist()[0]
        if(abs(prevDatetime.hour - dt.hour > 1)):
            return True
        else:
            return False
    def __rsi5MarginTempAtDate(self,margin:int,rev:int,dt:datetime):
        currInstance = self.db.getRowAtDate(dt)[const.RSI_INDEX].tolist()[0]
        if(rev*currInstance <= rev*self.RSI_MARGIN[margin]):
            return True
        else: return False

    def rsiOverMarginAtDate(self,dt:datetime): #check
        return self.__rsi5MarginTempAtDate(1,-1,dt)
    
    def rsi5UnderMarginAtDate(self,dt:datetime): #check
        return self.__rsi5MarginTempAtDate(0,1,dt)

    def shortOverLongAtDate(self,dt:datetime) -> bool: #check
        return (self.db.getRowAtDate(dt)[const.EMA_Long_INDEX] >= self.db.getRowAtDate(dt)[const.EMA_Short_INDEX]).tolist()[0]

    def emaLongToShortCrossAT(self,dt:datetime): #check
        currInstance = self.db.getRowAtDate(dt)
        prevInstance = self.db.getRowAtIndex(currInstance["index"].tolist()[0] - 1)
        prevEmaLong = prevInstance[const.EMA_Long_INDEX].tolist()[0]
        currEmaLong = currInstance[const.EMA_Long_INDEX].tolist()[0]
        prevEmaShort = prevInstance[const.EMA_Short_INDEX].tolist()[0]
        currEmaShort = currInstance[const.EMA_Short_INDEX].tolist()[0]
        if(prevEmaLong <= prevEmaShort and currEmaLong >= currEmaShort):
            return True
        else: return False

    def emaShortToLongCrossAT(self,dt:datetime) -> bool: #check
        currInstance = self.db.getRowAtDate(dt)
        prevInstance = self.db.getRowAtIndex(currInstance["index"].tolist()[0] - 1)
        prevEmaLong = prevInstance[const.EMA_Long_INDEX].tolist()[0]
        currEmaLong = currInstance[const.EMA_Long_INDEX].tolist()[0]
        prevEmaShort = prevInstance[const.EMA_Short_INDEX].tolist()[0]
        currEmaShort = currInstance[const.EMA_Short_INDEX].tolist()[0]
        if(prevEmaLong >= prevEmaShort and currEmaLong <= currEmaShort):
            return True
        else: return False

    def attributeDerivativeAtDate(self,index,dt:datetime) -> double: #check
        currInstance = self.db.getRowAtDate(dt)
        prevInstance = (self.db.getRowAtIndex(currInstance["index"].tolist()[0] - 1))
        derivative = currInstance[index].tolist()[0] - prevInstance[index].tolist()[0] # TimeUnit MarketAPI.Period()
        return derivative