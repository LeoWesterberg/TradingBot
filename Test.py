import datetime
from pandas.core.frame import DataFrame
import plotly.graph_objects as go
from pandas.core.indexes.datetimes import date_range
from pandas.core.series import Series
from plotly.missing_ipywidgets import FigureWidget 
from DbManagement import DbManagement
from Algorithms import Algorithms
from Constants import Constants as const
from Settings import Settings as st
import random
import pandas as pd



class Test:

    def __init__(self,db:DbManagement, algorithms:Algorithms):
        self.db = db
        self.algorithms = algorithms
        self.order_manag = self.algorithms.order_management
        self.active_holdings = DataFrame(columns=const.ACTIVE_ORDER_COLUMNS).reset_index(drop=True,inplace=False)
        self.previous_holdings = DataFrame(columns=const.PREV_ORDER_COLUMNS).reset_index(drop=True,inplace=False)
        self.nbr_active_tickers = dict.fromkeys(st.TICKERS, 0)
    


    def backTest(self):
        

        start_date = self.db.get_row_at_index(100,st.TICKERS[0]).at[0,const.DATETIME]
        print("Beginning at: %s"%start_date)
        
        end_date = self.db.get_previous_row(st.TICKERS[0]).at[0, const.DATETIME]
        date_times = date_range(start=start_date, end=end_date,freq='%smin'%st.TICKER_INTERVAL)
        
        for date in date_times:
            
            self.test_buy_at_date(date)            
            self.test_sell_at_date(date)

        self.showResult()



    def test_buy_at_date(self, date):
        for ticker in st.TICKERS:
                date_row = self.db.get_row_at_date(date, ticker)
                max_limit = self.nbr_active_tickers[ticker] >= st.TICKER_MAX_HOLDINGS
                if(date_row.size != 0 and self.algorithms.buy_signal(date, ticker) and not max_limit):
                    
                    close = date_row[const.CLOSE].values[0]
                    self.db.get_row_at_date(date, ticker)[const.CLOSE].tolist()[0]
                    order_values = [ticker, random.randint(1,10000), date, close]

                    order = DataFrame([order_values], columns=const.ACTIVE_ORDER_COLUMNS)
                    self.active_holdings =  self.active_holdings.append(order)
                    self.nbr_active_tickers[ticker] += 1

                    print("%s: \t Time =  %s \t Buy = %s"%(ticker, date, "{:.12f}".format(close)))
    


    def test_sell_at_date(self, date):
        for index, row in self.active_holdings.iterrows(): 
                ticker = row.get(0,"Ticker")
                order_id = row["Order id"]
                if(self.db.get_row_at_date(date, ticker).size != 0):
                    current_close = self.db.retrieve_value_dt(date,const.CLOSE, ticker)

                    if(self.algorithms.sell_signal(ticker, date)):
                       
                        order = self.active_holdings.loc[self.active_holdings["Order id"] == order_id]
                        ticker = order.at[0,"Ticker"]
                        
                        sell_price = self.db.get_row_at_date(date,ticker)[const.CLOSE].tolist()[0]
                        extra_columns = DataFrame([[date, sell_price]],columns=["Datetime Sell","Sell"])
                        
                        self.previous_holdings =  self.previous_holdings.append(pd.concat([order,extra_columns],axis=1))
                        self.active_holdings = self.active_holdings[self.active_holdings["Order id"] != order_id]   
                        self.nbr_active_tickers[ticker] -= 1

                        print("%s: \t Time = %s \t Sell = %s  \t diff = %s \t diff(%%): %s"%(ticker,date,"{:.13f}".format(current_close),"{:.13f}".format(current_close - row["Buy"]),"{:.13f}".format(100*current_close/row["Buy"] - 100)))

                  

    def showResult(self):
        print("############################# RESULT #################################")
        for ticker in st.TICKERS:
            ticker_holdings = self.previous_holdings.loc[self.previous_holdings['Ticker'] == ticker]
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

    