import datetime
from pandas import pandas 


from DbManagement import DbManagement as bm
import plotly.graph_objects as go
from Algorithms import Algorithms
from Constants import Constants as const
import plotly.express as px



class Test:

    def __init__(self,db:bm,algo:Algorithms):
        self.db = db
        self.algo = algo
        self.data = db.tableToDataFrame("Data")
    
    def backTest(self):
        
        for i in range(self.db.getPreviousRow()[const.INDEX].tolist()[0]-100,1,-1): #-100 for propagating towards more accurate values
            self.algo.strat1AtDate(self.db.getNthRow(i)[const.DATETIME].tolist()[0])
        print("Profit:%s, Winn/Loss: %s/%s"%(sum(self.algo.profit),self.algo.nbrWin,self.algo.nbrLoss))
        self.showPlot()
    

    def showPlot(self):
        dates:datetime = self.data[const.DATETIME].apply(lambda x: x.strftime("%m/%d %H:%M:%S"))
        candlestick = go.Figure(data=[go.Candlestick(x=dates,
                open=self.data[const.OPEN_INDEX],
                high=self.data[const.HIGH_INDEX],
                low=self.data[const.LOW_INDEX],
                close=self.data[const.CLOSE_INDEX])])

        candlestick.add_trace(
            go.Scatter(
            x=dates,
            y=self.data[const.EMA_Short_INDEX].to_list()))

        
        candlestick.add_trace(
            go.Scatter(
            x=dates,
            y=self.data[const.EMA_Long_INDEX].to_list()))

        
        candlestick.add_scatter(y=self.algo.buyClosings,x=list(map(lambda x:x.strftime("%m/%d - %H:%M:%S"), self.algo.buyDates)),mode='markers')
        candlestick.add_scatter(y=self.algo.sellClosings,x=list(map(lambda x:x.strftime("%m/%d - %H:%M:%S"), self.algo.sellDates)),mode='markers')
        candlestick.update_xaxes(scaleratio=0.5,tickangle=-70,nticks=16)
        

        candlestick.show()

    