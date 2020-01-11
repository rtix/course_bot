"""Общие кнопки, которые есть у всех юзеров"""

from json import dumps, loads

from telebot.types import InlineKeyboardButton

from Models import Course

registration = InlineKeyboardButton(
    'Зарегистрироваться',
    callback_data=dumps(dict(type='reg'))
    )


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
            callback_data=dumps(dict(goto='course', id=id_))
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
