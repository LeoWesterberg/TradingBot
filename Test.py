import datetime
import plotly.graph_objects as go
from pandas.core.indexes.datetimes import date_range
from pandas.core.series import Series
from plotly.missing_ipywidgets import FigureWidget 
from DbManagement import DbManagement
from Algorithms import Algorithms
from Constants import Constants as const



class Test:

    def __init__(self,db:DbManagement, algorithms:Algorithms):
        self.db = db
        self.algorithms = algorithms
        self.order_manag = self.algorithms.order_management
    


    def backTest(self):
        start_date = self.db.get_row_at_index(100,const.TICKERS[0]).at[0,const.DATETIME]
        print("Beginning at: %s"%start_date)
        
        end_date = self.db.get_previous_row(const.TICKERS[0]).at[0, const.DATETIME]
        date_times = date_range(start=start_date, end=end_date,freq='%smin'%const.TICKER_INTERVAL)
        
        for date in date_times:
            for ticker in const.TICKERS:
                date_row = self.db.get_row_at_date(date, ticker)

                if(date_row.size != 0):
                    self.algorithms.buy_strategy(date, True, ticker)

            self.algorithms.sell_strategy(date, True)  
                  
        self.showResult()



    def showResult(self):
        closings = self.order_manag.previous_holdings
        print("############################# RESULT #################################")
        for ticker in const.TICKERS:
            ticker_holdings = closings.loc[closings['Ticker'] == ticker]
            profits_result = (ticker_holdings["Sell"] - ticker_holdings["Buy"]).sum()
            print(ticker + ": " +  str(profits_result))

            ticker_sell_dates = ticker_holdings["Datetime Sell"].tolist()
            ticker_sell_prices = list(map(lambda x:self.db.get_row_at_date(x, ticker)[const.CLOSE].tolist()[0],ticker_sell_dates))
            
            ticker_buy_dates = ticker_holdings["Datetime Buy"].tolist()
            ticker_buy_prices = list(map(lambda x:self.db.get_row_at_date(x, ticker)[const.CLOSE].tolist()[0],ticker_buy_dates))

            data = self.db.get_table(ticker)
            dates = data[const.DATETIME].apply(lambda x:self.__dateToString(x))
            fig = go.Figure(data=[go.Candlestick(x=dates,
                                    open=data[const.OPEN],
                                    high=data[const.HIGH],
                                    low=data[const.LOW],
                                    close=data[const.CLOSE])])

            peaks = self.algorithms.all_pullback_indicies(ticker)
            closingPeaks = data['Close'][peaks].tolist()
            date_peaks = list(map(lambda x:(x + datetime.timedelta(hours=2)).strftime("%m/%d - %H:%M:%S"),data["Datetime"][peaks]))
            
            fig.add_scatter(y=closingPeaks,x=date_peaks,mode='markers',name="Peaks")
            self.__addTrace(fig,"Ema 200",dates,"200 Ema",data)
            self.__addScatterPlot(fig,ticker_buy_prices,ticker_buy_dates, "Buy signals")
            self.__addScatterPlot(fig,ticker_sell_prices,ticker_sell_dates,"Sell signals")

            fig.update_traces(marker=dict(size=12,      
                                line=dict(width=2,
                                            color='DarkSlateGrey')),
                    selector=dict(mode='markers'))
            fig.update_layout(title=ticker)
            fig.update_xaxes(scaleratio=0.5,tickangle=-70,nticks=16)
            fig.show()
        print("######################################################################")



    def __addScatterPlot(self,onFigure:FigureWidget,attrValues:list, attrDates:list,name):
        onFigure.add_scatter(y=attrValues,x=list(map(lambda x:x.strftime("%m/%d - %H:%M:%S"),attrDates)),mode='markers',name=name)
        
    def __addTrace(self,fig:FigureWidget,attr:str,dates:Series,name,data):
        fig.add_trace(go.Scatter(x=dates,y=data[attr].to_list(),name = name))

    def __dateToString(self,dt:datetime):
        return (dt + datetime.timedelta(hours=2)).strftime("%m/%d - %H:%M:%S")

    