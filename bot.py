import configparser
import csv
import datetime
import operator
import os
import re
import shutil
import tempfile
import time
import traceback
from json import loads
from secrets import token_urlsafe as create_key

import telebot

import Course
import Excel as xl
import Mail
import UI.cfg as cfg
import User
from UI.buttons import common as cbt, teacher as tbt
from UI.cfg import ui


sets = configparser.ConfigParser()
sets.read('settings.cfg')

if not Mail.check_valid(sets['mail']['email']):
    raise Mail.WrongEMail("Неправильный email в файле настроек.")
email = Mail.Mail(sets['mail']['email'], sets['mail']['password'])

bot = telebot.TeleBot(sets['bot']['token'], threaded=False)

# создание временной папки для времменых файлов
tmp_path = tempfile.TemporaryDirectory(prefix='kfubot-')


# при каждом запуске будет очищаться папка вывода .xlsx файлов
files = os.listdir('ExcelData/')
for file in files:
    try:
        shutil.rmtree('ExcelData/' + file)
    except OSError:
        os.unlink('ExcelData/' + file)


@bot.message_handler(commands=['start'])
def start(message):
    # для регистрации преподавателя
    def name(msg):
        if re.fullmatch(r"[a-zA-Zа-яА-Я]+ [a-zA-Zа-яА-Я ]+", msg.text):
            teacher.name = msg.text
            bot.send_message(message.chat.id, '*----Регистрация преподавателя завершена----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        else:
            bot.send_message(message.chat.id, 'Не понял. Повторите.')
            bot.register_next_step_handler(message, name)

    bot.send_message(message.chat.id, cfg.messages['start'])

    # если юзер не зарегистрирован в системе, идет проверка на возможного преподавателя
    if User.User(message.chat.id).type_u == 'unlogined':
        try:
            teacher = User.User(id=message.chat.id, username=message.from_user.username, name='noname')

            bot.send_message(message.chat.id, '*----Регистрация преподавателя----*',
                             parse_mode='Markdown'
                             )
            bot.send_message(message.chat.id, 'Введите ваше ФИО')
            bot.register_next_step_handler(message, name)
        except User.TeacherAccessDeniedError:
            pass


@bot.message_handler(commands=['menu'])
def menu(message, edit=False):
    # если что-то пошло не так. но вообще, не должно быть
    markup = cfg.err_markup
    msg = cfg.err_msg
    ##

    if edit:
        if User.User(message.chat.id).type_u == 'unlogined':
            msg = 'Для пользования необходимо зарегистрироваться'
            markup = ui.create_markup([cbt.registration])
        else:
            msg = cfg.messages['menu']
            if User.User(message.chat.id).type_u == 'teacher':
                markup = cfg.markups['menu_teach']
            else:
                markup = cfg.markups['menu']
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text=msg, reply_markup=markup
                                  )
        # здесь и далее это написано для небольшого отчета о некоторых ошибках
        except telebot.apihelper.ApiException as ex:
            print(ex)
    else:
        if User.User(message.chat.id).type_u == 'unlogined':
            msg = 'Для пользования необходимо зарегистрироваться'
            markup = ui.create_markup([cbt.registration])
        else:
            msg = cfg.messages['menu']
            if User.User(message.chat.id).type_u == 'teacher':
                markup = cfg.markups['menu_teach']
            else:
                markup = cfg.markups['menu']

        bot.send_message(message.chat.id, msg, reply_markup=markup)


@bot.message_handler(commands=['teacher'])
def teacher(message):
    # здесь теперь должно быть обновление типа юзера
    pass


# регистрация
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'reg')
def registration(call):
    # если уже есть в базе, то это хитрец
    message = call.message
    if User.User(message.chat.id).type_u != 'unlogined':
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                  text='Вы уже зарегистрированы'
                                  )
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=cfg.messages['menu'],
                              reply_markup=cfg.markups['menu']
                              )
        return

    # проверка ключа
    def registration_pass(msg, key):
        if msg.text == key:  # добавляю в бд
            User.User(id=msg.chat.id, name=user_info['name'], group=user_info['group'],
                      email=user_info['email']
                      )
            bot.send_message(msg.chat.id, '*----Регистрация завершена----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        else:
            bot.send_message(msg.chat.id, 'Неправильный код подтверждения.\n'
                                          'Делай все заново, потому что лень иначе'
                             )
            menu(msg)

    def registration_mail(msg):
        if msg.text == '/q':
            bot.send_message(msg.chat.id, '*----Регистрация отменена----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        elif Mail.check_valid(msg.text):
                user_info['email'] = msg.text.casefold().strip()

                # создаю код и отправляю письмо
                passkey = create_key(3)
                # если успешно отправлено
                if email.send(user_info['email'], 'Рега в нашем боте йооо', cfg.messages['reg_mail'] + passkey):
                    bot.send_message(msg.chat.id, 'Письмо отправлено.\n'
                                                  'Проверьте спам там даа.\n'
                                                  'Введите код регистрации:'
                                     )
                    bot.register_next_step_handler(msg, registration_pass, passkey)
                else:
                    bot.send_message(msg.chat.id, 'something wrong. try again later')
        else:
            bot.send_message(msg.chat.id, 'Не понял. Повтори.')
            bot.register_next_step_handler(msg, registration_mail)

    def registration_group(msg):
        if msg.text == '/q':
            bot.send_message(msg.chat.id, '*----Регистрация отменена----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        elif re.match(r"\d", msg.text):
                user_info['group'] = msg.text

                bot.send_message(msg.chat.id, 'Напишите Ваш email.'
                                              '\n/q чтобы отменить'
                                 )
                bot.register_next_step_handler(msg, registration_mail)
        else:
            bot.send_message(msg.chat.id, 'Не понял. Повтори.')
            bot.register_next_step_handler(msg, registration_group)

    def registration_name(msg):
        if msg.text == '/q':
            bot.send_message(msg.chat.id, '*----Регистрация отменена----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        elif re.fullmatch(r"[a-zA-Zа-яА-Я]+ [a-zA-Zа-яА-Я ]+", msg.text):
                user_info['name'] = msg.text

                bot.send_message(msg.chat.id, 'Напишите Вашу группу.'
                                              '\n/q чтобы отменить'
                                 )
                bot.register_next_step_handler(msg, registration_group)
        else:
            bot.send_message(msg.chat.id, 'Не понял. Повтори.')
            bot.register_next_step_handler(msg, registration_name)

    user_info = dict(name='', group='', email='')

    # начало регистрации
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='*----Начата регистрация----*', parse_mode='Markdown')
    except telebot.apihelper.ApiException as ex:
        print(ex)
    bot.send_message(message.chat.id, 'Напишите Ваше ФИО\n/q чтобы отменить')
    bot.register_next_step_handler(message, registration_name)


# создаю новый курс
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'new_course')
def callback_new_course(call):
    message = call.message

    # сохранение
    def new_course_save(msg):
        c = Course.Course(owner_id=msg.chat.id, name=course_info['name'])
        c.description = course_info['desc']
        c.entry_restriction = course_info['lock']

        bot.send_message(msg.chat.id, '*----Создание курса завершено----*',
                         parse_mode='Markdown'
                         )
        menu(msg)

    # промежуточный для проверки и изменения данных перед сохранением
    def new_course_trans(msg):
        if msg.text == '/q':
            bot.send_message(msg.chat.id, '*----Создание курса отменено----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        elif msg.text == '/name':
            course_info['name'] = ''
            bot.send_message(message.chat.id, 'Напишите название курса\n/q чтобы отменить')
            bot.register_next_step_handler(msg, new_course_name, edit=True)
        elif msg.text == '/desc':
            course_info['desc'] = ''
            bot.send_message(msg.chat.id, 'Напишите описание курса (необязательно).\n'
                                          '/p чтобы пропустить этот шаг\n/q чтобы отменить'
                             )
            bot.register_next_step_handler(msg, new_course_description, edit=True)
        elif msg.text == '/lock':
            course_info['lock'] = None
            bot.send_message(msg.chat.id, 'Напишите в течение скольки дней будет доступна '
                                          'запись на курс (необязательно).\n'
                                          '0 или /p чтобы пропустить этот шаг\n/q чтобы отменить'
                             )
            bot.register_next_step_handler(msg, new_course_lock)
        elif msg.text == '/g':
            new_course_save(msg)
        else:
            bot.send_message(msg.chat.id, 'Не понял. Повтори.')
            bot.register_next_step_handler(msg, new_course_trans)

    def new_course_lock(msg):
        if msg.text == '/q':
            bot.send_message(msg.chat.id, '*----Создание курса отменено----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        else:
            if msg.text != '/p':
                try:
                    days = int(msg.text)
                    if days != 0:
                        course_info['lock'] = time.time() + (days * 24 * 60 * 60)
                except ValueError:
                    bot.send_message(msg.chat.id, 'Не понял. Повтори.')
                    bot.register_next_step_handler(msg, new_course_lock)
                    return

            lock = time.strftime("%d %b %Y", time.localtime(course_info['lock']))
            if not course_info['lock']:
                lock = 'Без ограничения'
            bot.send_message(msg.chat.id, cfg.messages['new_course'].format(
                    name=course_info['name'],
                    desc=course_info['desc'],
                    lock=lock
                    ), parse_mode='Markdown'
                             )
            bot.register_next_step_handler(msg, new_course_trans)

    def new_course_description(msg, edit=False):
        if msg.text == '/q':
            bot.send_message(msg.chat.id, '*----Создание курса отменено----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        else:
            if msg.text != '/p':
                course_info['desc'] = msg.text

            if edit:
                lock = time.strftime("%d %b %Y", time.localtime(course_info['lock']))
                if not course_info['lock']:
                    lock = 'Без ограничения'
                bot.send_message(msg.chat.id, cfg.messages['new_course'].format(
                        name=course_info['name'],
                        desc=course_info['desc'],
                        lock=lock
                        ), parse_mode='Markdown'
                                 )
                bot.register_next_step_handler(msg, new_course_trans)
            else:
                bot.send_message(msg.chat.id, 'Напишите в течение скольки дней будет доступна '
                                              'запись на курс (необязательно).\n'
                                              '0 или /p чтобы пропустить этот шаг\n/q чтобы отменить'
                                 )
                bot.register_next_step_handler(msg, new_course_lock)

    def new_course_name(msg, edit=False):
        if msg.text == '/q':
            bot.send_message(msg.chat.id, '*----Создание курса отменено----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        else:
            if re.findall(r"[А-Яа-яA-Za-z]", msg.text):
                course_info['name'] = msg.text
            else:
                bot.send_message(msg.chat.id, 'Не понял. Повтори.')
                bot.register_next_step_handler(msg, new_course_name)

            if edit:
                lock = time.strftime("%d %b %Y", time.localtime(course_info['lock']))
                if not course_info['lock']:
                    lock = 'Без ограничения'
                bot.send_message(msg.chat.id, cfg.messages['new_course'].format(
                        name=course_info['name'],
                        desc=course_info['desc'],
                        lock=lock
                        ), parse_mode='Markdown'
                                 )
                bot.register_next_step_handler(msg, new_course_trans)
            else:
                bot.send_message(msg.chat.id, 'Напишите описание курса (необязательно).\n'
                                              '/p чтобы пропустить этот шаг\n/q чтобы отменить'
                                 )
                bot.register_next_step_handler(msg, new_course_description)

    # начало создания
    course_info = dict(name='', desc='', lock=None)
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='*----Начато создание курса----*', parse_mode='Markdown')
    except telebot.apihelper.ApiException as ex:
        print(ex)
    bot.send_message(message.chat.id, 'Напишите название курса\n/q чтобы отменить')
    bot.register_next_step_handler(message, new_course_name)


# создаю новое задание
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'new_task')
def callback_new_task(call):
    def key(task):
        return task.number

    message = call.message
    course_id = loads(call.data)['id']

    def new_task_save():
        Course.Task(course_id, name=task_info['name'], description=task_info['desc'],
                    highest_mark=task_info['mark']
                    )
        bot.send_message(message.chat.id, '*----Создание задания завершено----*',
                         parse_mode='Markdown'
                         )
        call.message = bot.send_message(message.chat.id, 'empty')
        callback_managing(call, 'task', course_id)

    def new_task_mark(msg):
        if msg.text == '/q':
            bot.send_message(msg.chat.id, '*----Создание задания отменено----*',
                             parse_mode='Markdown'
                             )
            call.message = bot.send_message(message.chat.id, 'empty')
            callback_managing(call, 'task', course_id)
        else:
            if msg.text != '/p':
                if re.fullmatch(r"[0-9]+", msg.text):
                    mark = int(msg.text)
                    if mark:
                        task_info['mark'] = int(msg.text)
                    else:
                        bot.send_message(msg.chat.id, 'Не понял. Повторите.')
                        bot.register_next_step_handler(msg, new_task_name)
                        return
                else:
                    bot.send_message(msg.chat.id, 'Не понял. Повторите.')
                    bot.register_next_step_handler(msg, new_task_name)
                    return

            new_task_save()

    def new_task_desc(msg):
        if msg.text == '/q':
            bot.send_message(msg.chat.id, '*----Создание задания отменено----*',
                             parse_mode='Markdown'
                             )
            call.message = bot.send_message(message.chat.id, 'empty')
            callback_managing(call, 'task', course_id)
        else:
            if msg.text != '/p':
                if re.findall(r"[А-Яа-яA-Za-z]", msg.text):
                    task_info['desc'] = msg.text
                else:
                    bot.send_message(msg.chat.id, 'Не понял. Повторите.')
                    bot.register_next_step_handler(msg, new_task_name)
                    return

            bot.send_message(msg.chat.id, 'Напишите максимальный балл задания '
                                          '(необязательно, по умолчанию 5).'
                                          '\n/p чтобы пропустить этот шаг\n/q чтобы отменить'
                             )
            bot.register_next_step_handler(msg, new_task_mark)

    def new_task_name(msg):
        if msg.text == '/q':
            bot.send_message(msg.chat.id, '*----Создание задания отменено----*',
                             parse_mode='Markdown'
                             )
            call.message = bot.send_message(message.chat.id, 'empty')
            callback_managing(call, 'task', course_id)
        else:
            if msg.text != '/p':
                if re.findall(r"[А-Яа-яA-Za-z]", msg.text):
                    task_info['name'] = msg.text
                else:
                    bot.send_message(msg.chat.id, 'Не понял. Повторите.')
                    bot.register_next_step_handler(msg, new_task_name)
                    return

            bot.send_message(msg.chat.id, 'Напишите описание/примечания задания (необязательно).\n'
                                          '/p чтобы пропустить этот шаг\n/q чтобы отменить'
                             )
            bot.register_next_step_handler(msg, new_task_desc)

    # начало создания
    tasks = Course.Course(course_id).tasks
    num = str(max(tasks, key=key).number + 1) if len(tasks) != 0 else '1'  # это нужно для имени по умолчанию
    task_info = dict(name='Задание ' + num, desc='Пуста', mark=5)
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='*----Начато создание задания----*', parse_mode='Markdown'
                              )
    except telebot.apihelper.ApiException as ex:
        print(ex)
    bot.send_message(message.chat.id, 'Напишите название задания (необязательно).'
                                      '\n/p чтобы пропустить\n/q чтобы отменить'
                     )
    bot.register_next_step_handler(message, new_task_name)


# хендлер для кнопки "назад"
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'back')
def callback_back(call):
    """Вызываются сами функции. call.data хранит два опциональных параметра.
    back=bool нужен для определения, что вызов является "прямым", через код."""

    back_to = loads(call.data)['back']
    if back_to == 'menu':
        menu(call.message, True)
    elif back_to == 'all':
        callback_menu(call, _command='all_courses', _page=loads(call.data)['ex'], back=True)
    elif back_to == 'my':
        callback_menu(call, _command='my_courses', _page=loads(call.data)['ex'], back=True)
    elif back_to == 'teach':
        callback_menu(call, _command='teach_courses', _page=loads(call.data)['ex'], back=True)
    elif back_to == 'a_course':
        callback_course(call, _course_id=loads(call.data)['ex'],
                        _back_to=loads(call.data)['ex1'],
                        page=0, back=True
                        )
    elif back_to == 'c_act':
        callback_course_act(call, _command=loads(call.data)['ex'],
                            _course_id=loads(call.data)['ex1'], back=True
                            )
    elif back_to == 'managing':
        callback_managing(call, _command=loads(call.data)['ex1'],
                          _course_id=loads(call.data)['ex'], back=True
                          )
    elif back_to == 'tasks':
        callback_managing(call, _command='task', _course_id=loads(call.data)['ex'],
                          page=loads(call.data)['ex1'], back=True
                          )
    elif back_to == 'task':
        callback_task(call, _course_id=loads(call.data)['ex'],
                      _id_task=loads(call.data)['ex1'], back=True
                      )
    elif back_to == 'courses':
        callback_course(call, _course_id=loads(call.data)['ex'],
                        _back_to=loads(call.data)['ex1'], back=True
                        )
    elif back_to == 'task_s':
        callback_tasks_show(call, _course_id=loads(call.data)['ex'],
                            page=loads(call.data)['ex1'], back=True)


# меню // кнопки для "Все курсы" и "Мои курсы"
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'menu')
def callback_menu(call, _command=None, _page=0, back=False):
    """Выводится список курсов по командам all, my, teach.

    Здесь и в последущих функциях параметры по умолчанию нужны для "прямых" вызовов.
    Т.е. для кнопки назад и ее имитации"""

    # если что-то пошло не так. но вообще, не должно быть
    markup = cfg.err_markup
    msg = cfg.err_msg
    ##

    if back:
        command = _command
        page = _page if _page else 0
    else:
        command = loads(call.data)['cmd']
        page = loads(call.data)['page']

    message = call.message

    if command == 'my_courses':  # получаем айди записанных курсов
        courses = [i for i in User.User(message.chat.id).participation]
        msg = cfg.messages['my']
        prev = 'my'
    elif command == 'teach_courses':  # получаем айди управляемых курсов
        courses = [i for i in User.User(message.chat.id).possessions]
        msg = cfg.messages['teach']
        prev = 'teach'
    else:  # получаем айди всех курсов
        courses = [i for i in Course.fetch_all_courses()]
        msg = cfg.messages['all']
        prev = 'all'

    p = ui.Paging(courses, sort_key='name')
    msg += p.msg(page)
    markup = ui.create_markup(*[[i] for i in cbt.course([i.id for i in p.list(page)], prev, page)],
                              [cbt.backward('menu', page, command),
                               cbt.forward('menu', page, command)],
                              [cbt.back('menu')],
                              width=2
                              )

    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=msg, reply_markup=markup
                              )
    except telebot.apihelper.ApiException as ex:
        print(ex)


# вывод информации о курсе
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'courses')
def callback_course(call, _course_id=None, _back_to='menu', page=0, back=False):
    # если что-то пошло не так. но вообще, не должно быть
    markup = cfg.err_markup
    msg = cfg.err_msg
    ##
    message = call.message
    if back:
        course_id = _course_id
        back_to = _back_to
    else:
        course_id = loads(call.data)['id']
        try:
            back_to = loads(call.data)['prev']
        except KeyError:
            back_to = _back_to
        try:
            page = loads(call.data)['page']
        except KeyError:
            pass

    # если вызвано из управляемых курсов, то не надо показывать инфу о нем
    if back_to == 'teach':
        callback_course_act(call, 'mng', course_id, back_to)
        return

    course = Course.Course(course_id)

    # получаю информацию о курсе
    desc = course.description if course.description else 'Описания нет'
    try:
        lock = time.strftime("%d %b %Y", time.localtime(float(course.entry_restriction)))
    except TypeError:
        lock = 'без ограничения'
    _fio = re.findall(r"[a-zA-Zа-яА-Я]+", course.owner.name)
    fio = _fio.pop(0) + ' '
    for word in _fio:
        fio += word[0] + '. '
    msg = cfg.messages['course'].format(name=course.name, desc=desc,
                                        num=len(course.participants), lock=lock,
                                        fio=fio
                                        )

    # создаю клавиатуру
    if message.chat.id == course.owner.id:  # если владелец
        markup = ui.create_markup([tbt.manage(course_id, back_to)], [cbt.back(back_to, page)])
    else:
        if message.chat.id in [user.id for user in course.participants]:  # если уже записан
            markup = ui.create_markup([cbt.show_mark(course_id, back_to), cbt.task_list(course_id)],
                                      [cbt.leave(course_id, back_to)], [cbt.back(back_to, page)]
                                      )
        else:
            markup = ui.create_markup([cbt.enroll(course_id, back_to)], [cbt.back(back_to, page)])

    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=msg, reply_markup=markup, parse_mode='Markdown')
    except telebot.apihelper.ApiException as ex:
        print(ex)


# показать оценки
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'perf')
def callback_marks_show(call):
    message = call.message
    course_id = loads(call.data)['id']
    page = loads(call.data)['page']
    try:
        prev = loads(call.data)['prev']
    except KeyError:
        prev = loads(call.data)['cmd']

    course = Course.Course(course_id)
    tasks = course.tasks

    msg = '*' + course.name + '*' + '\n'
    if tasks:
        p = ui.Paging(tasks)
        msg += p.msg(page)
        for task in p.list(page):
            msg += '\n*{name}*:  *{mark}*/{max}'.format(name=task.name,
                                                        mark=task.mark(message.chat.id).value,
                                                        max=task.highest_mark
                                                        )
    else:
        msg += 'Заданий еще не было.'

    classes = course.classworks
    if classes:
        absence = 0
        for cl in classes:
            if not cl.attendance(message.chat.id):
                absence += 1
        msg += '\nКол-во пропусков: ' + str(absence)

    markup = ui.create_markup([cbt.backward('mark_s', page, prev, course_id),
                               cbt.forward('mark_s', page, prev, course_id)],
                              [cbt.back('courses', course_id, prev)]
                              )

    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=msg, reply_markup=markup, parse_mode='Markdown')
    except telebot.apihelper.ApiException as ex:
        print(ex)


# показать задания
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'task_s')
def callback_tasks_show(call, _course_id=None, page=0, back=False):
    message = call.message

    if back:
        course_id = _course_id
        prev = 'menu'
    else:
        course_id = loads(call.data)['id']
        page = loads(call.data)['page']
        try:
            prev = loads(call.data)['prev']
        except KeyError:
            prev = loads(call.data)['cmd']

    tasks_id = [i.number for i in Course.Course(course_id).tasks]
    p = ui.Paging(tasks_id, 7)
    markup = ui.create_markup(*[[i] for i in cbt.task(p.list(page), course_id,
                                                      message.chat.id, page)],
                              [cbt.backward('managing', page, prev, course_id),
                               cbt.forward('managing', page, prev, course_id)],
                              [cbt.back('courses', course_id, prev)],
                              width=2
                              )

    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='Список заданий.' + p.msg(page),
                              reply_markup=markup
                              )
    except telebot.apihelper.ApiException as ex:
        print(ex)


# сведения о задании
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'task_u')
def callback_task_info(call):
    message = call.message
    course_id = loads(call.data)['id']
    id_task = loads(call.data)['id_t']
    back_page = loads(call.data)['page']

    task = Course.Task(course_id, id_task)

    markup = ui.create_markup([cbt.back('task_s', course_id, back_page)])

    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='*{}*\n{}\n\n*Оценка*: *{}*/{}'.format(Course.Course(course_id).name,
                                                                          task.description,
                                                                          task.mark(message.chat.id).value,
                                                                          task.highest_mark),
                              reply_markup=markup, parse_mode='Markdown'
                              )
    except telebot.apihelper.ApiException as ex:
        print(ex)


# обработка записаться и управление курса
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'c_act')
def callback_course_act(call, _command=None, _course_id=None, back=False):
    # если что-то пошло не так. но вообще, не должно быть
    markup = cfg.err_markup
    msg = cfg.err_msg
    ##

    message = call.message
    if back:
        command = _command
        course_id = _course_id
        back_to = 'menu'
    else:
        command = loads(call.data)['cmd']
        course_id = loads(call.data)['id']
        try:
            back_to = loads(call.data)['prev']
        except KeyError:
            back_to = 'menu'

    user = User.User(message.chat.id)
    course = Course.Course(course_id)

    if command == 'enroll':  # записаться
        # если запись еще открыта
        if course.entry_restriction is None or time.time() < float(course.entry_restriction):
            if course_id not in [course.id for course in user.participation]:
                course.append_student(user.id)
                bot.answer_callback_query(callback_query_id=call.id,
                                          text='Вы успешно записались на курс',
                                          )
            else:
                bot.answer_callback_query(callback_query_id=call.id,
                                          text='Вы уже записаны на этот курс',
                                          show_alert=True
                                          )
        else:
            bot.answer_callback_query(callback_query_id=call.id, text='Запись на курс закончена')

        callback_course(call, course_id, back_to, 0)
    elif command == 'leave':  # покинуть курс
        if course_id in [course.id for course in user.participation]:
            course.remove_student(user.id)
            bot.answer_callback_query(callback_query_id=call.id,
                                      text='Вы успешно покинули курс',
                                      )
        else:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text='Вы не были записаны на этот курс',
                                      show_alert=True
                                      )

        callback_course(call, course_id, back_to, 0)
    elif command == 'mng':  # управление
        try:
            lock = time.strftime("%d %b %Y", time.localtime(float(course.entry_restriction)))
        except TypeError:
            lock = 'без ограничения'
        msg = "*{name}*\n*Участников*: {num}\n*Конец записи*: {lock}". \
            format(num=len(course.participants),
                   lock=lock, name=course.name
                   )

        markup = ui.create_markup([tbt.tasks(course_id), tbt.attendance(course_id)],
                                  [tbt.participants(course_id, back_to)],
                                  [tbt.course_out(course_id)],
                                  [tbt.announce(course_id)],
                                  [tbt.delete(course_id), tbt.redact(course_id, back_to)],
                                  [cbt.back('teach')]
                                  )
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text=msg, reply_markup=markup, parse_mode='Markdown'
                                  )
        except telebot.apihelper.ApiException as ex:
            print(ex)


# управление курсом
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'managing')
def callback_managing(call, _command=None, _course_id=None, page=0, back=False):
    message = call.message
    if back:
        command = _command
        course_id = _course_id
    else:
        command = loads(call.data)['cmd']
        course_id = loads(call.data)['id']
        try:
            page = loads(call.data)['page']
        except KeyError:
            pass

    course = Course.Course(course_id)

    if command == 'del_c':  # удалить курс
        markup = ui.create_markup([tbt.confirm(command, course_id)],
                                  [cbt.back('c_act', 'mng', course_id)]
                                  )

        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text='Вы уверены, что хотите удалить курс?',
                                  reply_markup=markup
                                  )
        except telebot.apihelper.ApiException as ex:
            print(ex)
    elif command == 'parts':  # участники
        participants = [i for i in course.participants]
        p = ui.Paging(participants, 7, 'name')
        markup = ui.create_markup(*[[i] for i in tbt.user([i.id for i in p.list(page)],  course_id, page)],
                                  [cbt.backward('managing', page, command, course_id),
                                   cbt.forward('managing', page, command, course_id)],
                                  [cbt.back('c_act', 'mng', course_id)],
                                  width=2
                                  )
        msg = 'Участники' + p.msg(page)

        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text=msg, reply_markup=markup
                                  )
        except telebot.apihelper.ApiException as ex:
            print(ex)
    elif command == 'task':  # задания
        tasks_id = [i.number for i in course.tasks]
        p = ui.Paging(tasks_id, 7)
        markup = ui.create_markup(*[[i] for i in tbt.task(p.list(page), course_id, page)],
                                  [cbt.backward('managing', page, command, course_id),
                                   cbt.forward('managing', page, command, course_id)],
                                  [tbt.task_new(course_id)],
                                  [tbt.task_xl(course_id)],
                                  [cbt.back('c_act', 'mng', course_id)],
                                  width=2
                                  )

        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text='Список заданий.'
                                       '\n* - означет, что не у всех студентов есть оценка'
                                       + p.msg(page),
                                  reply_markup=markup
                                  )
        except telebot.apihelper.ApiException as ex:
            print(ex)
    elif command == 'attend':  # посещаемость
        class_id = [i.number for i in course.classworks]
        p = ui.Paging(class_id, 7)
        add_remove = [tbt.class_add(course_id)]
        if class_id:
            add_remove.append(tbt.class_remove(course_id))
        markup = ui.create_markup(*[[i] for i in tbt.class_list(p.list(page), course_id, page)],
                                  [cbt.backward('managing', page, command, course_id),
                                   cbt.forward('managing', page, command, course_id)],
                                  [tbt.class_csv(course_id), tbt.class_xl(course_id)],
                                  add_remove,
                                  [cbt.back('c_act', 'mng', course_id)]
                                  )

        msg = 'Список занятий.'
        if not len(class_id):
            msg += '\nВы еще не добавляли занятия.'
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text=msg, reply_markup=markup
                                  )
        except telebot.apihelper.ApiException as ex:
            print(ex)
    elif command == 'red':  # редактирование. Ужас какой-то. Всегда это скрываю в коде
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text='*----Начало редактирования----*', parse_mode='Markdown'
                                  )
        except telebot.apihelper.ApiException as ex:
            print(ex)

        def change(msg, what, msg_id):
            if msg.text == '/q':
                bot.delete_message(msg.chat.id, msg_id)
                try:
                    lock = time.strftime("%d %b %Y",
                                         time.localtime(float(course.entry_restriction))
                                         )
                except TypeError:
                    lock = 'без ограничения'
                text = cfg.messages['red'].format(name=course.name, desc=course.description,
                                                  lock=lock
                                                  )
                a = bot.send_message(chat_id=message.chat.id, text=text,
                                     parse_mode='Markdown'
                                     ).message_id
                bot.register_next_step_handler(message, choice, a)
            else:
                b = True
                if what == 'name':
                    if re.findall(r"[А-Яа-яA-Za-z]", msg.text):
                        course.name = msg.text
                    else:
                        a = bot.send_message(msg.chat.id, 'Не понял. Повторите.').message_id
                        bot.register_next_step_handler(msg, change, 'name', a)
                        b = False
                elif what == 'desc':
                    course.description = msg.text
                elif what == 'lock':
                    print(msg.text)
                    if msg.text == '0':
                        course.entry_restriction = None
                    elif re.fullmatch(r"\d{2} \d{2} \d{4}", msg.text):
                        date = msg.text.split()
                        for i in range(3):
                            date[i] = int(date[i])
                        try:
                            secs = datetime.datetime(date[2], date[1], date[0])
                        except ValueError:
                            a = bot.send_message(msg.chat.id, 'Не понял. Повторите.').message_id
                            bot.register_next_step_handler(msg, change, 'name', a)
                            b = False
                        else:
                            course.entry_restriction = secs.timestamp()
                    else:
                        a = bot.send_message(msg.chat.id, 'Не понял. Повторите.').message_id
                        bot.register_next_step_handler(msg, change, 'lock', a)
                        b = False
                if b:
                    bot.delete_message(message.chat.id, msg_id)
                    try:
                        lock = time.strftime("%d %b %Y",
                                             time.localtime(float(course.entry_restriction))
                                             )
                    except TypeError:
                        lock = 'без ограничения'
                    text = cfg.messages['red'].format(name=course.name, desc=course.description,
                                                      lock=lock
                                                      )
                    a = bot.send_message(chat_id=message.chat.id, text=text,
                                         parse_mode='Markdown'
                                         ).message_id
                    bot.register_next_step_handler(message, choice, a)

        def choice(msg, msg_id=0):
            msg_id = msg_id if msg_id else message.message_id
            if msg.text == '/q':
                bot.send_message(message.chat.id, '*----Конец редактирования----*',
                                 parse_mode='Markdown'
                                 )
                bot.edit_message_text(chat_id=message.chat.id, message_id=msg_id,
                                      text='Редактирование отменено.')
                a = bot.send_message(msg.chat.id, 'empty')
                call.message.message_id = a.message_id
                callback_course_act(call, 'mng', course_id, True)
            elif msg.text == '/name':
                bot.delete_message(msg.chat.id, msg_id)
                a = bot.send_message(msg.chat.id, 'Введите новое имя.\n*Текущее*: {}'
                                                  '\n/q чтобы отменить'.format(course.name),
                                     parse_mode='Markdown'
                                     ).message_id
                bot.register_next_step_handler(msg, change, 'name', a)
            elif msg.text == '/desc':
                bot.delete_message(msg.chat.id, msg_id)
                a = bot.send_message(msg.chat.id, 'Введите новое описание.\n*Текущее*: {}'
                                                  '\n/q чтобы отменить'.format(course.description),
                                     parse_mode='Markdown'
                                     ).message_id
                bot.register_next_step_handler(msg, change, 'desc', a)
            elif msg.text == '/lock':
                bot.delete_message(msg.chat.id, msg_id)
                try:
                    lock = time.strftime("%d %b %Y", time.localtime(float(course.entry_restriction)))
                except TypeError:
                    lock = 'без ограничения'
                a = bot.send_message(msg.chat.id, 'Введите новую дату закрытия записи'
                                                  'в формате дд мм гггг.\n0 чтобы убрать ограничение'
                                                  '\n*Текущее*: {}\n/q чтобы отменить'.format(lock),
                                     parse_mode='Markdown'
                                     ).message_id
                bot.register_next_step_handler(msg, change, 'lock', a)
            else:
                bot.send_message(msg.chat.id, 'Не понял. Повторите.')
                bot.register_next_step_handler(msg, choice)

        try:
            lock = time.strftime("%d %b %Y", time.localtime(float(course.entry_restriction)))
        except TypeError:
            lock = 'без ограничения'
        text = cfg.messages['red'].format(name=course.name, desc=course.description, lock=lock)
        a = bot.send_message(chat_id=message.chat.id, text=text, parse_mode='Markdown').message_id
        bot.register_next_step_handler(message, choice, a)
    elif command == 'c_out':  # вывести в .xlsx файл курс
        bot.send_document(message.chat.id, open(xl.get_attendance(course_id), 'br'), caption='Посещение')
        bot.send_document(message.chat.id, open(xl.get_marks(course_id), 'br'), caption='Оценки')

        try:  # т.к. бот не умеет удалять старые сообщения. По возможности удалит
            bot.delete_message(message.chat.id, message.message_id)
        except telebot.apihelper.ApiException:
            pass
        else:
            call.message.message_id = bot.send_message(message.chat.id, 'empty').message_id
        callback_course_act(call, 'mng', course_id, True)
    elif command == 'ance':
        def summary():
            file_names = [doc.file_name for doc in ann_info['files']]
            write = 'изменить' if ann_info['text'] else 'написать'
            bot.send_message(chat_id=message.chat.id,
                             text=cfg.messages['new_announce'].format(text=ann_info['text'],
                                                                      files=file_names, write=write
                                                                      ),
                             parse_mode='Markdown'
                             )
            bot.register_next_step_handler(message, command)
            return

        def command(msg):
            if msg.text == '/q':
                bot.send_message(msg.chat.id, '*----Отправление объявления отменено----*',
                                 parse_mode='Markdown'
                                 )
                call.message.message_id = bot.send_message(msg.chat.id, 'empty').message_id
                callback_course_act(call, 'mng', course_id, True)
                return
            elif msg.text == '/text':
                def get(msg):
                    if msg.text != '/q':
                        ann_info['text'] = msg.text

                    summary()
                    return

                bot.send_message(message.chat.id, 'Напишите текст:\n/q чтобы отменить изменение')
                bot.register_next_step_handler(msg, get)
                return
            elif msg.text == '/file':
                def get(msg):
                    if msg.document:
                        ann_info['files'].append(msg.document)
                    summary()
                    return

                bot.send_message(message.chat.id, 'Отправьте документ:\n/q чтобы отменить')
                bot.register_next_step_handler(msg, get)
                return
            elif msg.text == '/go':
                files = []
                for file in ann_info['files']:
                    downloaded_file = bot.download_file(bot.get_file(file.file_id).file_path)
                    with open(tmp_path.name + os.sep + file.file_name, 'bw') as new_file:
                        new_file.write(downloaded_file)
                    files.append(new_file.name)
                for student in course.participants:
                    bot.send_message(student.id, cfg.messages['announce'].format(text=ann_info['text']))
                    for file in files:
                        bot.send_document(student.id, open(file, 'br'))

                bot.send_message(message.chat.id, 'Объявление отправлено.')
                call.message = bot.send_message(message.chat.id, 'empty')
                callback_course_act(call, 'mng', course_id, True)
                return
            else:
                bot.send_message(msg.chat.id, 'Не понял. Повторите.')
                bot.register_next_step_handler(msg, command)
                return

        ann_info = dict(text='', files=[])
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text='*----Начато отправление объявления----*', parse_mode='Markdown'
                                  )
        except telebot.apihelper.ApiException as ex:
            print(ex)
        summary()


# добавить/убрать занятие
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'class')
def callback_class_other(call):
    message = call.message
    course_id = loads(call.data)['id']
    command = loads(call.data)['cmd']

    if command == 'add':  # добавить
        num = Course.Classwork(course_id, name='Занятие '
                                               + str(len(Course.Course(course_id).classworks)),
                               date=time.time()
                               ).number
        for user in Course.Course(course_id).participants:
            Course.Attendance(course_id, num, user.id)

        callback_managing(call, 'attend', course_id, back=True)
    elif command == 'rm':  # удалить
        classes = Course.Course(course_id).classworks
        if not classes:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                      text='Занятий нет'
                                      )
        else:
            # __надо изменить
            num = Course.Course(course_id).classworks[-1].number
            for user in Course.Course(course_id).participants:
                Course.Attendance(course_id, num, user.id).delete()
            # __

            Course.Course(course_id).classworks[-1].delete()

            callback_managing(call, 'attend', course_id, back=True)


# загрузка файлов
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'file')
def callback_file_filling(call):
    message = call.message
    course_id = loads(call.data)['id']
    command = loads(call.data)['cmd']

    if command == 'csv':
        # чтение .csv
        def read_csv(file, header):
            students = [i for i in Course.Course(course_id).participants]
            students = sorted(students, key=operator.attrgetter('name'))
            classes = Course.Course(course_id).classworks
            log = '\nОшибки:\n'
            errors = False
            header = bool(header)  # определяю наличие заголовков
            k = 0
            for row in csv.reader(file):
                if header:  # если есть, пропускаю первую строчку
                    header = False
                    continue
                else:
                    # сравниваю имена в моем отсорт. списке и .csv
                    b = False
                    for word in row[0].split():
                        for name in students[k].name.split():
                            if word == name:
                                b = True
                                break
                    if not b:
                        bot.answer_callback_query(call.id, 'Ошибка!')
                        log += 'Несовпадение ФИО у {}.\nВозможно несовпадение списков студентов.\n' \
                               'Отменяю операцию.'.format(row[0])
                        bot.send_message(message.chat.id, log)
                        callback_managing(call, 'attend', course_id, back=True)
                        return

                    k1 = 0
                    for i in row[1:]:
                        if k1 > len(classes) - 1:  # если занятий .csv больше, чем в боте, создаю новое
                            Course.Classwork(course_id, name='Занятие '
                                                             + str(len(Course.Course(course_id)
                                                                       .classworks)),
                                             date=time.time()
                                             )
                            classes = Course.Course(course_id).classworks

                        if int(i) != 0 and int(i) != 1:
                            errors = True
                            log += row[0] + ': Неверно указано значение.\n'

                        Course.Attendance(course_id, classes[k1].number, students[k].id).value = int(i)
                        k1 += 1
                    k += 1

            text = 'Проставление посещаемости завершено.'
            if errors:
                text += log
            bot.send_message(message.chat.id, text)
            call.message = bot.send_message(message.chat.id, 'empty')
            callback_managing(call, 'attend', course_id, back=True)
            return

        # получение .csv
        def get_csv(msg):
            if msg.text == '/q':
                bot.edit_message_text('Загрузка .csv отменена', message.chat.id, message.message_id)
                call.message = bot.send_message(msg.chat.id, 'empty')
                callback_managing(call, 'attend', course_id, back=True)
                return
            else:
                try:
                    file_info = bot.get_file(msg.document.file_id)
                except AttributeError:
                    bot.send_message(msg.chat.id, 'Вы не прикрепили файл. Попробуйте еще раз:'
                                                  '\n/q чтобы отменить')
                    bot.register_next_step_handler(msg, get_csv)
                    return
                file_downloaded = bot.download_file(file_info.file_path)
                # записываю файл во временную папку
                file = tempfile.TemporaryFile(dir=tmp_path.name)
                file.write(file_downloaded)
                file.seek(0)
                file.flush()
                with open(file.name) as tcsv:
                    read_csv(tcsv, msg.caption)

        # начало
        try:
            bot.edit_message_text("Загрузите .csv файл\nЕсли у вас нет заголовков, "
                                  "вместе с файлом напишите '0', иначе '1'\n/q чтобы отменить",
                                  message.chat.id, message.message_id
                                  )
        except telebot.apihelper.ApiException as ex:
            print(ex)
        bot.register_next_step_handler(message, get_csv)
    elif command == 'xl_a' or command == 'xl_t':
        def go_go_xl(msg):
            if msg.text == '/q':
                bot.edit_message_text('Загрузка .xl отменена', message.chat.id, message.message_id)
                call.message = bot.send_message(msg.chat.id, 'empty')
                callback_managing(call, 'attend', course_id, back=True)
                return
            else:
                try:
                    file_info = bot.get_file(msg.document.file_id)
                except AttributeError:
                    bot.send_message(msg.chat.id, 'Вы не прикрепили файл. Попробуйте еще раз:'
                                                  '\n/q чтобы отменить')
                    bot.register_next_step_handler(msg, get_csv)
                    return
                file_downloaded = bot.download_file(file_info.file_path)
                file = tempfile.TemporaryFile(dir=tmp_path.name)
                file.write(file_downloaded)
                file.seek(0)
                file.flush()

                try:
                    if command == 'xl_a': xl.set_attendance(course_id, file)
                    else: xl.set_marks(course_id, file)
                    bot.answer_callback_query(call.id, 'Успешно прочитано')
                except xl.ExtensionException:
                    bot.answer_callback_query(call.id, 'Ошибка!')
                    bot.send_message(message.chat.id, 'Не могу прочитать файл. Это точно экселевский файл?')

                call.message = bot.send_message(message.chat.id, 'empty')
                callback_managing(call, 'attend', course_id, back=True)
                return

        try:
            bot.edit_message_text("Загрузите .xl файл.\n/q чтобы отменить",
                                  message.chat.id, message.message_id
                                  )
        except telebot.apihelper.ApiException as ex:
            print(ex)
        bot.register_next_step_handler(message, go_go_xl)


# обработка посещений/занятий
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'classes')
def callback_class_act(call, page=0):
    message = call.message
    course_id = loads(call.data)['id']
    try:
        page = loads(call.data)['page']
    except KeyError:
        pass

    try:
        class_id = loads(call.data)['id_cl']
    except KeyError:
        class_id = loads(call.data)['cmd']

    users = [i for i in Course.Course(course_id).participants]

    for user in Course.Course(course_id).participants:
        Course.Attendance(course_id, class_id, user.id)

    p = ui.Paging(users, 7, 'name')
    markup = ui.create_markup(*[[i] for i in tbt.user_attendance(p.list(page), course_id, class_id)],
                              [cbt.backward('classes', page, class_id, course_id),
                               cbt.forward('classes', page, class_id, course_id)],
                              [tbt.invert_attendance(course_id, class_id)],
                              [cbt.back('managing', course_id, 'attend')]
                              )

    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='Список студентов. По умолчанию стоит "н".\nНажмите для изменения.'
                                   '\n* - означет, что студент не был на занятии' + p.msg(page),
                              reply_markup=markup
                              )
    except telebot.apihelper.ApiException as ex:
        print(ex)


# изменение посещения
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'sw_attend')
def callback_switch_attendance(call):
    message = call.message
    course_id = loads(call.data)['id']
    class_id = loads(call.data)['id_cl']

    try:  # для одного юзера
        user_id = loads(call.data)['id_u']
        Course.Attendance(course_id, class_id, user_id).value = \
            not Course.Attendance(course_id, class_id, user_id).value
    except KeyError:  # для всех
        for user in Course.Course(course_id).participants:
            Course.Attendance(course_id, class_id, user.id).value = \
                not Course.Attendance(course_id, class_id, user.id).value

    callback_class_act(call, True)


# вывод информации о юзере
# __не дописано
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'user')
def callback_user(call):
    message = call.message
    course_id = loads(call.data)['id']
    id_user = loads(call.data)['id_u']

    course = Course.Course(course_id)
    user = User.User(id_user)

    markup = ui.create_markup([tbt.remove_user(course_id, id_user), tbt.ban_user(course_id, id_user)],
                              [cbt.back('managing', course_id, 'parts')]
                              )
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=cfg.messages['user'].format(name=user.name, email='N/A',
                                                               mark='N/A',
                                                               abs='N/A'
                                                               ),
                              reply_markup=markup, parse_mode='Markdown'
                              )
    except telebot.apihelper.ApiException as ex:
        print(ex)


# действия над юзером в курсе
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'u_act')
def callback_user_confirm(call):
    message = call.message
    course_id = loads(call.data)['id']
    id_user = loads(call.data)['id_u']
    command = loads(call.data)['cmd']

    markup = ui.create_markup([tbt.confirm(course_id, id_user, command)],
                              [cbt.back('managing', course_id, 'parts')]
                              )

    text = ' отчислить?' if command == 'rm' else ' заблокировать?'
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='Вы уверены, что хотите'+text, reply_markup=markup)
    except telebot.apihelper.ApiException as ex:
        print(ex)


# обработка задания
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'task')
def callback_task(call, _task_id=None, _course_id=None, back=False):
    message = call.message
    if back:
        task_id = _task_id
        course_id = _course_id
    else:
        task_id = loads(call.data)['id_t']
        course_id = loads(call.data)['id']
    try:
        page = loads(call.data)['page']
    except KeyError:
        page = 0

    markup = ui.create_markup([tbt.mark_user(course_id, task_id), tbt.mark_all(course_id, task_id)],
                              [cbt.back('tasks', course_id, page)]
                              )
    msg = Course.Task(course_id, task_id).name + '\nВыберите, как вы хотите поставить оценки'
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=msg, reply_markup=markup
                              )
    except telebot.apihelper.ApiException as ex:
        print(ex)


# поставить оценки сразу всем
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'mark_a')
def callback_mark_all(call):
    message = call.message
    id_task = loads(call.data)['id_t']
    course_id = loads(call.data)['id']

    task = Course.Task(course_id, id_task)
    students = [i.id for i in Course.Course(course_id).participants]

    if len(students) == 0:
        bot.answer_callback_query(callback_query_id=call.id,
                                  text='На ваш курс никто не записан'
                                  )
        callback_course_act(call, 'mng', course_id)
        return

    def mark_all_save(marks):
        for student, mark in zip(students, marks):
            Course.Mark(course_id, id_task, student).value = int(mark) if mark != '-1' else None

        call.message = bot.send_message(message.chat.id, 'empty')
        callback_managing(call, 'task', course_id)
        return

    def mark_all_enter(msg):
        if msg.text == '/q':
            call.message = bot.send_message(message.chat.id, 'empty')
            callback_task(call)
            return
        else:
            marks = msg.text.split()

            num_marks = len(marks)
            num_students = len(students)
            if num_marks != num_students:
                bot.send_message(message.chat.id, 'Кол-во оценок({}) не совпадает с кол-вом '
                                                  'студентов({})'.format(num_marks, num_students)
                                 )
                bot.register_next_step_handler(message, mark_all_enter)
                return

            k = 1
            for mark in marks:
                if not re.fullmatch(r"-1|\d+", mark):
                    bot.send_message(message.chat.id,
                                     'Вы ввели неверный балл.\nЕго порядковый номер: ' + str(k) +
                                     '\nВведите еще раз:'
                                     )
                    bot.register_next_step_handler(message, mark_all_enter)
                    return
                elif int(mark) > task.highest_mark:
                    bot.send_message(msg.chat.id, 'Вы поставили балл выше максимума.'
                                                  '\nЕго порядковый номер: ' + str(k) +
                                                  '\nПопробуйте еще раз:')
                    bot.register_next_step_handler(msg, mark_all_enter)
                    return
                k += 1

            mark_all_save(marks)

    try:
        note = ''
        for student in students:
            if task.mark(student).value:
                note = '\n*У некоторых студентов уже есть оценки. При выполнении они буду заменены!*\n'
                break
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=cfg.messages['mark_a'].format(task=task.name,
                                                                 max=task.highest_mark,
                                                                 note=note),
                              reply_markup=None, parse_mode='Markdown'
                              )
    except telebot.apihelper.ApiException as ex:
        print(ex)
    bot.register_next_step_handler(message, mark_all_enter)


# выбор студента, чтобы поставить оценочку
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'mark_o')
def callback_mark_one(call):
    message = call.message
    try:
        id_task = loads(call.data)['id_t']
    except KeyError:
        id_task = loads(call.data)['cmd']
    course_id = loads(call.data)['id']
    try:
        page = loads(call.data)['page']
    except KeyError:
        page = 0

    course = Course.Course(course_id)
    participants = [i for i in course.participants]
    p = ui.Paging(participants, 7, 'name')
    markup = ui.create_markup(*[[i] for i in tbt.user_mark([i.id for i in p.list(page)], course_id, id_task)],
                              [cbt.backward('mark_o', page, id_task, course_id),
                               cbt.forward('mark_o', page, id_task, course_id)],
                              [cbt.back('managing', course_id, 'task')],
                              width=2
                              )
    msg = 'Выберите студента.\n* - означает, что оценка не выставлена.' + p.msg(page)

    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=msg, reply_markup=markup
                              )
    except telebot.apihelper.ApiException as ex:
        print(ex)


# ставим оценочку одному
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'mark_u_o')
def callback_mark_user_one(call):
    message = call.message
    id_task = loads(call.data)['id_t']
    course_id = loads(call.data)['id']
    id_user = loads(call.data)['id_u']

    task = Course.Task(course_id, id_task)

    def mark_user_one_enter(msg):
        if msg.text == '/q':
            pass
        elif msg.text == '-1':
            Course.Mark(course_id, id_task, id_user).value = None
        else:
            if re.fullmatch(r"[0-9]+", msg.text):
                if int(msg.text) <= task.highest_mark:
                    Course.Mark(course_id, id_task, id_user).value = int(msg.text)
                else:
                    bot.send_message(msg.chat.id, 'Вы поставили оценку выше максимума.'
                                                  '\nПопробуйте еще раз:')
                    bot.register_next_step_handler(msg, mark_user_one_enter)
                    return
            else:
                bot.send_message(msg.chat.id, 'Не понял. Повторите.')
                bot.register_next_step_handler(msg, mark_user_one_enter)
                return

        call.message = bot.send_message(message.chat.id, 'empty')
        callback_mark_one(call)

    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=cfg.messages['mark_o'].format(task=task.name,
                                                                 max=task.highest_mark,
                                                                 user=User.User(id_user).name,
                                                                 mark=task.mark(id_user).value
                                                                 ),
                              reply_markup=False, parse_mode='Markdown'
                              )
    except telebot.apihelper.ApiException as ex:
        print(ex)
    bot.register_next_step_handler(message, mark_user_one_enter)


# подтверждение
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'conf')
def callback_confirm(call):
    message = call.message
    course_id = loads(call.data)['id']
    id_user = loads(call.data)['id_u']
    command = loads(call.data)['cmd']

    course = Course.Course(course_id)

    if command == 'rm':  # отчислить юзера
        course.remove_student(id_user)
        bot.answer_callback_query(callback_query_id=call.id,
                                  text='Пользователь отчислен',
                                  )
        callback_managing(call, command, course_id)
    elif command == 'ban':  # забанить юзера
        course.append_to_blacklist(id_user)
        bot.answer_callback_query(callback_query_id=call.id,
                                  text='Пользователь заблокирован',
                                  )
        callback_managing(call, command, course_id)
    elif command == 'del_c':  # удалить курс
        course.delete()
        bot.answer_callback_query(callback_query_id=call.id,
                                  text='Курс удален',
                                  )
        menu(message, True)
    else:
        bot.send_message(message.chat.id, 'smthg went wrong\ncallback_confirm')


while True:
    try:
        bot.polling()
    except Exception:
        print(traceback.print_exc())
        time.sleep(10)

