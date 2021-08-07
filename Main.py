from OrderManagement import OrderManagement
from Algorithms import Algorithms
from BotManagement import BotManagement
from DbManagement import DbManagement
from OrderManagement import OrderManagement
from Test import Test
class main:
    def main():
        db = DbManagement()
        algorithms = Algorithms(db)
        bot = BotManagement(db, algorithms)
        bot.run_bot()

        #test = Test(db,algorithms)
        #test.backTest()



    if __name__ == "__main__":
        main()

        