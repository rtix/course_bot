import configparser

import telebot

import Models.Mail
from . import helper
from . import util
from .config import *

sets = configparser.ConfigParser()
sets.read(ROOT_DIR + '/settings.cfg')

if not Models.Mail.check_valid(sets['mail']['email']):
    raise Models.Mail.WrongEMail("Неправильный email в файле настроек.")

bot = telebot.TeleBot(sets['bot']['token'])

if sets['optional']['proxy']:
    telebot.apihelper.proxy = {
        'https': sets['optional']['proxy']
    }

email = Models.Mail.Mail(sets['mail']['email'], sets['mail']['password'], sets['optional']['smtp_host'])

botHelper = helper.BotHelper(bot)
