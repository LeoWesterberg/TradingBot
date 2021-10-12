from BotManagement import BotManagement
class main:
    def main(self):
    
        bot = BotManagement()
        bot.run_bot()

    if __name__ == "__main__":
        try:
            main()
        except KeyboardInterrupt:
            print("Exiting program")
        