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
        for i in range(self.db.getPreviousRow()[const.INDEX].tolist()[0]-100,1,-1): #-100 for propagating towards more accurate values
            self.algo.strategy(self.db.getNthRow(i)[const.DATETIME].tolist()[0])

        past_orders = self.algo.past_orders
        


        print(self.algo.profit)

        self.showPlot(past_orders)



    def showPlot(self,past_orders):
        dates = self.data[const.DATETIME].apply(lambda x:self.__dateToString(x))
        fig = go.Figure(data=[go.Candlestick(x=dates,
                                open=self.data[const.OPEN_INDEX],
                                high=self.data[const.HIGH_INDEX],
                                low=self.data[const.LOW_INDEX],
                                close=self.data[const.CLOSE_INDEX])])

        buy_dates = list(map(lambda x: x.buy_date - datetime.timedelta(hours=3), past_orders))
        sell_dates = list(map(lambda x: x.sell_date - datetime.timedelta(hours=3), past_orders))
        buy_closing = list(map(lambda x: x.buy_closing, past_orders))
        sell_closing = list(map(lambda x: x.buy_closing, past_orders))

        self.__addTrace(fig,"Ema 200",dates)

        peaks = self.algo.all_pullback_indicies()

        closingPeaks = self.db.tableToDataFrame()['Close'][peaks].tolist()
        datePeaks = self.db.tableToDataFrame()['Datetime'][peaks].tolist()
        self.__addScatterPlot(fig,closingPeaks,datePeaks)
        


        self.__addScatterPlot(fig,buy_closing,buy_dates)
        self.__addScatterPlot(fig,sell_closing,sell_dates)

        fig.update_traces(marker=dict(size=12,      
                              line=dict(width=2,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))

        fig.update_xaxes(scaleratio=0.5,tickangle=-70,nticks=16)
        fig.show()

    ###################################### PRIVATE FUNCTIONS ############################################

    def __addScatterPlot(self,onFigure:FigureWidget,attrValues:list, attrDates:list):
        onFigure.add_scatter(y=attrValues,x=list(map(lambda x:self.__dateToString(x),attrDates)),mode='markers')
        
    def __addTrace(self,fig:FigureWidget,attr:str,dates:Series):
        fig.add_trace(go.Scatter(x=dates,y=self.data[attr].to_list()))

    def __dateToString(self,date:datetime):
        return date.strftime("%m/%d - %H:%M:%S")

    