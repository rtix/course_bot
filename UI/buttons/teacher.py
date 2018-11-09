"""Кнопки преподователей"""
from json import dumps
from telebot.types import InlineKeyboardButton


# выводит управляемые курсы
manage_list = InlineKeyboardButton(
    'Управление курсами',
    callback_data=dumps(dict(type='menu', command='teach_courses', page=0))
    )

manage = InlineKeyboardButton(
    'Управление',
    callback_data=dumps(dict(type='a_course', command='manage'))
    )

create = InlineKeyboardButton(
    'Создать курс',
    callback_data=dumps(dict(type='new_course', command='NONE'))
    )
