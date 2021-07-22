import datetime
from pandas.core.series import Series
from plotly.missing_ipywidgets import FigureWidget 
from DbManagement import DbManagement as bm
import plotly.graph_objects as go
from Algorithms import Algorithms
from NewAlgorithms import NewAlgorithms
from Constants import Constants as const



class Test:

    def __init__(self,db:bm,algo:NewAlgorithms):
        self.db = db
        self.algo = algo
        self.data = db.tableToDataFrame("Data")
    


    def backTest(self):
        for i in range(self.db.getPreviousRow()[const.INDEX].tolist()[0]-30,1,-1): #-100 for propagating towards more accurate values
            self.algo.strategy(self.db.getNthRow(i)[const.DATETIME].tolist()[0])
        nbrWin = count = sum(map(lambda x : x > 0 == 1, self.algo.profit))
        nbrLoss = count = sum(map(lambda x : x < 0 == 1, self.algo.profit))

        print("Profit:%s, Winn/Loss: %s/%s"%(sum(self.algo.profit),nbrWin,nbrLoss))
        self.showPlot()



    def showPlot(self):
        dates = self.data[const.DATETIME].apply(lambda x:self.__dateToString(x))
        fig = go.Figure(data=[go.Candlestick(x=dates,
                                open=self.data[const.OPEN_INDEX],
                                high=self.data[const.HIGH_INDEX],
                                low=self.data[const.LOW_INDEX],
                                close=self.data[const.CLOSE_INDEX])])

        self.__addTrace(fig,const.EMA_Long_INDEX,dates)
        self.__addTrace(fig,const.EMA_Short_INDEX,dates)
        self.__addTrace(fig,"Ema 200",dates)



        self.__addScatterPlot(fig,self.algo.buyClosings,self.algo.buyDates)
        self.__addScatterPlot(fig,self.algo.sellClosings,self.algo.sellDates)

        fig.update_xaxes(scaleratio=0.5,tickangle=-70,nticks=16)
        fig.show()

    ###################################### PRIVATE FUNCTIONS ############################################

    def __addScatterPlot(self,onFigure:FigureWidget,attrValues:list, attrDates:list):
        onFigure.add_scatter(y=attrValues,x=list(map(lambda x:self.__dateToString(x),attrDates)),mode='markers')
        
    def __addTrace(self,fig:FigureWidget,attr:str,dates:Series):
        fig.add_trace(go.Scatter(x=dates,y=self.data[attr].to_list()))

    def __dateToString(self,date:datetime):
        return date.strftime("%m/%d - %H:%M:%S")

    