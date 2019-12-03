import operator
import os

from telebot import types


# путь к сообщениям
mespath = 'UI' + os.sep + 'messages' + os.sep


class Paging:
    def __init__(self, data, inpage=5, sort_key=''):
        """
        :param data: Iterable. Список данных.
        :param inpage: int. Кол-во вывода на странице. По умолчанию 5.
        :param sort_key: str. Ключ сортировки.
        """

        self.arr = data
        self.last_page = ((len(data)-1) // inpage)
        self.inpage = inpage

        if sort_key:
            self.arr = sorted(self.arr, key=operator.attrgetter(sort_key))

    def list(self, page):
        """
        :param page: int. Страница вывода.
        :return: list of data in self.arr.
                    Возвращает срез списка 'self.arr' по странице 'page'.
        """

        if page == '':
            page = 0
        if page < 0:
            page = 0
        elif page > self.last_page:
            page = self.last_page

        return [i for i in self.arr[page * self.inpage:(page + 1) * self.inpage]]

    def msg(self, page):
        """
        :param page: int. Текущая страница.
        :return: str. Строка вида "Страница 'page' из 'self.last_page'".
        """

        if page < 0:
            page = 0
        elif page > self.last_page:
            page = self.last_page

        return '\nСтраница {} из {}'.format(page + 1, self.last_page + 1)


def create_markup(*buttons, width=3):
    """
    Создает разметку кнопок '*buttons' с шириной 'width'.

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

    return markup
