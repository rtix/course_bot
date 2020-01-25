"""Кнопки преподователей"""

from json import dumps

from telebot.types import InlineKeyboardButton

from Models import Course, User


def new_course():
    return InlineKeyboardButton('Создать курс', callback_data=dumps(dict(goto='new_course')))


def manage_list(page=0):
    return InlineKeyboardButton(
        'Управление курсами',
        callback_data=dumps(dict(goto='course_list', type='teach', page=page))
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
            callback_data=dumps(dict(goto='course_owner', course_id=course.id))
        )
        arr.append(button)

    return arr


def manage(course_id):
    return InlineKeyboardButton('Управление', callback_data=dumps(dict(goto='course_owner', course_id=course_id)))


def switch_lock(course_id, lock):
    return InlineKeyboardButton(
        'Закрыть запись' if lock else 'Открыть запись',
        callback_data=dumps(dict(goto='switch_lock', course_id=course_id, lock=lock))
    )


#########################################################################


def delete(id):
    button = InlineKeyboardButton(
            'Удалить курс',
            callback_data=dumps(dict(type='managing', cmd='del_c', id=id))
            )

    return button


def participants(id, prev=None):
    button = InlineKeyboardButton(
            'Участники',
            callback_data=dumps(dict(type='managing', cmd='parts', id=id, prev=prev))
            )

    return button


def tasks(id):
    button = InlineKeyboardButton(
            'Задания',
            callback_data=dumps(dict(type='managing', cmd='task', id=id))
            )

    return button


def task(id_tasks, id_course, back_page=0):
    arr = []

    students = Course.Course(id_course).participants

    for i in id_tasks:
        star = ''
        for student in students:
            if Course.Task(id_course, i).mark(student.id).value is None:
                star = '*'
                break

        button = InlineKeyboardButton(
                Course.Task(id_course, i).name + star,
                callback_data=dumps(dict(type='task', id=id_course, id_t=i, page=back_page))
                )
        arr.append(button)

    return arr


def task_new(id_course):
    button = InlineKeyboardButton(
            "Новое задание",
            callback_data=dumps(dict(type='new_task', id=id_course))
            )

    return button


def attendance(id):
    button = InlineKeyboardButton(
            'Посещаемость',
            callback_data=dumps(dict(type='managing', cmd='attend', id=id))
            )

    return button


def redact(id, prev=None):
    button = InlineKeyboardButton(
            'Редактировать',
            callback_data=dumps(dict(type='managing', cmd='red', id=id, prev=prev))
            )

    return button


def course_out(course_id):
    button = InlineKeyboardButton(
            'Выгрузить данные в .xlsx',
            callback_data=dumps(dict(type='managing', cmd='c_out', id=course_id))
            )

    return button


def user(id_u, id_c, back_page=0):
    arr = []
    for i in id_u:
        name = User.User(i).name
        button = InlineKeyboardButton(
            name,
            callback_data=dumps(dict(type='user', id=id_c, id_u=i, page=back_page))
            )
        arr.append(button)

    return arr


def user_mark(id_u, id_c, id_t):
    task = Course.Task(id_c, id_t)

    arr = []
    for i in id_u:
        name = User.User(i).name if task.mark(i).value is not None else User.User(i).name + '*'
        button = InlineKeyboardButton(
            name,
            callback_data=dumps(dict(type='mark_u_o', id=id_c, id_u=i, id_t=id_t))
            )
        arr.append(button)

    return arr


def remove_user(id_course, id_user):
    button = InlineKeyboardButton(
        'Убрать? Удалить? Отчислить?',
        callback_data=dumps(dict(type='u_act', cmd='rm', id=id_course, id_u=id_user))
        )

    return button


def ban_user(id_course, id_user):
    button = InlineKeyboardButton(
        'Заблокировать',
        callback_data=dumps(dict(type='u_act', cmd='ban', id=id_course, id_u=id_user))
        )

    return button


def confirm(cmd, id_course, id_user=0):
    button = InlineKeyboardButton(
        'Да',
        callback_data=dumps(dict(type='conf', cmd=cmd, id=id_course, id_u=id_user))
        )

    return button


def mark_user(id_course, id_task, page=0):
    button = InlineKeyboardButton(
        'Одному студенту',
        callback_data=dumps(dict(type='mark_o', id=id_course, id_t=id_task, page=page))
        )

    return button


def mark_all(id_course, id_task):
    button = InlineKeyboardButton(
        'Всем студентам',
        callback_data=dumps(dict(type='mark_a', id=id_course, id_t=id_task))
        )

    return button


def class_list(class_ids, course_id, page=0):
    arr = []

    k = 1
    for i in class_ids:
        button = InlineKeyboardButton(
            'Занятие ' + str(k),
            callback_data=dumps(dict(type='classes', id=course_id, id_cl=i, page=page))
            )
        arr.append(button)
        k += 1

    return arr


def class_csv(course_id):
    button = InlineKeyboardButton(
        'Загрузить через .csv',
        callback_data=dumps(dict(type='file', cmd='csv', id=course_id))
        )

    return button


def class_add(course_id):
    button = InlineKeyboardButton(
        'Добавить',
        callback_data=dumps(dict(type='class', cmd='add', id=course_id))
        )

    return button


def class_remove(course_id):
    button = InlineKeyboardButton(
        'Убрать',
        callback_data=dumps(dict(type='class', cmd='rm', id=course_id))
        )

    return button


def user_attendance(users, course_id, class_id):
    arr = []

    cw = Course.Classwork(course_id, class_id)

    for user in users:
        button = InlineKeyboardButton(
            User.User(user.id).name if cw.attendance(user.id).value else User.User(user.id).name + '*',
            callback_data=dumps(dict(type='sw_attend', id=course_id, id_u=user.id, id_cl=class_id))
            )
        arr.append(button)

    return arr


def invert_attendance(course_id, class_id):
    button = InlineKeyboardButton(
            'Инвертировать посещения',
            callback_data=dumps(dict(type='sw_attend', id=course_id, id_cl=class_id))
            )

    return button


def class_xl(course_id):
    button = InlineKeyboardButton(
        'Загрузить через .xl*',
        callback_data=dumps(dict(type='file', cmd='xl_a', id=course_id))
        )

    return button


def task_xl(course_id):
    button = InlineKeyboardButton(
        'Загрузить через .xl*',
        callback_data=dumps(dict(type='file', cmd='xl_t', id=course_id))
        )

    return button


def announce(course_id):
    button = InlineKeyboardButton(
        'Сделать объявление',
        callback_data=dumps(dict(type='managing', cmd='ance', id=course_id))
        )

    return button
