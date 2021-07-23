import hashlib
import pyotp
from avanza import Avanza, TimePeriod, OrderType
from OrderCredentials import OrderCredentials as Auth
from datetime import date


class OrderManagement:
    totp = pyotp.TOTP(Auth.avanza_totpSecret, digest=hashlib.sha1)
    print(totp)
    avanza = Avanza({
    'username': Auth.avanza_username,
    'password': Auth.avanza_password,
    'totpSecret': Auth.avanza_totpSecret
    })
    print(avanza.get_overview())
    avanza.get_stock_info('AAPL')
    
    def placeOrder(self):
        result = self.avanza.place_order(
            account_id=Auth.avanza_account_id,
            order_book_id='XXXXXX',
            order_type= OrderType.BUY,
            price=13.37,
            valid_until=date
            .fromisoformat('2011-11-11'),
            volume=42)
