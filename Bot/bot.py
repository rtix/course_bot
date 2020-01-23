import json
import re
import time

import UI
from Bot import botHelper, bot
from Bot.util import kfubot_callback, get_confirm_message, goto, save_user_movement
from Models import Course
from Models import User
from UI import markup as mkp
from UI.buttons import common as cbt
from UI.buttons import teacher as tbt
from UI.buttons.confirm import btn_text as btc_text


def go():
    bot.polling(none_stop=True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'back')
def back(call, fake=False, x=1):
    if fake:
        save_user_movement(call.message.chat.id, call.message.message_id, dict())
    for i in range(x - 1):
        botHelper.get_back(call)
    globals()[botHelper.get_back(call)](call)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'no')
def force_back(call):
    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'confirm')
def confirm(call):
    call.data = json.loads(call.data)

    text = botHelper.get_from_disc(get_confirm_message, call=call)
    if text:
        botHelper.edit_mes(text, call, markup=mkp.create_confirm(call.data))


def create_course(chat_id):
    def idle():
        if course_info['lock'] is None:
            t = None
        else:
            t = UI.to_dtime(course_info['lock'])

        if course_info['name'] and course_info['desc']:
            c = creating['valid']
        elif course_info['name'] and not course_info['desc']:
            c = creating['desc']
        elif not course_info['name'] and course_info['desc']:
            c = creating['name']
        else:
            c = creating['both']

        text = UI.messages['new_course'].format(name=course_info['name'], desc=course_info['desc'], lock=t, create=c)
        msg = botHelper.send_mes(text, chat_id)
        bot.register_next_step_handler(msg, get_user_command)

    def name(message):
        length = len(message.text)
        if UI.constants.COURSE_NAME_LENGTH_MIN <= length <= UI.constants.COURSE_NAME_LENGTH_MAX:
            course_info['name'] = message.text
            idle()
        else:
            botHelper.send_mes('Неверная длина имени курса. Попробуйте еще раз.', chat_id)
            message.text = '/name'
            get_user_command(message)

    def desc(message):
        length = len(message.text)
        if UI.constants.COURSE_DESC_LENGTH_MIN <= length <= UI.constants.COURSE_DESC_LENGTH_MAX:
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
                .format(UI.constants.COURSE_NAME_LENGTH_MIN, UI.constants.COURSE_NAME_LENGTH_MAX)
            botHelper.send_mes(text, chat_id)
            bot.register_next_step_handler(message, name)
        elif message.text == '/desc':
            text = 'Введите описание курса.\nМинимальная длина {} символов, максимальная {}.' \
                .format(UI.constants.COURSE_DESC_LENGTH_MIN, UI.constants.COURSE_DESC_LENGTH_MAX)
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

    botHelper.send_mes(UI.messages['start'], message.chat.id)

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
            User.User(id=message.chat.id, name=msg.text, group=1, email='q')

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
        botHelper.send_mes(UI.messages['new_user'], message.chat.id)
    else:
        if User.User(message.chat.id).type_u == 'student':
            botHelper.send_mes(UI.messages['menu'], message.chat.id, markup=UI.static_markups['menu'])
        else:
            botHelper.send_mes(UI.messages['menu'], message.chat.id, markup=UI.static_markups['menu_teach'])


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'menu')
def menu(call):
    if User.User(call.message.chat.id).type_u == 'student':
        botHelper.edit_mes(UI.messages['menu'], call, markup=UI.static_markups['menu'])
    else:
        botHelper.edit_mes(UI.messages['menu'], call, markup=UI.static_markups['menu_teach'])


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'new_course')
def new_course(call):
    botHelper.edit_mes('*---Создание курса---*', call)
    create_course(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course_list')
@kfubot_callback
def course_list(call):
    if call.data['type'] == 'all':  # TODO не добавлять закрытые курсы
        courses = [i for i in Course.fetch_all_courses()]
        text = UI.messages['all']
    elif call.data['type'] == 'my':
        courses = [i for i in User.User(call.message.chat.id).participation]
        text = UI.messages['my']
    elif call.data['type'] == 'teach':
        courses = [i for i in User.User(call.message.chat.id).possessions]
        text = UI.messages['teach']
    else:
        botHelper.error(call=call)
        return
    page = call.data['page']

    p = UI.Paging(courses, sort_key='name')
    text += p.msg(call.data['page'])
    if call.data['type'] == 'teach':
        markup = mkp.create_listed(tbt.courses(p.list(page)), tbt.manage_list, 2, page)
    else:
        markup = mkp.create_listed(cbt.courses(p.list(page)), cbt.course_list_of, 2, call.data['type'], page)
    botHelper.edit_mes(text, call, markup=markup)


# TODO check_lock method
@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course')
@kfubot_callback
def course(call):
    course_ = Course.Course(call.data['course_id'])
    num_par = len(course_.participants)
    owner = course_.owner
    end_entry = course_.entry_restriction

    if owner.id == call.message.chat.id:  # owner
        lock = 'открыта'
        if (end_entry is not None) and (time.time() > float(end_entry)):
            lock = 'закрыта'
        desc = course_.description
        if len(desc) > UI.constants.COURSE_INFO_DESC_LENGTH:
            desc = desc[:UI.constants.COURSE_INFO_DESC_LENGTH] + '...'
        text = UI.messages['course_owner_min'].format(name=course_.name, num=num_par, lock=lock, desc=desc)

        botHelper.edit_mes(text, call, markup=mkp.create([tbt.manage(call.data['course_id'])]))
    elif course_.id in (c.id for c in User.User(call.message.chat.id).participation):  # enrolled
        text = UI.messages['course'].format(
            name=course_.name, fio=owner.name, num=num_par, mail='', marks='', attend=''
        )
        c_text = 'Вы уверены, что хотите покинуть курс *{}*?'.format(course_.name)
        if (end_entry is not None) and (time.time() > float(end_entry)):
            c_text += '\n*Запись на этот курс сейчас закрыта*. Возможно, вы не сможете больше записаться на него.'
        markup = mkp.create([
                cbt.confirm_action(
                    'leave', btc_text['leave'], c_text,
                    call.message.chat.id, call.message.message_id, course_id=course_.id
                )
        ])

        botHelper.edit_mes(text, call, markup=markup)
    else:  # not enrolled
        locked = ''
        if (end_entry is not None) and (time.time() > float(end_entry)):
            locked = '*Запись на курс окончена*'
        lock = UI.to_dtime(end_entry) if end_entry else 'отсутствует'
        text = UI.messages['course_not_enroll'].format(
            name=course_.name, fio=owner.name, desc=course_.description, num=num_par, lock=lock, mail='', locked=locked
        )  # TODO mail
        c_text = 'записаться на курс *{}*'.format(course_.name)
        if locked:
            markup = mkp.create()
        else:
            markup = mkp.create([
                cbt.confirm_action(
                    'enroll', btc_text['enroll'], c_text,
                    call.message.chat.id, call.message.message_id, course_id=course_.id
                )
            ])

        botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course_owner')
@kfubot_callback
def course_owner(call):
    course_ = Course.Course(call.data['course_id'])

    text = UI.messages['course_owner_full'].format(
        name=course_.name, num=len(course_.participants),
        lock=UI.to_dtime(course_.entry_restriction), desc=course_.description
    )
    c_text = 'удалить курс *{}*'.format(course_.name)
    markup = mkp.create([
            cbt.confirm_action(
                'delete_course', btc_text['delete_course'], c_text,
                call.message.chat.id, call.message.message_id,
                course_id=course_.id
            )
    ])

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

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'leave')
def leave(call):
    call.data = json.loads(call.data)

    if call.data['course_id'] in (c.id for c in User.User(call.message.chat.id).participation):
        c = Course.Course(call.data['course_id'])
        c.remove_student(call.message.chat.id)
        bot.answer_callback_query(call.id, 'Вы покинули курс ' + c.name)
    else:
        bot.answer_callback_query(call.id, 'Вы не записаны на этот курс!', show_alert=True)

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'delete_course')
def delete_course(call):
    call.data = json.loads(call.data)
    course_ = Course.Course(call.data['course_id'])

    if call.message.chat.id == course_.owner.id:
        course_.delete()
        bot.answer_callback_query(call.id, 'Курс удален')
    else:
        bot.answer_callback_query(call.id, 'Вы не владелец этого курса!', show_alert=True)

    back(call, True, 2)


# DEBUG
@bot.message_handler(commands=['su_s'])
def sus(message):
    User.User(message.chat.id).type_u = 'student'


# DEBUG
@bot.message_handler(commands=['su_t'])
def sut(message):
    User.User(message.chat.id).type_u = 'teacher'
