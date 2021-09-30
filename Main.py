from Algorithms import Algorithms
from BotManagement import BotManagement
from DbManagement import DbManagement
class main:
    def main():
        db = DbManagement()
        algorithms = Algorithms(db)
        bot = BotManagement(db, algorithms)
        bot.run_bot()

    if __name__ == "__main__":
        main()

        