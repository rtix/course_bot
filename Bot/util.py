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

    move_dir = os.path.join(USER_MOVEMENT_DIR, str(user_id))
    if not os.path.exists(move_dir):
        os.makedirs(move_dir)
    move_file = os.path.join(USER_MOVEMENT_DIR, str(user_id), str(message_id))

    data = []
    if os.path.exists(move_file):
        with open(move_file, 'rb') as file:
            data = pickle.load(file)

        if (new_data.get('page') is not None) and (len(data) > 0) and (data[-1].get('page') is not None):
            data.pop()

    data.append(new_data)
    with open(move_file, 'wb') as file:
        pickle.dump(data, file)


def get_user_movement(user_id, message_id):
    """
    Возвращает данные о последнем посещении пользователя.

    :param user_id: Id пользователя
    :param message_id: Id сообщения(меню)
    :return: dict
    """

    move_file = os.path.join(USER_MOVEMENT_DIR, str(user_id), str(message_id))

    if os.path.exists(move_file):
        with open(move_file, 'rb') as file:
            data = pickle.load(file)
    else:
        raise FileNotFoundError("Movement file: for user id: {}\nfor message id: {}".format(user_id, message_id))

    try:
        _, prev = data.pop(), data.pop()
    except IndexError:
        prev = 'menu'

    with open(move_file, 'wb') as file:
        pickle.dump(data, file)

    return prev


def move_menu_info(old, new, user_id):
    move_dir = os.path.join(USER_MOVEMENT_DIR, str(user_id))
    old_file = os.path.join(move_dir, str(old))
    new_file = os.path.join(move_dir, str(new))

    if os.path.exists(old_file):
        if os.path.exists(new_file):
            os.remove(new_file)

        os.rename(old_file, new_file)
    else:
        raise FileNotFoundError("Movement file: for user id: {}\nfor message id: {}".format(user_id, old))


def save_confirm_message(text, user_id, message_id):
    confirm_dir = os.path.join(USER_MOVEMENT_DIR, str(user_id), 'confirm')

    if not os.path.exists(confirm_dir):
        os.makedirs(confirm_dir)

    with open(os.path.join(confirm_dir, str(message_id)), 'w') as file:
        file.write(text)


def get_confirm_message(user_id, message_id):
    confirm_file = os.path.join(USER_MOVEMENT_DIR, str(user_id), 'confirm', str(message_id))

    if os.path.exists(confirm_file):
        with open(confirm_file, 'r') as file:
            text = file.read()
        os.remove(confirm_file)
    else:
        raise FileNotFoundError("Confirm file: user id: {}\nfor message id: {}".format(user_id, message_id))

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
