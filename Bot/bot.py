from Bot.init import bot_init

bot, mailer = bot_init()


def go():
    bot.polling(none_stop=True)
