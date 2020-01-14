import re

from Bot.util import get_user_movement
from UI.cfg import messages


class BotHelper:
    __markdown_regex = re.compile(r'\*.+?\*|_.+?_', re.IGNORECASE)

    def __init__(self, bot):
        self.__bot = bot

    def send_mes(self, text, chat_id, *, markup=None):
        return self.__bot.send_message(
            text=text,
            chat_id=chat_id,
            reply_markup=markup,
            parse_mode='Markdown' if BotHelper.__markdown_regex.search(text) else None
        )

    def edit_mes(self, text, call, *, markup=None):
        return self.__bot.edit_message_text(
            text=text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown' if BotHelper.__markdown_regex.search(text) else None
        )

    def del_mes(self, chat_id=None, message_id=None, call=None):
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
        try:
            call.data = get_user_movement(call.message.chat.id, call.message.message_id)
        except FileNotFoundError as ex:
            print(ex)
            self.del_mes(call)
            self.send_mes(messages['bad_error'], call.message.chat.id)

            return 'menu'
        else:
            return call.data if call.data == 'menu' else call.data['goto']
