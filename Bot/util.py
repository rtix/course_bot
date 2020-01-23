import json
import os
import pickle

from .config import USER_MOVEMENT_DIR


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
    path = user_dir + str(message_id)
    data = []

    if os.path.exists(path):
        with open(path, 'rb') as file:
            data = pickle.load(file)

        if (new_data.get('page') is not None) and (len(data) > 0) and (data[-1].get('page') is not None):
            data.pop()

    data.append(new_data)
    with open(path, 'wb') as file:
        pickle.dump(data, file)


def get_user_movement(user_id, message_id):
    """
    Возвращает данные о последнем посещении пользователя.

    :param user_id: Id пользователя
    :param message_id: Id сообщения(меню)
    :return: dict
    """

    user_dir = USER_MOVEMENT_DIR + '/' + str(user_id) + '/'
    path = user_dir + str(message_id)

    if os.path.exists(path):
        with open(path, 'rb') as file:
            data = pickle.load(file)
    else:
        raise FileNotFoundError("Movement file: for user id: {}\nfor message id: {}".format(user_id, message_id))

    try:
        _, prev = data.pop(), data.pop()
    except IndexError:
        prev = 'menu'

    with open(path, 'wb') as file:
        pickle.dump(data, file)

    return prev


def save_confirm_message(text, user_id, message_id):
    if not os.path.exists(USER_MOVEMENT_DIR):
        os.mkdir(USER_MOVEMENT_DIR)
    user_dir = USER_MOVEMENT_DIR + '/' + str(user_id) + '/'
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)
    confirm_dir = user_dir + 'confirm/'
    if not os.path.exists(confirm_dir):
        os.mkdir(confirm_dir)

    with open(confirm_dir + str(message_id), 'w') as file:
        file.write(text)


def get_confirm_message(user_id, message_id):
    if not os.path.exists(USER_MOVEMENT_DIR):
        os.mkdir(USER_MOVEMENT_DIR)
    user_dir = USER_MOVEMENT_DIR + '/' + str(user_id) + '/'
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)
    confirm_dir = user_dir + 'confirm/'
    if not os.path.exists(confirm_dir):
        os.mkdir(confirm_dir)
    path = confirm_dir + str(message_id)

    if os.path.exists(path):
        with open(path, 'r') as file:
            text = file.read()
    else:
        raise FileNotFoundError("Confirm file: user id: {}\nfor message id: {}".format(user_id, message_id))

    os.remove(path)
    return text


def kfubot_callback(func):
    def wrapper(call):
        if type(call.data) is str:
            call.data = json.loads(call.data)
        save_user_movement(call.message.chat.id, call.message.message_id, call.data)
        func(call)

    return wrapper


def goto(data):
    return json.loads(data)['goto']
