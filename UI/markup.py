from telebot.types import InlineKeyboardMarkup

from UI import buttons


def create(lang, *btns, width=3, include_back=True):
    """
    Создает разметку кнопок '*buttons' с шириной 'width'.

    :param lang: str. Язык пользователя
    :param include_back: bool. Влияет на наличие кнопки "назад"
    :param btns: lists of InlineKeyboardMarkup. Списки из 'InlineKeyboardMarkup'.
                    При разделении списка выведет кнопки на разных строках.
                    Т.е. '[b1, b2]' будут на одной;
                        '[b1], [b2]' будут на разных.
    :param width: int. Кол-во кнопок на одной строке. По умолчанию 3.
    :return: InlineKeyboardMarkup. Возвращает разметку кнопок.
    """

    markup = InlineKeyboardMarkup(row_width=width)
    for btn in btns:
        markup.add(*btn)
    if include_back:
        markup.add(buttons.common.back(lang))

    return markup


def create_listed(lang, lst, list_type, *args):
    """
    Создает клавиатуру со списком, разделенный на страницы.

    :param lang: str. Язык пользователя
    :param lst: list of InlineKeyboardButton of list_type. Список перечисляемого
    :param list_type: func from UI.buttons. Тип списка
    :param args: list. Аргументы для функции "list_type"
    :return: InlineKeyboardMarkup. Возвращает разметку кнопок
    """

    return create(
        lang,
        *[[i] for i in lst],
        [buttons.common.paging_backward(list_type, *args), buttons.common.paging_forward(list_type, *args)]
    )


def create_confirm(lang, call_data):
    """
    Создает клавиатуру для подтверждения действия.

    :param lang: str. Язык пользователя
    :param call_data: dict. Информация кнопки, которая будет использована в последующем действии.
    :return: InlineKeyboardMarkup.
    """

    tmp = call_data.copy()
    tmp.pop('G'), tmp.pop('what')
    return create(
        lang,
        [buttons.common.confirm(call_data['what'], lang, **tmp), buttons.common.dis_confirm(lang)],
        include_back=False
    )


def add_before_back(markup, button):
    markup.add(button)
    markup.keyboard[-1], markup.keyboard[-2] = markup.keyboard[-2], markup.keyboard[-1]
    return markup
