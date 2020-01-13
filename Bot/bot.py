import re
import time
from json import loads

import UI.cfg as cfg
import UI.ui as ui
from Bot import bot
from Bot.util import kfubot_callback, get_user_movement, goto
from Models import Course
from Models import User
from UI.buttons import common as cbt


def go():
    bot.polling(none_stop=True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'back')
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


def create_course(chat_id):
    def idle():
        if course_info['lock'] is None:
            t = None
        else:
            t = time.strftime("%d %b %Y", time.localtime(course_info['lock']))

        if course_info['name'] and course_info['desc']:
            c = creating['valid']
        elif course_info['name'] and not course_info['desc']:
            c = creating['desc']
        elif not course_info['name'] and course_info['desc']:
            c = creating['name']
        else:
            c = creating['both']

        text = cfg.messages['new_course'].format(name=course_info['name'], desc=course_info['desc'], lock=t, create=c)
        msg = bot.send_message(chat_id, text, parse_mode='Markdown')
        bot.register_next_step_handler(msg, get_user_command)

    def name(message):
        length = len(message.text)
        if cfg.course_name_length_min <= length <= cfg.course_name_length_max:
            course_info['name'] = message.text
            idle()
        else:
            bot.send_message(chat_id, 'Неверная длина имени курса. Попробуйте еще раз.')
            message.text = '/name'
            get_user_command(message)

    def desc(message):
        length = len(message.text)
        if cfg.course_desc_length_min <= length <= cfg.course_desc_length_max:
            course_info['desc'] = message.text
            idle()
        else:
            bot.send_message(chat_id, 'Неверная длина описания курса. Попробуйте еще раз.')
            message.text = '/desc'
            get_user_command(message)

    def lock(message):
        if message.text == '0':
            course_info['lock'] = None
            idle()
        elif re.fullmatch(r'\d+', message.text):
            course_info['lock'] = time.time() + (int(message.text) * 24 * 60 * 60)
            idle()
        else:
            bot.send_message(chat_id, 'Ошибочный ввод. Попробуйте еще раз.')
            message.text = '/lock'
            get_user_command(message)

    def get_user_command(message):
        if message.text == '/name':
            text = 'Введите имя курса.\nМинимальная длина {} символов, максимальная {}.' \
                .format(cfg.course_name_length_min, cfg.course_name_length_max)
            msg = bot.send_message(chat_id, text)
            bot.register_next_step_handler(msg, name)
        elif message.text == '/desc':
            text = 'Введите описание курса.\nМинимальная длина {} символов, максимальная {}.' \
                .format(cfg.course_desc_length_min, cfg.course_desc_length_max)
            msg = bot.send_message(chat_id, text)
            bot.register_next_step_handler(msg, desc)
        elif message.text == '/lock':
            text = 'Введите, в течение скольки дней будет доступна запись на курс.\nЧтобы убрать закрытие введите 0.'
            msg = bot.send_message(chat_id, text)
            bot.register_next_step_handler(msg, lock)
        elif message.text == '/create':
            if not course_info['name'] or not course_info['desc']:
                msg = bot.send_message(chat_id, 'Имя курса и описания обязательны для создания.')
                bot.register_next_step_handler(msg, get_user_command)
            else:
                c = Course.Course(owner_id=chat_id, name=course_info['name'])
                c.description = course_info['desc']
                c.entry_restriction = course_info['lock']

                msg = bot.send_message(chat_id, '*---Создание курса завершено---*', parse_mode='Markdown')
                menu_command(msg)
        elif message.text == '/exit':
            msg = bot.send_message(chat_id, '*---Создание курса отменено---*', parse_mode='Markdown')
            menu_command(msg)
        else:
            text = '*---Неверная команда. Попробуйте еще раз.\nexit чтобы выйти---*'
            msg = bot.send_message(chat_id, text, parse_mode='Markdown')
            bot.register_next_step_handler(msg, get_user_command)

    creating = {
        'valid': '*Чтобы завершить создание /create.*',
        'name': '*Необходимо заполнить имя курса /name.*',
        'desc': '*Необходимо заполнить описание курса /desc.*',
        'both': '*Необходимо заполнить имя и описание курса /name, /desc.*'
    }
    course_info = dict(name=None, desc=None, lock=None)
    idle()


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


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'menu')
def menu(call):
    if User.User(call.message.chat.id).type_u == 'student':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=cfg.static_markups['menu'], text=cfg.messages['menu']
                              )
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=cfg.static_markups['menu_teach'], text=cfg.messages['menu']
                              )


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'new_course')
def new_course(call):
    text = '*---Начато создание курса---*'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                          parse_mode='Markdown'
                          )

    create_course(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course_list')
@kfubot_callback
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
