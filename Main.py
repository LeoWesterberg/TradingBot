from BotManagement import BotManagement
from DbManagement import DbManagement
import time


class main:
    def main():
        BotManagement(DbManagement()).reset_bot().run_bot()
    if __name__ == "__main__":
        main()

        