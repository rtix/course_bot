from Bot.init import bot_init


def start():
    bot, mailer = bot_init()
    bot.polling(none_stop=True)
