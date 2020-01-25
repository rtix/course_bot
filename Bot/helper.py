import re
import traceback

from UI.misc import messages
from Bot import util


class BotHelper:
    __danger_symbols = ('*', '_', '`')

    def __init__(self, bot):
        self.__bot = bot
        self.__markdown_regex = re.compile(r'\*.+?\*|_.+?_|`.+?`', re.IGNORECASE)

    def send_mes(self, text, chat_id, *, markup=None):
        return self.__bot.send_message(
            text=BotHelper.remove_danger(text, False),
            chat_id=chat_id,
            reply_markup=markup,
            parse_mode='Markdown' if self.__markdown_regex.search(text) else None
        )

    def edit_mes(self, text, call, *, markup=None):
        return self.__bot.edit_message_text(
            text=BotHelper.remove_danger(text, False),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown' if self.__markdown_regex.search(text) else None
        )

    def del_mes(self, *, chat_id=None, message_id=None, call=None):
        if call:
            return self.__bot.delete_message(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        else:
            return self.__bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )

    def get_back(self, call):
        call.data = self.get_from_disc(util.get_user_movement, call=call)
        return call.data if (call.data == 'menu') or (not call.data) else call.data['goto']

    @staticmethod
    def remove_danger(text, user_text=True):
        for s in BotHelper.__danger_symbols:
            if text.count(s) % 2:
                if not user_text:
                    print('Markdown parse error in text:\n' + text)

                text = text.replace(s, '')

        return text

    def get_from_disc(self, util_func, *, chat_id=None, message_id=None, call=None):
        try:
            if call:
                result = util_func(call.message.chat.id, call.message.message_id)
            else:
                result = util_func(chat_id, message_id)
        except FileNotFoundError as ex:
            if call:
                self.error(ex, call=call)
            else:
                self.error(ex, chat_id=chat_id, message_id=message_id)

            return None
        else:
            return result

    def error(self, ex=None, *, chat_id=None, message_id=None, call=None):
        if ex:
            print(ex)
        else:
            print(traceback.print_stack())

        if call:
            self.del_mes(call=call)
            self.send_mes(messages['bad_error'], call.message.chat.id)
        else:
            self.del_mes(chat_id=chat_id, message_id=message_id)
            self.send_mes(messages['bad_error'], chat_id)
