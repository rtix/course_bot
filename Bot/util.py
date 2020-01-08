import os
import pickle

from Bot.config import USER_MOVEMENT_DIR
from UI.cfg import prevs_dict


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

    new_data['goto'] = prevs_dict[new_data['goto']]
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

    last = data.pop(-1)

    with open(user_dir + str(message_id), 'wb') as file:
        pickle.dump(data, file)

    return last
