from telebot import types

# кол-во записей на странице
inpage = 5


class Paging:
    def __init__(self, id):
        self.arr = id
        self.last_page = (len(id) // inpage)

    def list(self, page):
        """Выводит определенное кол-во кнопок.
        За это кол-во отвечает переменная inpage."""
        return [i for i in self.arr[page*inpage:(page+1)*inpage]]

    def msg(self, page):
        return '\nСтраница {} из {}'.format(page + 1, self.last_page + 1)


def create_markup(*buttons, width=3):
    """Создает разметку с шириной width(по умолчанию = 3).
    Берет на вход переменное количество списка кнопок.
    При разделении списка выведет кнопки на разных строках.
    Т.е. [b1, b2] будут на одной;
         [b1], [b2] будут на разных.
    При условии, width >= 2."""
    markup = types.InlineKeyboardMarkup(row_width=width)
    for button in buttons:
        markup.add(*button)

    return markup
