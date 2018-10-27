import telebot
import bot_token
from config import *

bot = telebot.TeleBot(bot_token.token)


@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, "Я пожилой бот", reply_markup=bt_start)


@bot.message_handler()
def command(message):
	bot.send_message(message.chat.id, "Шо?")


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
	if call.data == 'courses':
		bot.send_message(call.message.chat.id, 'dadaya')


bot.polling()
