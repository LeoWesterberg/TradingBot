from BotManagement import BotManagement
from DbManagement import DbManagement
from NewAlgorithms import NewAlgorithms
from Constants import Constants as const
import time


class main:
    def main():
        db_manag = DbManagement() 
        bot_manag = BotManagement()
        newAlgorithms = NewAlgorithms(db_manag)

        bot_manag.reset_bot()

        
        

       # order_manag = OrderManagement()
       # order_manag.avanza.get_inspiration_lists
        #print(order_manag.buy_order(1,1))
        #print(db.get_nbr_of_rows())
    
        

     
      







    if __name__ == "__main__":
        main()

        