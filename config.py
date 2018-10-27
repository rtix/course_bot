from telebot import *

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(types.KeyboardButton(text='Меню'))


# кнопки после /start и /menu
bt_start = types.InlineKeyboardMarkup()
inline_buttons = [['Курсы', 'courses'], ['Мои курсы', 'my_courses']]
bt_start.add(*[types.InlineKeyboardButton(text, callback_data=call) for text, call in inline_buttons])
