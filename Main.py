from InitializeBot import InitializeBot
from Test import Test
from Indicators import Indicators
from DbManagement import DbManagement
from MarketAPI import MarketAPI
from Algorithms import Algorithms
from NewAlgorithms import NewAlgorithms


class main:
    def main():

        #INITIALIZING ALL NECESSARY OBJECTS
        api =  MarketAPI() 
        db = DbManagement(api) 
        ind = Indicators()
        algo = Algorithms(db)
        init = InitializeBot(db,ind,api)
        newAlgorithms = NewAlgorithms(db)
        test:Test = Test(db,newAlgorithms)

        ##########################
        init.resetBot()
        test.backTest()
        

       
      







    if __name__ == "__main__":
        main()

        