import configparser
import time
import traceback

import telebot

sets = configparser.ConfigParser()
sets.read('settings.cfg')

bot = telebot.TeleBot(sets['bot']['token'], threaded=False)


def main():
    while True:
        try:
            bot.polling()
        except Exception:
            print(traceback.print_exc())
            time.sleep(10)


if __name__ == '__main__':
    main()
