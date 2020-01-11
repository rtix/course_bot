import json
import os
import pickle

from Bot.config import USER_MOVEMENT_DIR


def save_user_movement(user_id, message_id, new_data):
    """
    Сохраняет данные перемещения пользователя по меню.
    Необходимо для корректной работы кнопки "назад".

    :param user_id: Id пользователя
    :param message_id: Id сообщения(меню)
    :param new_data: dict. Данные кнопки
    """

    if not os.path.exists(USER_MOVEMENT_DIR):
        os.mkdir(USER_MOVEMENT_DIR)
    user_dir = USER_MOVEMENT_DIR + '/' + str(user_id) + '/'
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)
    data = []

    if os.path.exists(user_dir + str(message_id)):
        with open(user_dir + str(message_id), 'rb') as file:
            data = pickle.load(file)

        if len(data) > 0 and json.loads(data[-1]).get('page') is not None:
            data.pop()

    data.append(new_data)
    with open(user_dir + str(message_id), 'wb') as file:
        pickle.dump(data, file)


def get_user_movement(user_id, message_id):
    """
    Возвращает данные о последнем посещении пользователя.

    :param user_id: Id пользователя
    :param message_id: Id сообщения(меню)
    :return: dict
    """

    user_dir = USER_MOVEMENT_DIR + '/' + str(user_id) + '/'

    if os.path.exists(user_dir + str(message_id)):
        with open(user_dir + str(message_id), 'rb') as file:
            data = pickle.load(file)
    else:
        raise FileNotFoundError("for user id: {}\nfor message id: {}".format(user_id, message_id))

    try:
        _, prev = data.pop(), data.pop()
    except IndexError:
        prev = 'menu'

    with open(user_dir + str(message_id), 'wb') as file:
        pickle.dump(data, file)

    return prev


def kfubot_callback(func):
    def wrapper(*args):
        save_user_movement(args[0].message.chat.id, args[0].message.message_id, args[0].data)
        func(*args)
    return wrapper
