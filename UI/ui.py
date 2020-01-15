import operator
import time


class Paging:
    def __init__(self, data, inpage=5, sort_key=''):
        """
        :param data: Iterable. Список данных.
        :param inpage: int. Кол-во вывода на странице. По умолчанию 5.
        :param sort_key: str. Ключ сортировки.
        """

        self.arr = data
        self.last_page = ((len(data) - 1) // inpage)
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

        return [i for i in self.arr[(page * self.inpage):((page + 1) * self.inpage)]]

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


def to_dtime(utime):
    return time.strftime("%d %b %Y", time.localtime(float(utime))) if utime else None
