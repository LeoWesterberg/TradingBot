from pandas.core.frame import DataFrame
from DbManagement import DbManagement
from Indicators import Indicators as Ind
from MarketAPI import MarketAPI as API
import pandas as pd
from Constants import Constants as const

class InitializeBot:

    def __init__(self,db:DbManagement, ind:Ind, api:API):
        self.api = api
        self.db = db
        self.ind = ind
    
    def resetBot(self):
        data = self.api.getData(self.api.stock)
        dates = data[const.DATETIME]
        dataIndicatorsConcat = pd.concat([data,self.ind.rsiInit(data,const.RSI_PERIOD),
                                               self.ind.emaInit(data,const.LONG_EMA),
                                               self.ind.emaInit(data,const.SHORT_EMA),
                                               self.ind.macdInit(data,26,12,9),
                                               self.ind.SmoothRsiInit(data,const.RSI_PERIOD,const.RSI_SMOOTH_EMA_PERIOD)],axis=1)
        self.db.reset(dataIndicatorsConcat,"Data")


    def updateBot(self):
        previousRow = self.db.getPreviousRow()

        prevShortEma = self.__retrieveValue(previousRow,const.EMA_Short_INDEX)
        prevLongEma = self.__retrieveValue(previousRow,const.EMA_Long_INDEX)
        prevIndex = self.__retrieveValue(previousRow,const.INDEX)
        requestDate = self.__retrieveValue(previousRow,const.DATETIME)
        data:DataFrame = self.api.getDataSince(requestDate).iloc[1: , :]
        
        # CALCULATING NEW EMAS BASED ON PREVIOUS ONES
        newShortEma = self.ind.updateEma(data,const.SHORT_EMA,prevShortEma)
        newLongEma = self.ind.updateEma(data,const.LONG_EMA,prevLongEma)   
        dropColumns = ['index'] + const.ACTIVE_INDICATORS

        # CALCULATING NEW RSI VALUE BASED ON PREVIOUS 150(DUE TO INCREASING ACCURACY) ROWS
        newRsi:DataFrame =self.ind.rsiInit(self.db.getLastNthRow(150).iloc[::-1].drop(columns=['index']+const.ACTIVE_INDICATORS).append(data),5)[150:]
        newRsi.reset_index(inplace=True)

        #CONFIGURING AND CONCATENATING RESULTS AND ADDING TO DATABASE
        data.reset_index(inplace=True)
        res = pd.concat([data.drop(columns='index'),newRsi.drop(columns='index'),prevShortEma,prevLongEma],axis=1)
        res.index = range(prevIndex+1,prevIndex+len(res)+1)
        self.db.appendRow(res)

    def __retrieveValue(self,df:DataFrame,attr:str):
        return df[attr].to_list()[0]



        

