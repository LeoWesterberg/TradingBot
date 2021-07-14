from InitializeBot import InitializeBot
from Test import Test
from Indicators import Indicators
from DbManagement import DbManagement
from MarketAPI import MarketAPI
from Algorithms import Algorithms

class main:
    def main():

        #INITIALIZING ALL NECESSARY OBJECTS
        api =  MarketAPI() 
        db = DbManagement(api) 
        ind = Indicators()
        algo = Algorithms(db)
        test:Test = Test(db,algo)
        init = InitializeBot(db,ind,api)
        ##########################

        init.resetBot()
        #test.backTest()
        

       
      







    if __name__ == "__main__":
        main()

        