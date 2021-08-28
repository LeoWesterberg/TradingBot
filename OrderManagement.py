import datetime, datetime, hashlib, pyotp, random,pandas as pd

from DbManagement import DbManagement
from pandas.core.frame import DataFrame
from avanza import Avanza, OrderType
from Credentials import Credentials as Auth
from Constants import Constants as const


class OrderManagement:
    
    active_holdings = DataFrame(columns=const.ACTIVE_ORDER_COLUMNS).reset_index(drop=True,inplace=False)
    previous_holdings = DataFrame(columns=const.PREV_ORDER_COLUMNS).reset_index(drop=True,inplace=False)
    active_tickers = dict.fromkeys(const.TICKERS, 0)
        
    def __init__(self,db:DbManagement):
        self.db = db
        self.totp = pyotp.TOTP(Auth.AVANZA_TOTP_SECRET, digest=hashlib.sha1)
        self.avanza = Avanza({
        'username': Auth.AVANZA_USERNAME,
        'password': Auth.AVANZA_PASSWORD,
        'totpSecret': Auth.AVANZA_TOTP_SECRET
        })


    #Returns order id if successful, else ERROR
    def __place_order(self, type:OrderType,  volume:int, ticker:str):
        format_date = datetime.date.today().strftime("%Y-%m-%d")
        result = self.avanza.place_order(
            account_id=Auth.AVANZA_ACCOUNT_ID, order_book_id=self.__get_stock_id(ticker),
            order_type=type, price=self.__get_stock_price(ticker),
            valid_until=datetime.date.fromisoformat(format_date),
            volume=volume) 
        
        order_id = result.get("orderId")

        if(result.get('status') == 'ERROR'):
            print("Error during buying order: %s"%result)
            self.__remove_order(order_id)
            return "ERROR"
        else:
            return order_id



    def __remove_order(self, order_id):
        self.avanza.delete_order(Auth.AVANZA_ACCOUNT_ID,order_id)



    def __get_stock_id(self,ticker):
          return self.avanza.search_for_stock(ticker).get('hits')[0].get('topHits')[0].get('id')



    def __get_stock_price(self,ticker):
        return self.avanza.get_stock_info(self.__get_stock_id(ticker)).get('lastPrice')



    def buy_order(self, stop_loss:float, profit_take:float, ticker:str,test_mode:bool, dt = datetime.datetime.now()) -> None:
        order_id = None

        if(not test_mode):
            result = self.__place_order(OrderType.BUY, 1, ticker)
            if(result == "ERROR"):
                return
            else: 
                order_id = result
                self.active_tickers[ticker] += 1
        else: 
            order_id = random.randint(1,1000)

        buy_price = self.__get_stock_price(ticker) if not test_mode else self.db.get_row_at_date(dt,ticker)[const.CLOSE].tolist()[0]
        order_values = [ticker, order_id, dt, buy_price, stop_loss, profit_take]

        order = DataFrame([order_values], columns=const.ACTIVE_ORDER_COLUMNS)
        self.active_holdings =  self.active_holdings.append(order)



    def sell_order(self,orderId, test_mode:bool, dt = datetime.datetime.now()) -> None:
        order = self.active_holdings.loc[self.active_holdings["Order id"] == orderId]
        ticker = order.at[0,"Ticker"]
        if(not test_mode):
            result = self.__place_order(OrderType.SELL,1,ticker)
            if(result == "ERROR"):
                return
            else:
                self.active_tickers[ticker] -= 1


        sell_price = self.__get_stock_price(ticker) if not test_mode else self.db.get_row_at_date(dt,ticker)[const.CLOSE].tolist()[0]
        extra_columns = DataFrame([[dt, sell_price]],columns=["Datetime Sell","Sell"])
            
        self.previous_holdings =  self.previous_holdings.append(pd.concat([order,extra_columns],axis=1))
        self.active_holdings = self.active_holdings[self.active_holdings["Order id"] != orderId]   
