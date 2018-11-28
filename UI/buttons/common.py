"""Общие кнопки, которые есть у всех юзеров"""

from json import dumps

from telebot.types import InlineKeyboardButton

registration = InlineKeyboardButton(
    'Зарегистрироваться',
    callback_data=dumps(dict(type='reg'))
    )

# выводит все курсы
all_courses = InlineKeyboardButton(
    'Все курсы',
    callback_data=dumps(dict(type='menu', command='all_courses', page=0))
    )

# выводит курсы, на которые записан
my_courses = InlineKeyboardButton(
    'Мои курсы',
    callback_data=dumps(dict(type='menu', command='my_courses', page=0))
    )


def course(id, prev='NONE', back_page=0):
    """
    Берет на вход список 'id' и создает список кнопок с айди курса.

    :param id: list of int. Список айди курсов.
    :param prev: str. Меню в которое произойдет при нажатии кнопки "Назад".
    :param back_page: int. Страница для возврата. Чтобы, если зашел на курс из страницы 3,
                        на ту же страницу и возвратился.
    :return: list of InlineKeyboardButton. Возвращает список кнопок с айди курсов.
    """

    arr = []
    for i in id:
        # тут надо будеть делать запрос
        name = 'курс' + str(i)
        button = InlineKeyboardButton(
            name,
            callback_data=dumps(dict(type='courses', command=i, prev=prev, page=back_page))
            )
        arr.append(button)

    return arr


enroll = InlineKeyboardButton(
    'Записаться',
    callback_data=dumps(dict(type='a_course', command='enroll'))
    )

leave = InlineKeyboardButton(
    'Отписаться',
    callback_data=dumps(dict(type='course_enrolled', command='leave'))
    )


# кнопка назад по аргументу to - куда возвращаться
def back(to, back_page=0):
    button = InlineKeyboardButton(
        'Назад',
        callback_data=dumps(dict(type='back', back=to, page=back_page))
        )

    return button


# кнопка вперед
def forward(page, cmd):
    button = InlineKeyboardButton(
        '>',
        callback_data=dumps(dict(type='menu', command=cmd, page=page + 1))
        )

    return button


def backward(page, cmd):
    button = InlineKeyboardButton(
        '<',
        callback_data=dumps(dict(type='menu', command=cmd, page=page - 1))
        )

    return button
