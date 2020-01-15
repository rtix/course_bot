"""Общие кнопки, которые есть у всех юзеров"""

from json import dumps, loads

from telebot.types import InlineKeyboardButton

from Bot.util import save_confirm_message
from Models import Course
from UI import buttons


def back():
    return InlineKeyboardButton('Назад', callback_data=dumps(dict(goto='back')))


def paging_forward(data_func, *args):
    """
    Создает кнопку вперед для переключения страницы списка

    :param data_func: func from UI.buttons. Действие, которое будет возвращать кнопка
    :return: InlineKeyboardButton
    """

    goto_data = loads(data_func(*args).callback_data)
    goto_data['page'] += 1
    text = '>>'

    return InlineKeyboardButton(text, callback_data=dumps(goto_data))


def paging_backward(data_func, *args):
    """
    Создает кнопку назад для переключения страницы списка

    :param data_func: func from UI.buttons. Действие, которое будет возвращать кнопка
    :return: InlineKeyboardButton
    """

    goto_data = loads(data_func(*args).callback_data)
    goto_data['page'] -= 1
    text = '<<'

    return InlineKeyboardButton(text, callback_data=dumps(goto_data))


def confirm(what, **kwargs):
    """
    Создаёт кнопку положительного подтверждения дейтсвия, которая вернёт само действие.

    :param what: str. Название действия; должно совпадать с именем функции из этого модуля.
    :param kwargs: Аргументы вызываемой функции.
    :return: InlineKeyboardButton.
    """

    return InlineKeyboardButton('Да', callback_data=dumps(getattr(buttons.confirm, what)(**kwargs)))


def dis_confirm():
    return InlineKeyboardButton('Нет', callback_data=dumps(dict(goto='no')))


def course_list_of(what, page=0):
    return InlineKeyboardButton(
        'Все курсы' if what == 'all' else 'Мои курсы',
        callback_data=dumps(dict(goto='course_list', type=what, page=page))
    )


def course(course_ids):
    """
    Берет на вход список 'id' и создает список кнопок с айди курса.

    :param course_ids: list. Список айди курсов.
    :return: list of InlineKeyboardButton. Возвращает список кнопок с айди курсов.
    """

    arr = []
    for id_ in course_ids:
        button = InlineKeyboardButton(
            Course.Course(id_).name,
            callback_data=dumps(dict(goto='course', course_id=id_))
        )
        arr.append(button)

    return arr


def confirm_enroll(course_id, confirm_text, user_id, message_id):
    save_confirm_message(confirm_text, user_id, message_id)
    return InlineKeyboardButton(
        'Записаться',
        callback_data=dumps(dict(goto='confirm', what='enroll', course_id=course_id))
    )


def confirm_leave(course_id, confirm_text, user_id, message_id):
    save_confirm_message(confirm_text, user_id, message_id)
    return InlineKeyboardButton(
        'Покинуть курс',
        callback_data=dumps(dict(goto='confirm', what='leave', course_id=course_id))
    )


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
