from InitializeBot import InitializeBot
from Test import Test
from Indicators import Indicators
from DbManagement import DbManagement
from MarketAPI import MarketAPI
from Algorithms import Algorithms
from NewAlgorithms import NewAlgorithms
from OrderManagement import OrderManagement
from Credentials import Credentials as Auth


class main:
    def main():

        #INITIALIZING ALL NECESSARY OBJECTS
        api =  MarketAPI() 
        db = DbManagement() 
        ind = Indicators()
        algo = Algorithms(db)
        init = InitializeBot(db,ind,api)
        newAlgorithms = NewAlgorithms(db)
        test:Test = Test(db,newAlgorithms)

        ##########################

        init.reset_bot() 
        #order_manag = OrderManagement()
        print(db.get_nbr_of_rows())
        test.backTest()
        

     
      







    if __name__ == "__main__":
        main()

        