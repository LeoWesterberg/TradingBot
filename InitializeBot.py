from DbManagement import DbManagement as Bm
from Indicators import Indicators as Ind
from MarketAPI import MarketAPI as API
import pandas as pd
from Constants import Constants as const

class InitializeBot:

    def __init__(self,db:Bm, ind:Ind, api:API):
        self.api = api
        self.db = db
        self.ind = ind
    
    def resetBot(self):
        data = self.api.getData(self.api.stock)
        dataIndicatorsConcat = pd.concat([data,self.ind.rsiInit(data,const.RSI_PERIOD),
                                               self.ind.emaInit(data,const.LONG_EMA),
                                               self.ind.emaInit(data,const.SHORT_EMA),
                                               self.ind.macdInit(data),
                                               self.ind.SmoothRsiInit(data,const.RSI_PERIOD,3)],axis=1)
        self.db.reset(dataIndicatorsConcat)

    def updateBot(self):
        self.db.update()
        

