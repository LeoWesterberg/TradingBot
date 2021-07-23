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


