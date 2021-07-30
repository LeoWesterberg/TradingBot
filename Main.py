from Algorithms import Algorithms
from BotManagement import BotManagement
from DbManagement import DbManagement
from Test import Test
class main:
    def main():
        db = DbManagement()
        algorithms = Algorithms(db)
        BotManagement(db, algorithms).reset_bot().run_bot()
       # test = Test(db,algorithms)
       # test.backTest()

    if __name__ == "__main__":
        main()

        