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


@bot.callback_query_handler(func=lambda call: goto(call.data) is None)
def error(call):
    botHelper.error(call=call)


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


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'C')
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
    botHelper.send_mes(UI.messages['start'], message.chat.id)


@bot.message_handler(commands=['registration'])
def registration(message):
    def name(msg):
        if re.fullmatch(r"[a-zA-Zа-яА-Я]+ [a-zA-Zа-яА-Я ]+", msg.text):
            user.name = msg.text

            menu_command(msg)
        else:
            botHelper.send_mes('Необходимо корректное имя-отчество(фамилия). Повторите:', message.chat.id)
            bot.register_next_step_handler(message, name)

    if User.User(message.chat.id).type_u == 'unlogined':
        try:
            user = User.User(id=message.chat.id, username=message.from_user.username, name='noname')
            botHelper.send_mes('*---Регистрация преподавателя---*', message.chat.id)
        except User.TeacherAccessDeniedError:
            user = User.User(id=message.chat.id, name='noname', group='1', email='qwe@qwe.qwe')
            botHelper.send_mes('*---Регистрация пользователя---*', message.chat.id)

        botHelper.send_mes('Введите ваше ФИО:', message.chat.id)
        bot.register_next_step_handler(message, name)
    else:
        botHelper.send_mes('Вы уже зарегистрированы.', message.chat.id)


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


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course')
@kfubot_callback
def course(call):
    course_ = Course.Course(call.data['c_id'])
    num_par = len(course_.participants)
    owner = course_.owner

    if owner.id == call.message.chat.id:  # owner
        lock = 'открыта' if course_.is_open else 'закрыта'
        desc = course_.description
        if len(desc) > UI.constants.COURSE_INFO_DESC_LENGTH:
            desc = botHelper.remove_danger(desc[:UI.constants.COURSE_INFO_DESC_LENGTH]) + '...'
        text = UI.messages['course_owner_min'].format(name=course_.name, num=num_par, lock=lock, desc=desc)

        botHelper.edit_mes(text, call, markup=mkp.create([tbt.manage(call.data['c_id'])]))
    elif course_.id in (c.id for c in User.User(call.message.chat.id).participation):  # enrolled
        cws = course_.classworks
        attend_text = ''
        overall = len(cws)
        if overall:
            att = sum(map(lambda cw_: cw_.attendance(call.message.chat.id).value, cws))
            attend_text = UI.messages['attendance'].format(
                count=att,
                overall=overall,
                ratio=int(att / overall * 100)
            )

        tasks = course_.tasks
        if tasks:
            total_mark = sum(map(lambda task_: task_.mark(call.message.chat.id).value, tasks))
            mean_mark = total_mark / len(tasks)
            mark_text = 'Суммарный балл: {}\nСредний балл: {}'.format(total_mark, round(mean_mark, 2))
        else:
            mark_text = ''

        text = UI.messages['course'].format(
            name=course_.name, fio=owner.name, num=num_par, mail='', marks=mark_text, attend=attend_text
        )

        c_text = 'Вы уверены, что хотите покинуть курс *{}*?'.format(course_.name)
        if not course_.is_open:
            c_text += '\n*Запись на этот курс сейчас закрыта*. Возможно, вы не сможете больше записаться на него.'

        markup = mkp.create([
                cbt.confirm_action(
                    'leave', btc_text['leave'], c_text,
                    call.message.chat.id, call.message.message_id, c_id=course_.id
                )
        ])

        botHelper.edit_mes(text, call, markup=markup)
    else:  # not enrolled
        locked = '' if course_.is_open else '*Запись на курс окончена*'
        end_entry = course_.entry_restriction
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
                    call.message.chat.id, call.message.message_id, c_id=course_.id
                )
            ])

        botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course_owner')
@kfubot_callback
def course_owner(call):
    course_ = Course.Course(call.data['c_id'])

    text = UI.messages['course_owner_full'].format(
        name=course_.name, num=len(course_.participants),
        lock=UI.to_dtime(course_.entry_restriction), desc=course_.description
    )
    c_text = 'удалить курс *{}*'.format(course_.name)
    markup = mkp.create(
        [tbt.task_list(call.data['c_id'])],
        [tbt.classwork_list(call.data['c_id'])],
        [tbt.announce(call.data['c_id'])],
        [tbt.switch_lock(call.data['c_id'], True if course_.is_open else False)],
        [cbt.confirm_action(
                'delete_course', btc_text['delete_course'], c_text,
                call.message.chat.id, call.message.message_id,
                c_id=course_.id
        )]
    )

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'class_list')
@kfubot_callback
def class_list(call):
    classworks = Course.Course(call.data['c_id']).classworks

    p = UI.Paging(classworks, sort_key='date')

    text = 'Список классных уроков' + p.msg(call.data['page'])

    markup = mkp.create_listed(
        tbt.classworks(p.list(call.data['page'])),
        tbt.classwork_list,
        2,
        call.data['c_id'], call.data['page']
    )
    mkp.add_before_back(markup, tbt.new_classwork(call.data['c_id']))

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'cw')
@kfubot_callback
def cw(call):
    course_ = Course.Course(call.data['c_id'])
    classwork = course_.classwork(call.data['cw_id'])

    p = UI.Paging(course_.participants, sort_key='name')

    text = UI.messages['classwork'].format(date=classwork.date) + p.msg(call.data['page'])

    c_text = 'Вы уверены, что хотите удалить занятие *{}*?'.format(classwork.name)

    markup = mkp.create_listed(
        tbt.user_attendance_list(p.list(call.data['page']), call.data['c_id'], call.data['cw_id']),
        tbt.classwork,
        2,
        call.data['c_id'], call.data['cw_id'], call.data['page']
    )
    mkp.add_before_back(markup, tbt.invert_attendance(call.data['c_id'], call.data['cw_id']))
    mkp.add_before_back(markup, cbt.confirm_action(
        'del_class',
        btc_text['del_class'],
        c_text,
        call.message.chat.id,
        call.message.message_id,
        c_id=call.data['c_id'], cw_id=call.data['cw_id']
    ))

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'task_list')
@kfubot_callback
def task_list(call):
    tasks = Course.Course(call.data['c_id']).tasks

    p = UI.Paging(tasks, sort_key='name')

    text = 'Список заданий' + p.msg(call.data['page'])

    markup = mkp.create_listed(
        tbt.tasks(p.list(call.data['page'])),
        tbt.task_list,
        2,
        call.data['c_id'], call.data['page']
    )
    mkp.add_before_back(markup, tbt.new_task(call.data['c_id']))

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'task')
@kfubot_callback
def task(call):
    course_ = Course.Course(call.data['c_id'])
    task_ = course_.task(call.data['t_id'])

    p = UI.Paging(course_.participants, sort_key='name')

    text = UI.messages['task'].format(name=task_.name, hmark=int(task_.highest_mark)) + p.msg(call.data['page'])

    c_text = 'Вы уверены, что хотите удалить задание *{}*?'.format(task_.name)

    markup = mkp.create_listed(
        tbt.user_tasks_list(p.list(call.data['page']), call.data['c_id'], call.data['t_id']),
        tbt.task,
        2,
        call.data['c_id'], call.data['t_id'], call.data['page']
    )
    mkp.add_before_back(markup, cbt.confirm_action(
        'del_task',
        btc_text['del_task'],
        c_text,
        call.message.chat.id,
        call.message.message_id,
        c_id=call.data['c_id'], t_id=call.data['t_id']
    ))

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'enroll')
def enroll(call):
    call.data = json.loads(call.data)

    if call.data['c_id'] not in (c.id for c in User.User(call.message.chat.id).participation):
        c = Course.Course(call.data['c_id'])
        c.append_student(call.message.chat.id)
        bot.answer_callback_query(call.id, 'Вы записались на курс ' + c.name)
    else:
        bot.answer_callback_query(call.id, 'Вы уже записаны на этот курс!', show_alert=True)

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'leave')
def leave(call):
    call.data = json.loads(call.data)

    if call.data['c_id'] in (c.id for c in User.User(call.message.chat.id).participation):
        c = Course.Course(call.data['c_id'])
        c.remove_student(call.message.chat.id)
        bot.answer_callback_query(call.id, 'Вы покинули курс ' + c.name)
    else:
        bot.answer_callback_query(call.id, 'Вы не записаны на этот курс!', show_alert=True)

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'delete_course')
def delete_course(call):
    call.data = json.loads(call.data)
    course_ = Course.Course(call.data['c_id'])

    if call.message.chat.id == course_.owner.id:
        course_.delete()
        bot.answer_callback_query(call.id, 'Курс удален')
    else:
        bot.answer_callback_query(call.id, 'Вы не владелец этого курса!', show_alert=True)

    back(call, True, 2)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'switch_lock')
def switch_lock(call):
    call.data = json.loads(call.data)

    if call.data['lock']:
        Course.Course(call.data['c_id']).entry_restriction = time.time()
        bot.answer_callback_query(call.id, 'Запись на курс закрыта')
    else:
        Course.Course(call.data['c_id']).entry_restriction = None
        bot.answer_callback_query(call.id, 'Запись на курс открыта')

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'announce')
def announce(call):
    def return_to_menu():
        new_mes = botHelper.send_mes('empty', call.message.chat.id)
        botHelper.renew_menu(call, new_mes)
        back(call, True)

    def send():
        course_ = Course.Course(call.data['c_id'])

        for part in course_.participants:
            botHelper.send_mes('Сообщение от преподавателя курса {}:'.format(course_.name), part.id)
            botHelper.send_mes(announce_info['text'], part.id)
            if announce_info['file']:
                bot.send_document(part.id, announce_info['file'], caption=announce_info['file_caption'])

        botHelper.send_mes('*---Уведомление отправлено---*', call.message.chat.id)
        return_to_menu()

    def get_file(message):
        if message.document:
            announce_info['file'] = message.document.file_id
            announce_info['file_caption'] = message.caption

        send()

    def get_text(message):
        announce_info['text'] = message.text

        botHelper.send_mes(
            'Если хотите прикрепить файлы к уведомлению, отправьте их (как документ).'
            '\nИнача нажмите /no или отправьте любой текст.',
            call.message.chat.id
        )
        bot.register_next_step_handler(message, get_file)

    call.data = json.loads(call.data)
    announce_info = {'text': '', 'file': None, 'file_caption': ''}

    botHelper.edit_mes('*---Создание уведомления---*', call)
    botHelper.send_mes(
        'Введите текст уведомления.',
        call.message.chat.id
    )
    bot.register_next_step_handler(call.message, get_text)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'new_class')
def new_class(call):
    call.data = json.loads(call.data)

    d = UI.to_dtime(time.time())
    cw_id = Course.Classwork(call.data['c_id'], name=d, date=d).number
    for user in Course.Course(call.data['c_id']).participants:
        Course.Attendance(call.data['c_id'], cw_id, user.id).value = 0

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'del_class')
def del_class(call):
    call.data = json.loads(call.data)

    if call.message.chat.id == Course.Course(call.data['c_id']).owner.id:
        Course.Classwork(call.data['c_id'], call.data['cw_id']).delete()
        bot.answer_callback_query(call.id, 'Занятие удалено')
    else:
        bot.answer_callback_query(call.id, 'Этого занятия не существует!', show_alert=True)

    back(call, True, 2)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'attend')
def attend(call):
    call.data = json.loads(call.data)

    if bool(call.data.get('u_id')):
        Course.Attendance(call.data['c_id'], call.data['cw_id'], call.data['u_id']).value = \
            not Course.Attendance(call.data['c_id'], call.data['cw_id'], call.data['u_id']).value
    else:
        for user in Course.Course(call.data['c_id']).participants:
            Course.Attendance(call.data['c_id'], call.data['cw_id'], user.id).value = \
                not Course.Attendance(call.data['c_id'], call.data['cw_id'], user.id).value

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'new_task')
def new_task(call):
    def return_to_menu():
        new_mes = botHelper.send_mes('empty', call.message.chat.id)
        botHelper.renew_menu(call, new_mes)
        back(call, True)

    def create():
        name = task_info['name']
        if not name:
            name = 'Задание ' + str(len(Course.Course(call.data['c_id']).tasks) + 1)

        Course.Task(
            course_id=call.data['c_id'],
            name=name,
            description=task_info['desc'].format(task_info['hmark']),
            highest_mark=task_info['hmark']
        )

        botHelper.send_mes('*---Задание создано---*', call.message.chat.id)
        return_to_menu()

    def get_hmark(message):
        if message.text == '/exit':
            botHelper.send_mes('*---Создание задания отменено---*', call.message.chat.id)
            return_to_menu()
        else:
            if message.text != '0' and re.fullmatch(r'\d+', message.text):
                task_info['hmark'] = int(message.text)

                create()
            else:
                botHelper.send_mes(
                    'Максимальный балл должен быть положительным целым числом.\n/exit чтобы отменить создание',
                    call.message.chat.id
                )
                bot.register_next_step_handler(message, get_hmark)

    def get_desc(message):
        if message.text == '/exit':
            botHelper.send_mes('*---Создание задания отменено---*', call.message.chat.id)
            return_to_menu()
        else:
            if len(message.text) <= UI.constants.TASK_DESC_MAX_LENGTH:
                if message.text != '/no':
                    task_info['desc'] += message.text

                botHelper.send_mes('Введите максимальный балл задания.', call.message.chat.id)
                bot.register_next_step_handler(message, get_hmark)
            else:
                botHelper.send_mes(
                    'Максимальная длина {} символов, попробуйте еще раз.\n/exit, чтобы отменить создание'.format(
                        UI.constants.TASK_DESC_MAX_LENGTH
                    ),
                    call.message.chat.id
                )
                bot.register_next_step_handler(message, get_desc)

    def get_name(message):
        if message.text == '/exit':
            botHelper.send_mes('*---Создание задания отменено---*', call.message.chat.id)
            return_to_menu()
        else:
            if len(message.text) <= UI.constants.TASK_NAME_MAX_LENGTH:
                if message.text != '/no':
                    task_info['name'] = message.text

                botHelper.send_mes(
                    'Введите описание задания.\n/no чтобы использовать описание по умолчанию.',
                    call.message.chat.id
                )
                bot.register_next_step_handler(message, get_desc)
            else:
                botHelper.send_mes(
                    'Максимальная длина {} символов, попробуйте еще раз.\n/exit, чтобы отменить создание'.format(
                        UI.constants.TASK_NAME_MAX_LENGTH
                    ),
                    call.message.chat.id
                )
                bot.register_next_step_handler(message, get_name)

    call.data = json.loads(call.data)
    task_info = {'name': '', 'desc': 'Максимальный балл: {}\n', 'hmark': 0}

    botHelper.edit_mes('*---Создание задания---*', call)
    botHelper.send_mes(
        'Введите имя задания.\n/no чтобы использовать имя по умолчанию.',
        call.message.chat.id
    )
    bot.register_next_step_handler(call.message, get_name)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'del_task')
def del_task(call):
    call.data = json.loads(call.data)

    if call.message.chat.id == Course.Course(call.data['c_id']).owner.id:
        Course.Task(call.data['c_id'], call.data['t_id']).delete()
        bot.answer_callback_query(call.id, 'Занятие удалено')
    else:
        bot.answer_callback_query(call.id, 'Этого задания не существует!', show_alert=True)

    back(call, True, 2)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'do_tsk')
def do_tsk(call):
    def return_to_menu():
        new_mes = botHelper.send_mes('empty', call.message.chat.id)
        botHelper.renew_menu(call, new_mes)
        back(call, True)

    def get_mark(message):
        if message.text == '/exit':
            return_to_menu()
        elif message.text == '-1':
            mark.value = None
        elif re.fullmatch(r'\d+', message.text):
            if int(message.text) <= task_.highest_mark:
                mark.value = int(message.text)

                return_to_menu()
            else:
                botHelper.send_mes('Оценка превышает максимум. Попробуйте еще раз.\n/exit чтобы отменить')
                bot.register_next_step_handler(message, get_mark)
        else:
            botHelper.send_mes('Неверый ввод. Попробуйте еще раз.\n/exit чтобы отменить.')
            bot.register_next_step_handler(message, get_mark)

    call.data = json.loads(call.data)
    task_ = Course.Task(call.data['c_id'], call.data['t_id'])
    mark = Course.Mark(call.data['c_id'], call.data['t_id'], call.data['u_id'])

    text = UI.messages['mark_one'].format(
        task=task_.name,
        user=User.User(call.data['u_id']).name,
        mark=mark.value,
        max=task_.highest_mark
    )

    botHelper.edit_mes(text, call)
    bot.register_next_step_handler(call.message, get_mark)


# DEBUG
@bot.message_handler(commands=['su_s'])
def sus(message):
    User.User(message.chat.id).type_u = 'student'


# DEBUG
@bot.message_handler(commands=['su_t'])
def sut(message):
    User.User(message.chat.id).type_u = 'teacher'

# TODO проверки существования сущностей
