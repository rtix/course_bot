"""Общие кнопки, которые есть у всех юзеров"""

from json import dumps, loads

from telebot.types import InlineKeyboardButton

import UI.buttons.confirm
from Bot.util import save_confirm_message
from Models import Course


def back():
    return InlineKeyboardButton('Назад', callback_data=dumps(dict(G='back')))


def paging_forward(data_func, *args):
    """
    Создает кнопку вперед для переключения страницы списка

    :param data_func: func from UI.buttons. Действие, которое будет возвращать кнопка
    :return: InlineKeyboardButton
    """

    G_data = loads(data_func(*args).callback_data)
    G_data['page'] += 1
    text = '>>'

    return InlineKeyboardButton(text, callback_data=dumps(G_data))


def paging_backward(data_func, *args):
    """
    Создает кнопку назад для переключения страницы списка

    :param data_func: func from UI.buttons. Действие, которое будет возвращать кнопка
    :return: InlineKeyboardButton
    """

    G_data = loads(data_func(*args).callback_data)
    G_data['page'] -= 1
    text = '<<'

    return InlineKeyboardButton(text, callback_data=dumps(G_data))


def confirm(what, **kwargs):
    """
    Создаёт кнопку положительного подтверждения дейтсвия, которая вернёт само действие.

    :param what: str. Название действия; должно совпадать с именем функции из этого модуля.
    :param kwargs: Аргументы вызываемой функции.
    :return: InlineKeyboardButton.
    """

    return InlineKeyboardButton('Да', callback_data=dumps(getattr(UI.buttons.confirm, what)(**kwargs)))


def dis_confirm():
    return InlineKeyboardButton('Нет', callback_data=dumps(dict(G='no')))


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


def course_list_of(what, page=0):
    return InlineKeyboardButton(
        'Все курсы' if what == 'all' else 'Мои курсы',
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


####################################################


def show_mark(id_course, prev='menu', page=0):
    button = InlineKeyboardButton(
        'Успеваемость',
        callback_data=dumps(dict(type='perf', id=id_course, page=page, prev=prev))
    )

    return button


def task_list(id_course, prev='menu', page=0):
    button = InlineKeyboardButton(
        'Список заданий',
        callback_data=dumps(dict(type='task_s', id=id_course, page=page, prev=prev))
    )

    return button


def task(id_tasks, id_course, id_user, back_page=0):
    arr = []

    for i in id_tasks:
        task = Course.Task(id_course, i)
        button = InlineKeyboardButton(
            '{}  {}/{}'.format(task.name, task.mark(id_user).value, task.highest_mark),
            callback_data=dumps(dict(type='task_u', id=id_course, id_t=i, page=back_page))
        )
        arr.append(button)

    return arr
