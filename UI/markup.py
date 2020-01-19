from telebot import types

from UI.buttons import common as cbt


def create(*buttons, width=3, include_back=True):
    """
    Создает разметку кнопок '*buttons' с шириной 'width'.

    :param include_back: bool. Влияет на наличие кнопки "назад"
    :param buttons: lists of InlineKeyboardMarkup. Списки из 'InlineKeyboardMarkup'.
                    При разделении списка выведет кнопки на разных строках.
                    Т.е. '[b1, b2]' будут на одной;
                        '[b1], [b2]' будут на разных.
    :param width: int. Кол-во кнопок на одной строке. По умолчанию 3.
    :return: InlineKeyboardMarkup. Возвращает разметку кнопок.
    """

    markup = types.InlineKeyboardMarkup(row_width=width)
    for button in buttons:
        markup.add(*button)
    if include_back:
        markup.add(cbt.back())

    return markup


def create_listed(list, list_type, width=3, *args):
    """
    Создает клавиатуру со списком, разделенный на страницы.

    :param list: list of InlineKeyboardButton of list_type. Список перечисляемого
    :param list_type: func from UI.buttons. Тип списка
    :param width: int. Кол-во кнопок на одной строке. По умолчанию 3
    :param args: list. Аргументы для функции "list_type"
    :return: InlineKeyboardMarkup. Возвращает разметку кнопок
    """

    return create(*[[i] for i in list],
                  [cbt.paging_backward(list_type, *args), cbt.paging_forward(list_type, *args)],
                  width=width
                  )


def create_confirm(call_data):
    """
    Создает клавиатуру для подтверждения действия.

    :param call_data: dict. Информация кнопки, которая будет использована в последующем действии.
    :return: InlineKeyboardMarkup.
    """

    tmp = call_data.copy()
    tmp.pop('goto'), tmp.pop('what')
    return create([cbt.confirm(call_data['what'], **tmp), cbt.dis_confirm()], include_back=False)
