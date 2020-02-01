"""Общие кнопки, которые есть у всех юзеров"""

from json import dumps, loads

from telebot.types import InlineKeyboardButton

import UI.buttons.confirm
import UI.misc
from Bot.util import save_confirm_message


def back(lang):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['common']['back'],
        callback_data=dumps(dict(G='back'))
    )


def paging_forward(data_func, *args):
    """
    Создает кнопку вперед для переключения страницы списка

    :param data_func: func from UI.buttons. Действие, которое будет возвращать кнопка
    :return: InlineKeyboardButton
    """

    g_data = loads(data_func(*args).callback_data)
    g_data['page'] += 1
    text = '>>'

    return InlineKeyboardButton(text, callback_data=dumps(g_data))


def paging_backward(data_func, *args):
    """
    Создает кнопку назад для переключения страницы списка

    :param data_func: func from UI.buttons. Действие, которое будет возвращать кнопка
    :return: InlineKeyboardButton
    """

    g_data = loads(data_func(*args).callback_data)
    g_data['page'] -= 1
    text = '<<'

    return InlineKeyboardButton(text, callback_data=dumps(g_data))


def confirm(what, lang, **kwargs):
    """
    Создаёт кнопку положительного подтверждения дейтсвия, которая вернёт само действие.

    :param what: str. Название действия; должно совпадать с именем функции из этого модуля.
    :param lang: str. Язык пользователя.
    :param kwargs: Аргументы вызываемой функции.
    :return: InlineKeyboardButton.
    """

    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['common']['confirm'],
        callback_data=dumps(getattr(UI.buttons.confirm, what)(**kwargs))
    )


def dis_confirm(lang):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['common']['dis_confirm'],
        callback_data=dumps(dict(G='no'))
    )


def confirm_action(action, button_text, confirm_text, user_id, message_id, **kwargs):
    """
    Создает кнопку, которая ведет к подтверждению действия.

    :param button_text: str. Текст кнопки.
    :param confirm_text: str. Текст кнопки.
    :param action: str; function name. Название действия.
    :param user_id: int. id пользователя.
    :param message_id: int. id сообщения(меню).
    :param kwargs: аргументы для дальнейшего действия при подтверждении.
    :return: InlineKeyboardButton.
    """

    save_confirm_message(confirm_text, user_id, message_id)
    return InlineKeyboardButton(
        button_text,
        callback_data=dumps(dict(G='C', what=action, **kwargs))
    )


def course_list_of(what, lang, page=0):
    if what == 'all':
        text = UI.misc.messages[lang]['buttons']['common']['all']
    else:
        text = UI.misc.messages[lang]['buttons']['common']['my']

    return InlineKeyboardButton(
        text,
        callback_data=dumps(dict(G='course_list', type=what, page=page))
    )


def courses(courses_list):
    """
    Берет на вход список курсов и создает список кнопок с айди курса.

    :param courses_list: iterable. Список курсов.
    :return: list of InlineKeyboardButton. Возвращает список кнопок с айди курсов.
    """

    arr = []
    for course in courses_list:
        button = InlineKeyboardButton(
            course.name,
            callback_data=dumps(dict(G='course', c_id=course.id))
        )
        arr.append(button)

    return arr


def task_list(c_id, lang, page=0):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['common']['task_list'],
        callback_data=dumps(dict(G='st_task_list', c_id=c_id, page=page))
    )


def tasks(tasks_list):
    arr = []
    for t in tasks_list:
        arr.append(InlineKeyboardButton(t.name, callback_data=dumps(dict(G='st_tsk', c_id=t.course_id, t_id=t.number))))

    return arr
