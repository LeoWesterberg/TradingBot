from DbManagement import DbManagement as bm
import plotly.graph_objects as go
from Algorithms import Algorithms
from Constants import Constants as const

class Test:

    def __init__(self,db:bm,algo:Algorithms):
        self.db = db
        self.algo = algo
        self.data = db.tableToDataFrame("Data")
    
    def backTest(self):
        
        for i in range(self.db.getPreviousRow()[const.INDEX].tolist()[0]-1 -const.RSI_PERIOD,1,-1):
            self.algo.strat1AtDate(self.db.getNthRow(i)[const.DATETIME].tolist()[0])
        print("Profit:%s, Winn/Loss: %s/%s"%(sum(self.algo.profit),self.algo.nbrWin,self.algo.nbrLoss))
        #self.showPlot()
    

    def showPlot(self):
        candlestick = go.Figure(data=[go.Candlestick(x=self.data[const.DATETIME].astype(str),
                open=self.data[const.OPEN_INDEX],
                high=self.data[const.HIGH_INDEX],
                low=self.data[const.LOW_INDEX],
                close=self.data[const.CLOSE_INDEX])])

        candlestick.add_trace(
            go.Scatter(
            x=self.data[const.DATETIME].to_list(),
            y=self.data[const.EMA_Short_INDEX].to_list()))

        candlestick.add_trace(
            go.Scatter(
            x=self.data[const.DATETIME].to_list(),
            y=self.data[const.EMA_Long_INDEX].to_list()))

        
        candlestick.add_scatter(y=self.algo.buyClosings,x=self.algo.buyDates,mode='markers')
        candlestick.add_scatter(y=self.algo.sellClosings,x=self.algo.sellDates,mode='markers')
        #rsi = go.Figure(data=[go.Scatter(x=self.data[const.DATETIME],
         #       y=self.data[const.RSI_INDEX],
         #       )])
        #rsi.show()

        candlestick.show()

    