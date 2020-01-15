import json
import re
import time

from Bot import botHelper, bot
from Bot.util import kfubot_callback, get_confirm_message, goto
from Models import Course
from Models import User
from UI import constants
from UI import markup as mkp
from UI import misc
from UI import ui
from UI.buttons import common as cbt


def go():
    bot.polling(none_stop=True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'back')
def back(call):
    globals()[botHelper.get_back(call)](call)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'no')
@kfubot_callback
def force_back(call):
    back(call)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'confirm')
def confirm(call):
    call.data = json.loads(call.data)

    try:
        text = get_confirm_message(call.message.chat.id, call.message.message_id)
    except FileNotFoundError as ex:
        print(ex)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        botHelper.send_mes(misc.messages['bad_error'], call.message.chat.id)
    else:
        botHelper.edit_mes(text, call, markup=mkp.create_confirm(call.data))


def create_course(chat_id):
    def idle():
        if course_info['lock'] is None:
            t = None
        else:
            t = ui.to_dtime(course_info['lock'])

        if course_info['name'] and course_info['desc']:
            c = creating['valid']
        elif course_info['name'] and not course_info['desc']:
            c = creating['desc']
        elif not course_info['name'] and course_info['desc']:
            c = creating['name']
        else:
            c = creating['both']

        text = misc.messages['new_course'].format(name=course_info['name'], desc=course_info['desc'], lock=t, create=c)
        msg = botHelper.send_mes(text, chat_id)
        bot.register_next_step_handler(msg, get_user_command)

    def name(message):
        length = len(message.text)
        if constants.COURSE_NAME_LENGTH_MIN <= length <= constants.COURSE_NAME_LENGTH_MAX:
            course_info['name'] = message.text
            idle()
        else:
            botHelper.send_mes('Неверная длина имени курса. Попробуйте еще раз.', chat_id)
            message.text = '/name'
            get_user_command(message)

    def desc(message):
        length = len(message.text)
        if constants.COURSE_DESC_LENGTH_MIN <= length <= constants.COURSE_DESC_LENGTH_MAX:
            course_info['desc'] = message.text
            idle()
        else:
            botHelper.send_mes('Неверная длина описания курса. Попробуйте еще раз.', chat_id)
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
            botHelper.send_mes('Ошибочный ввод. Попробуйте еще раз.', chat_id)
            message.text = '/lock'
            get_user_command(message)

    def get_user_command(message):
        if message.text == '/name':
            text = 'Введите имя курса.\nМинимальная длина {} символов, максимальная {}.' \
                .format(constants.COURSE_NAME_LENGTH_MIN, constants.COURSE_NAME_LENGTH_MAX)
            botHelper.send_mes(text, chat_id)
            bot.register_next_step_handler(message, name)
        elif message.text == '/desc':
            text = 'Введите описание курса.\nМинимальная длина {} символов, максимальная {}.' \
                .format(constants.COURSE_DESC_LENGTH_MIN, constants.COURSE_DESC_LENGTH_MAX)
            botHelper.send_mes(text, chat_id)
            bot.register_next_step_handler(message, desc)
        elif message.text == '/lock':
            text = 'Введите, в течение скольки дней будет доступна запись на курс.\nЧтобы убрать закрытие введите 0.'
            botHelper.send_mes(text, chat_id)
            bot.register_next_step_handler(message, lock)
        elif message.text == '/create':
            if not course_info['name'] or not course_info['desc']:
                botHelper.send_mes('Имя курса и описания обязательны для создания.', chat_id)
                bot.register_next_step_handler(message, get_user_command)
            else:
                c = Course.Course(owner_id=chat_id, name=course_info['name'])
                c.description = course_info['desc']
                c.entry_restriction = course_info['lock']

                botHelper.send_mes('*---Создание курса завершено---*', chat_id)
                menu_command(message)
        elif message.text == '/exit':
            botHelper.send_mes('*---Создание курса отменено---*', chat_id)
            menu_command(message)
        else:
            text = '*---Неверная команда. Попробуйте еще раз.\nexit чтобы выйти---*'
            botHelper.send_mes(text, chat_id)
            bot.register_next_step_handler(message, get_user_command)

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
            botHelper.send_mes('*---Регистрация преподавателя завершена---*', message.chat.id)
            menu_command(msg)
        else:
            botHelper.send_mes('Необходимо корректное имя-отчество(фамилия). Повторите:', message.chat.id)
            bot.register_next_step_handler(message, name)

    botHelper.send_mes(misc.messages['start'], message.chat.id)

    if User.User(message.chat.id).type_u == 'unlogined':
        try:
            teacher = User.User(id=message.chat.id, username=message.from_user.username, name='noname')

            botHelper.send_mes('*---Регистрация преподавателя---*', message.chat.id)
            botHelper.send_mes('Введите ваше ФИО:', message.chat.id)
            bot.register_next_step_handler(message, name)
        except User.TeacherAccessDeniedError:
            pass


@bot.message_handler(commands=['registration'])
def registration(message):
    def name(msg):
        if re.fullmatch(r"[a-zA-Zа-яА-Я]+ [a-zA-Zа-яА-Я ]+", msg.text):
            User.User(id=message.chat.id, username=message.from_user.username, name=msg.text)

            botHelper.send_mes('*---Регистрация пользователя завершена---*', message.chat.id)
            menu_command(msg)
        else:
            botHelper.send_mes('Необходимо корректное имя-отчество(фамилия). Повторите:', message.chat.id)
            bot.register_next_step_handler(message, name)

    botHelper.send_mes('*---Регистрация пользователя---*', message.chat.id)
    botHelper.send_mes('Введите ваше ФИО:', message.chat.id)
    bot.register_next_step_handler(message, name)


@bot.message_handler(commands=['menu'])
def menu_command(message):
    if User.User(message.chat.id).type_u == 'unlogined':
        botHelper.send_mes(misc.messages['new_user'], message.chat.id)
    else:
        if User.User(message.chat.id).type_u == 'student':
            botHelper.send_mes(misc.messages['menu'], message.chat.id, markup=misc.static_markups['menu'])
        else:
            botHelper.send_mes(misc.messages['menu'], message.chat.id, markup=misc.static_markups['menu_teach'])


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'menu')
def menu(call):
    if User.User(call.message.chat.id).type_u == 'student':
        botHelper.edit_mes(misc.messages['menu'], call, markup=misc.static_markups['menu'])
    else:
        botHelper.edit_mes(misc.messages['menu'], call, markup=misc.static_markups['menu_teach'])


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'new_course')
def new_course(call):
    botHelper.edit_mes('*---Создание курса---*', call)
    create_course(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course_list')
@kfubot_callback
def course_list(call):
    if call.data['type'] == 'all':  # TODO не добавлять закрытые курсы
        courses = [i for i in Course.fetch_all_courses()]
        text = misc.messages['all']
    else:
        courses = [i for i in User.User(call.message.chat.id).participation]
        text = misc.messages['my']
    page = call.data['page']

    p = ui.Paging(courses, sort_key='name')
    text += p.msg(call.data['page'])
    markup = mkp.create_listed(p.list(page), list_type=cbt.course_list_of,
                               args=(call.data['type'], page), width=2
                               )
    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course')
@kfubot_callback
def course(call):
    course_ = Course.Course(call.data['course_id'])
    num_par = len(course_.participants)
    owner = course_.owner

    if owner.id == call.message.chat.id:  # owner
        lock = 'открыта'
        end_entry = course_.entry_restriction
        if (end_entry is not None) and (time.time() > float(end_entry)):
            lock = 'закрыта'
        desc = course_.description
        if len(desc) > constants.COURSE_INFO_DESC_LENGTH:
            desc = desc[:constants.COURSE_INFO_DESC_LENGTH] + '...'
        text = misc.messages['course_owner_min'].format(name=course_.name, num=num_par, lock=lock, desc=desc)
        botHelper.edit_mes(text, call, markup=mkp.create())
    elif course_.id in (c.id for c in User.User(call.message.chat.id).participation):  # enrolled
        text = misc.messages['course'].format(name=course_.name, fio=owner.name, num=num_par,
                                              mail='', marks='', attend=''
                                              )
        c_text = 'покинуть курс *{}*'.format(course_.name)
        markup = mkp.create([cbt.confirm_leave(course_.id, c_text, call.message.chat.id, call.message.message_id)])
        botHelper.edit_mes(text, call, markup=markup)
    else:  # not enrolled
        locked = ''
        end_entry = course_.entry_restriction
        if (end_entry is not None) and (time.time() > float(end_entry)):
            locked = '*Запись на курс окончена*'
        lock = ui.to_dtime(end_entry) if end_entry else 'отсутствует'
        text = misc.messages['course_not_enroll'].format(name=course_.name, fio=owner.name,
                                                         desc=course_.description, num=num_par,
                                                         lock=lock,
                                                         mail='', locked=locked
                                                         )  # TODO mail
        c_text = 'записаться на курс *{}*'.format(course_.name)
        if locked:
            markup = mkp.create()
        else:
            markup = mkp.create(
                [cbt.confirm_enroll(course_.id, c_text, call.message.chat.id, call.message.message_id)]
            )
        botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'enroll')
def enroll(call):
    call.data = json.loads(call.data)

    if call.data['course_id'] not in (c.id for c in User.User(call.message.chat.id).participation):
        c = Course.Course(call.data['course_id'])
        c.append_student(call.message.chat.id)
        bot.answer_callback_query(call.id, 'Вы записались на курс ' + c.name)
    else:
        bot.answer_callback_query(call.id, 'Вы уже записаны на этот курс!', show_alert=True)

    force_back(call)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'leave')
def leave(call):
    call.data = json.loads(call.data)

    if call.data['course_id'] in (c.id for c in User.User(call.message.chat.id).participation):
        c = Course.Course(call.data['course_id'])
        c.remove_student(call.message.chat.id)
        bot.answer_callback_query(call.id, 'Вы покинули курс ' + c.name)
    else:
        bot.answer_callback_query(call.id, 'Вы не записаны на этот курс!', show_alert=True)

    force_back(call)


# DEBUG
@bot.message_handler(commands=['su_s'])
def sus(message):
    User.User(message.chat.id).type_u = 'student'


# DEBUG
@bot.message_handler(commands=['su_t'])
def sut(message):
    User.User(message.chat.id).type_u = 'teacher'
