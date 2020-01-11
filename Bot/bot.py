import re
from json import loads

import UI.cfg as cfg
import UI.ui as ui
from Bot import bot
from Bot.util import save_user_movement, get_user_movement
from Models import Course
from Models import User
from UI.buttons import common as cbt


def go():
    bot.polling(none_stop=True)


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back(call):
    try:
        call.data = get_user_movement(call.message.chat.id, call.message.message_id)
    except FileNotFoundError:
        print('ERROR!\nUser\'s movement file missing\nuser_id: {}; message_id: {}'
              .format(call.message.chat.id, call.message.message_id)
              )
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, cfg.messages['bad_error'], parse_mode='Markdown')
    else:
        if call.data == 'menu':
            menu(call)
        else:
            globals()[loads(call.data)['goto']](call)


@bot.message_handler(commands=['start'])
def start(message):
    def name(msg):
        if re.fullmatch(r"[a-zA-Zа-яА-Я]+ [a-zA-Zа-яА-Я ]+", msg.text):
            teacher.name = msg.text
            bot.send_message(message.chat.id, '*----Регистрация преподавателя завершена----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        else:
            bot.send_message(message.chat.id, 'Необходимо корректное имя-отчество(фамилия). Повторите:')
            bot.register_next_step_handler(message, name)

    bot.send_message(message.chat.id, cfg.messages['start'])

    if User.User(message.chat.id).type_u == 'unlogined':
        try:
            teacher = User.User(id=message.chat.id, username=message.from_user.username, name='noname')

            bot.send_message(message.chat.id, '*----Регистрация преподавателя----*',
                             parse_mode='Markdown'
                             )
            bot.send_message(message.chat.id, 'Введите ваше ФИО:')
            bot.register_next_step_handler(message, name)
        except User.TeacherAccessDeniedError:
            pass


@bot.message_handler(commands=['menu'])
def menu_command(message):
    if User.User(message.chat.id).type_u == 'unlogined':
        bot.send_message(chat_id=message.chat.id, text=cfg.messages['new_user'])
    else:
        if User.User(message.chat.id).type_u == 'student':
            bot.send_message(text=cfg.messages['menu'], chat_id=message.chat.id,
                             reply_markup=cfg.static_markups['menu']
                             )
        else:
            bot.send_message(text=cfg.messages['menu'], chat_id=message.chat.id,
                             reply_markup=cfg.static_markups['menu_teach']
                             )


@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def menu(call):
    if User.User(call.message.chat.id).type_u == 'student':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=cfg.static_markups['menu'], text=cfg.messages['menu']
                              )
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=cfg.static_markups['menu_teach'], text=cfg.messages['menu']
                              )


@bot.callback_query_handler(func=lambda call: loads(call.data)['goto'] == 'course_list')
def course_list(call):
    call_data = loads(call.data)

    if call_data['type'] == 'all':
        courses = [i for i in Course.fetch_all_courses()]
        text = cfg.messages['all']
    else:
        courses = [i for i in User.User(call.message.chat.id).participation]
        text = cfg.messages['my']
    page = call_data['page']

    p = ui.Paging(courses, sort_key='name')
    text += p.msg(call_data['page'])
    markup = ui.create_listed_markup(p.list(page), list_type=cbt.course_list_of, args=(call_data['type'], page),
                                     width=2
                                     )

    save_user_movement(call.message.chat.id, call.message.message_id, call.data)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=text, reply_markup=markup
                          )


# DEBUG
@bot.message_handler(commands=['su_s'])
def sus(message):
    User.User(message.chat.id).type_u = 'student'


# DEBUG
@bot.message_handler(commands=['su_t'])
def sut(message):
    User.User(message.chat.id).type_u = 'teacher'
