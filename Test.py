import datetime
from pandas.core.frame import DataFrame
from pandas.core.indexes.datetimes import date_range
from pandas.core.series import Series
from plotly.missing_ipywidgets import FigureWidget 
import plotly.graph_objects as go

from DbManagement import DbManagement
from Algorithms import Algorithms
from Constants import Constants as const



class Test:

    def __init__(self,db:DbManagement, algorithms:Algorithms):
        self.db = db
        self.algorithms = algorithms
    


    def backTest(self):
        start_date = self.db.get_row_at_index(100,const.TICKERS[0])[const.DATETIME].tolist()[0]
        print("Beginning at: %s"%start_date)
        end_date = self.db.get_previous_row(const.TICKERS[0])[const.DATETIME].tolist()[0]
        date_times = date_range(start=start_date, end=end_date,freq='%smin'%const.TICKER_INTERVAL)
        
        for date in date_times:
            for ticker in const.TICKERS:
                date_row = self.db.get_row_at_date(date,ticker)
                if(date_row.size != 0):
                    self.algorithms.buy_strategy(date,ticker)
            self.algorithms.sell_strategy(date)
        #past_orders = self.algorithms.past_orders
        


        #print(self.algorithms.profit)

       # self.showPlot(past_orders)



    def showPlot(self,past_orders, date:DataFrame):
        dates = self.data[const.DATETIME].apply(lambda x:self.__dateToString(x))
        fig = go.Figure(data=[go.Candlestick(x=dates,
                                open=self.data[const.OPEN_INDEX],
                                high=self.data[const.HIGH_INDEX],
                                low=self.data[const.LOW_INDEX],
                                close=self.data[const.CLOSE_INDEX])])

        buy_dates = list(map(lambda x: x.buy_date, past_orders))
        sell_dates = list(map(lambda x: x.sell_date, past_orders))
        buy_closing = list(map(lambda x: x.buy_closing, past_orders))
        sell_closing = list(map(lambda x: x.sell_closing, past_orders))

        self.__addTrace(fig,"Ema 200",dates,"200 Ema")

        peaks = self.algorithms.all_pullback_indicies()

        closingPeaks = self.db.get_table()['Close'][peaks].tolist()
        datePeaks = self.db.get_table()['Datetime'][peaks].tolist()
        self.__addScatterPlot(fig,closingPeaks,datePeaks, "Peaks")
        
        self.__addScatterPlot(fig,self.algorithms.macd_closings,self.algorithms.macd_dates,"MACD signals")


        self.__addScatterPlot(fig,buy_closing,buy_dates, "Buy signals")
        self.__addScatterPlot(fig,sell_closing,sell_dates,"Sell signals")

        fig.update_traces(marker=dict(size=12,      
                              line=dict(width=2,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))

        fig.update_xaxes(scaleratio=0.5,tickangle=-70,nticks=16)
        fig.show()

    ###################################### PRIVATE FUNCTIONS ############################################

    def __addScatterPlot(self,onFigure:FigureWidget,attrValues:list, attrDates:list,name):
        onFigure.add_scatter(y=attrValues,x=list(map(lambda x:self.__dateToString(x),attrDates)),mode='markers',name=name)
        
    def __addTrace(self,fig:FigureWidget,attr:str,dates:Series,name):
        fig.add_trace(go.Scatter(x=dates,y=self.data[attr].to_list(),name = name))

    def __dateToString(self,date:datetime):
        return date.strftime("%m/%d - %H:%M:%S")

    