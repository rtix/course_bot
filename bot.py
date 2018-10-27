import telebot
import config


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands='start')
def start(message):
	bot.send_message(message.chat.id, "Я пожилой бот")


bot.polling()
