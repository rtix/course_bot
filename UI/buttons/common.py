"""Общие кнопки, которые есть у всех юзеров"""

from json import dumps

from telebot.types import InlineKeyboardButton

import Course

registration = InlineKeyboardButton(
    'Зарегистрироваться',
    callback_data=dumps(dict(type='reg'))
    )

# выводит все курсы
all_courses = InlineKeyboardButton(
    'Все курсы',
    callback_data=dumps(dict(type='menu', cmd='all_courses', page=0))
    )

# выводит курсы, на которые записан
my_courses = InlineKeyboardButton(
    'Мои курсы',
    callback_data=dumps(dict(type='menu', cmd='my_courses', page=0))
    )


def course(id, prev='', back_page=0):
    """
    Берет на вход список 'id' и создает список кнопок с айди курса.

    :param id: list of int. Список айди курсов.
    :param prev: str. Меню в которое попадет при нажатии кнопки "Назад".
    :param back_page: int. Страница для возврата. Чтобы, если зашел на курс из страницы 3,
                        на ту же страницу и возвратился.
    :return: list of InlineKeyboardButton. Возвращает список кнопок с айди курсов.
    """

    arr = []
    for i in id:
        name = Course.Course(i).name
        button = InlineKeyboardButton(
            name,
            callback_data=dumps(dict(type='courses', id=i, prev=prev, page=back_page))
            )
        arr.append(button)

    return arr


def enroll(id, prev=None):
    button = InlineKeyboardButton(
        'Записаться',
        callback_data=dumps(dict(type='c_act', cmd='enroll', id=id, prev=prev))
        )

    return button


def leave(id, prev=None):
    button = InlineKeyboardButton(
        'Отписаться',
        callback_data=dumps(dict(type='c_act', cmd='leave', id=id, prev=prev))
            )

    return button


# кнопка назад по аргументу to - куда возвращаться
def back(to, extra='', extra1=''):
    button = InlineKeyboardButton(
        'Назад',
        callback_data=dumps(dict(type='back', back=to, ex=extra, ex1=extra1))
        )

    return button


# кнопка вперед
def forward(type, page, cmd, id=None):
    button = InlineKeyboardButton(
        '>',
        callback_data=dumps(dict(type=type, cmd=cmd, page=page + 1, id=id))
        )

    return button


def backward(type, page, cmd, id=None):
    button = InlineKeyboardButton(
        '<',
        callback_data=dumps(dict(type=type, cmd=cmd, page=page - 1, id=id))
        )

    return button


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
