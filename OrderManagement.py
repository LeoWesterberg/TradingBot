import datetime
import hashlib
import pyotp
from avanza import Avanza, TimePeriod, OrderType
from Credentials import Credentials as Auth
from datetime import date


class OrderManagement:
    def __init__(self):
        self.currentOrders = []

        self.totp = pyotp.TOTP(Auth.AVANZA_TOTP_SECRET, digest=hashlib.sha1)
        self.avanza = Avanza({
        'username': Auth.AVANZA_USERNAME,
        'password': Auth.AVANZA_PASSWORD,
        'totpSecret': Auth.AVANZA_TOTP_SECRET
        })

    def buyOrder(self,stockName,volume):
        id = self.avanza.search_for_stock(stockName).get('hits')[0].get('topHits')[0].get('id')
        result = self.avanza.place_order(
            account_id=Auth.AVANZA_ACCOUNT_ID,
            order_book_id=id,
            order_type= OrderType.BUY,
            price=self.avanza.get_stock_info(id).get('lastPrice'),
            valid_until=date.fromisoformat('%s'%(date.today().strftime("%Y-%m-%d"))),
            volume=1)
        if(not result.get('status') == 'ERROR'):
            self.currentOrders.append(result.get('orderId'))

    def sellOrder(self,stockName, price,volume):
        id = self.avanza.search_for_stock(stockName).get('hits')[0].get('topHits')[0].get('id')
        result = self.avanza.place_order(
            account_id=Auth.AVANZA_ACCOUNT_ID,
            order_book_id=id,
            order_type= OrderType.SELL,
            price=price,
            valid_until=TimePeriod.ONE_WEEK,
            volume=volume)
        return result
    
    def getOrders(self):
        return self.avanza.get
