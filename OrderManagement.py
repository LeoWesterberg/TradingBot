import datetime
import hashlib
import pyotp
from avanza import Avanza, TimePeriod, OrderType
from Credentials import Credentials as Auth
from datetime import date
import datetime

class Order:
    sell_closing:float
    sell_date:datetime
    active:True
    second_profit_take = False

    def __init__(self,buy_date:datetime, buy_closing:float, stop_loss:float, profit_take:float, stop_loss_mid:float):
        self.buy_date = buy_date
        self.buy_closing = buy_closing
        self.stop_loss = stop_loss
        self.profit_take = profit_take
        self.stop_loss_mid = stop_loss_mid




class OrderManagement:
    def __init__(self):
        self.totp = pyotp.TOTP(Auth.AVANZA_TOTP_SECRET, digest=hashlib.sha1)
        self.avanza = Avanza({
        'username': Auth.AVANZA_USERNAME,
        'password': Auth.AVANZA_PASSWORD,
        'totpSecret': Auth.AVANZA_TOTP_SECRET
        })



    def __place_order(self, type:OrderType, stock_name, volume:int):
        self.avanza.place_order(
            account_id=Auth.AVANZA_ACCOUNT_ID,
            order_book_id=self.get_stock_id(stock_name),
            order_type= type,
            price=self.get_latest_stock_price(stock_name),
            valid_until=date.fromisoformat('%s'%(date.today().strftime("%Y-%m-%d"))),
            volume=volume)



    def buy_order(self,stock_name,volume):
        result = self.__place_order(OrderType.BUY, stock_name, volume)

        if(result.get('status') == 'ERROR'):
            self.avanza.delete_order(Auth.AVANZA_ACCOUNT_ID,result.get('orderId'))



    def sell_order(self,stock_name,volume):
        result = self.__place_order(OrderType.SELL, stock_name, volume)

        if(result.get('status') == 'ERROR'):
            self.avanza.delete_order(Auth.AVANZA_ACCOUNT_ID,result.get('orderId'))



    def get_stock_id(self,stock_name):
        return self.avanza.search_for_stock(stock_name).get('hits')[0].get('topHits')[0].get('id')



    def get_latest_stock_price(self,stock_name):
        return self.avanza.get_stock_info(self.get_stock_id(stock_name)).get('lastPrice')



    def delete_pending_order(self,order_id):
        self.avanza.delete_order(Auth.AVANZA_ACCOUNT_ID,order_id)
    
   
