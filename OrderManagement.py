import datetime
import hashlib
import random
from pandas.core.frame import DataFrame
import pyotp
from Constants import Constants as const
from avanza import Avanza, OrderType
from Credentials import Credentials as Auth
from datetime import date
import datetime
import pandas as pd

class OrderManagement:
    

    def __init__(self):
        self.ORDER_COLUMNS =  ["Ticker","Order id","Stock","Datetime Buy", "Buy", "Stop loss", "Profit take"]
        self.current_holdings = DataFrame(columns=self.ORDER_COLUMNS)
        self.previous_holdings = DataFrame(columns=self.ORDER_COLUMNS + ["Datetime Sell","Sell"])

        self.totp = pyotp.TOTP(Auth.AVANZA_TOTP_SECRET, digest=hashlib.sha1)
        self.avanza = Avanza({
        'username': Auth.AVANZA_USERNAME,
        'password': Auth.AVANZA_PASSWORD,
        'totpSecret': Auth.AVANZA_TOTP_SECRET
        })



    def __place_order(self, type:OrderType,  volume:int, ticker:str):
        return self.avanza.place_order(
            account_id=Auth.AVANZA_ACCOUNT_ID,
            order_book_id=self.__get_stock_id(ticker),
            order_type= type,
            price=self.get_latest_stock_price(),
            valid_until=date.fromisoformat('%s'%(date.today().strftime("%Y-%m-%d"))),
            volume=volume) 



    def buy_order(self, stop_loss:float, profit_take:float, ticker:str):
       # result = self.__place_order(OrderType.BUY, 1)
       # #if(result.get('status') == 'ERROR'):
        #    self.avanza.delete_order(Auth.AVANZA_ACCOUNT_ID,result.get('orderId'))
        #    return "Failure"
       # else: 
            order_id:int = random.randint(3, 90) #result.get("orderId")
            buy_price = self.get_latest_stock_price(ticker)
            dt = datetime.datetime.now()
            order = DataFrame([[ticker, order_id, ticker, dt, buy_price, stop_loss, profit_take]], columns=self.ORDER_COLUMNS)
            self.current_holdings =  self.current_holdings.append(order)
            return "Success"



    def sell_order(self,orderId):
       # result = self.__place_order(OrderType.SELL,1)

       # if(result.get('status') == 'ERROR'):
       #     self.avanza.delete_order(Auth.AVANZA_ACCOUNT_ID,result.get('orderId'))
      #      return "Failure"
      #  else: 
        order = self.current_holdings.loc[self.current_holdings["Order id"] == orderId]
        
        sell_price = self.get_latest_stock_price(order.at[0,"Ticker"])
        sell_df = DataFrame([[datetime.datetime.now(), sell_price]],columns=["Datetime Sell","Sell"])
        self.previous_holdings =  self.previous_holdings.append(pd.concat([order,sell_df],axis=1))
        self.current_holdings = self.current_holdings[self.current_holdings["Order id"] != orderId]   
        return "Success"



    def __get_stock_id(self,ticker):
        return self.avanza.search_for_stock(ticker).get('hits')[0].get('topHits')[0].get('id')



    def get_latest_stock_price(self,ticker):
        return self.avanza.get_stock_info(self.__get_stock_id(ticker)).get('lastPrice')



    def delete_pending_order(self,order_id):
        self.avanza.delete_order(Auth.AVANZA_ACCOUNT_ID,order_id)
    
   
