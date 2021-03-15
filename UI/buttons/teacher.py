from json import dumps

from telebot.types import InlineKeyboardButton

from Models import Course
import UI.misc


def new_course(lang):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['new_course'],
        callback_data=dumps(dict(G='new_course'))
    )


def manage_list(lang, page=0):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['manage_list'],
        callback_data=dumps(dict(G='course_list', type='teach', page=page))
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
            callback_data=dumps(dict(G='course_owner', c_id=course.id))
        )
        arr.append(button)

    return arr


def manage(c_id, lang):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['manage'],
        callback_data=dumps(dict(G='course_owner', c_id=c_id))
    )


def switch_lock(c_id, lock, lang):
    if lock:
        text = UI.misc.messages[lang]['buttons']['teacher']['switch_lock_close']
    else:
        text = UI.misc.messages[lang]['buttons']['teacher']['switch_lock_open']

    return InlineKeyboardButton(
        text,
        callback_data=dumps(dict(G='switch_lock', c_id=c_id, lock=lock))
    )


def announce(c_id, lang):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['announce'],
        callback_data=dumps(dict(G='announce', c_id=c_id))
    )


def classwork_list(c_id, lang, page=0):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['classwork_list'],
        callback_data=dumps(dict(G='class_list', c_id=c_id, page=page))
    )


def classworks(classworks_list, page=0):
    arr = []
    for cw in classworks_list:
        arr.append(classwork(cw.course_id, cw.number, page))

    return arr


def classwork(c_id, cw_id, page=0):
    return InlineKeyboardButton(
        Course.Classwork(c_id, cw_id).name,
        callback_data=dumps(dict(G='cw', c_id=c_id, cw_id=cw_id, page=page))
    )


def new_classwork(c_id, lang):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['new_classwork'],
        callback_data=dumps(dict(G='new_class', c_id=c_id))
    )


def user_attendance_list(users_list, c_id, cw_id):
    cw = Course.Classwork(c_id, cw_id)
    arr = []
    for usr in users_list:
        arr.append(InlineKeyboardButton(
            usr.name + ' #' if cw.attendance(usr.id).value else usr.name,
            callback_data=dumps(dict(G='attend', u_id=usr.id, c_id=c_id, cw_id=cw_id))
        ))

    return arr


def invert_attendance(c_id, cw_id, lang):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['invert_attendance'],
        callback_data=dumps(dict(G='attend', c_id=c_id, cw_id=cw_id))
    )


def task_list(c_id, lang, page=0):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['task_list'],
        callback_data=dumps(dict(G='task_list', c_id=c_id, page=page))
    )


def tasks(tasks_list, page=0):
    arr = []
    for tsk in tasks_list:
        arr.append(task(tsk.course_id, tsk.number, page))

    return arr


def task(c_id, t_id, page=0):
    return InlineKeyboardButton(
        Course.Task(c_id, t_id).name,
        callback_data=dumps(dict(G='task', c_id=c_id, t_id=t_id, page=page))
    )


def new_task(c_id, lang):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['new_task'],
        callback_data=dumps(dict(G='new_task', c_id=c_id))
    )


def user_tasks_list(users_list, c_id, t_id):
    arr = []
    for usr in users_list:
        arr.append(InlineKeyboardButton(
            usr.name,
            callback_data=dumps(dict(G='do_tsk', u_id=usr.id, c_id=c_id, t_id=t_id))
        ))

    return arr


def user_list(c_id, lang, page=0):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['user_list'],
        callback_data=dumps(dict(G='user_list', c_id=c_id, page=page))
    )


def users(users_list, c_id):
    arr = []
    for usr in users_list:
        arr.append(InlineKeyboardButton(
            usr.name,
            callback_data=dumps(dict(G='usr_mng', u_id=usr.id, c_id=c_id))
        ))

    return arr


def kick_user(c_id, u_id):
    return InlineKeyboardButton('Отчислить', callback_data=dumps(dict(G='kick', c_id=c_id, u_id=u_id)))


def change_cw_date(c_id, cw_id, lang):
    return InlineKeyboardButton(
        UI.misc.messages[lang]['buttons']['teacher']['change_cw_data'],
        callback_data=dumps(dict(G='cw_date', c_id=c_id, cw_id=cw_id))
    )
