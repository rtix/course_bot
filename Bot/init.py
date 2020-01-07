import configparser

import telebot

from Bot.config import ROOT_DIR
from Models import Mail

sets = configparser.ConfigParser()
sets.read(ROOT_DIR + '/settings.cfg')

if not Mail.check_valid(sets['mail']['email']):
    raise Mail.WrongEMail("Неправильный email в файле настроек.")

bot = telebot.TeleBot(sets['bot']['token'])

email = Mail.Mail(sets['mail']['email'], sets['mail']['password'], sets['optional']['smtp_host'])


def bot_init():
    return bot, email
