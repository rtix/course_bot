import configparser
import os  # ВРЕМЕННО
import time
from json import dump
from json import loads
from secrets import token_urlsafe as create_key

import telebot

import Mail
import UI.cfg as cfg
from UI.buttons import common as cbt, teacher as tbt
from UI.cfg import ui

sets = configparser.ConfigParser()
sets.read('settings.cfg')

if not Mail.check_valid(sets['mail']['email']):
    raise Mail.WrongEMail("Неправильный email в файле настроек.")
email = Mail.Mail(sets['mail']['email'], sets['mail']['password'])
bot = telebot.TeleBot(sets['bot']['token'])


@bot.message_handler(commands=['s'])
def s(message):
    bot.send_message(message.chat.id, 'super_menu',
                     reply_markup=cfg.markups['menu_teach']
                     )


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, cfg.messages['start'])


@bot.message_handler(commands=['menu'])
def menu(message, edit=False):
    # если не зарегистрирован
    if edit:
        if not os.path.exists('fictionDB/users/' + str(message.chat.id)):  # ВРЕМЕННО
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text='Для пользования необходимо зарегистрироваться',
                                  reply_markup=ui.create_markup([cbt.registration])
                                  )
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text=cfg.messages['menu'],
                                  reply_markup=cfg.markups['menu_teach']
                                  )
    else:
        if not os.path.exists('fictionDB/users/' + str(message.chat.id)):  # ВРЕМЕННО
            bot.send_message(message.chat.id, 'Для пользования необходимо зарегистрироваться',
                             reply_markup=ui.create_markup([cbt.registration])
                             )
        else:
            bot.send_message(message.chat.id, cfg.messages['menu'],
                             reply_markup=cfg.markups['menu_teach']
                             )


# регистрация
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'reg')
def registration(call):
    # если уже есть в базе, то это хитрец
    message = call.message
    if os.path.exists('fictionDB/users/' + str(message.chat.id)):
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
            open('fictionDB/users/' + str(msg.from_user.id), 'w').close()
            bot.send_message(msg.chat.id, '*----Регистрация завершена----*',
                             parse_mode='Markdown'
                             )
            menu(msg)
        else:
            bot.send_message(msg.chat.id, 'Неправильный код подтверждения.\n'
                                          'Делай все заново, потому что лень иначе'
                             )
            menu(msg)

    # отправка письма
    def registration_mail(msg):
        try:
            # проверяю имя почты
            mail = msg.text.casefold().strip()
            if not Mail.check_valid(mail):
                raise Mail.WrongEMail('Неправильное имя почты.\nПопробуйте еще раз.'
                                      '\n/q чтобы отменить'
                                      )

            # создаю код и отправляю письмо
            passkey = create_key(3)
            # если успешно отправлено
            if email.send(mail, 'Рега в нашем боте йооо', cfg.messages['reg_mail'] + passkey):
                bot.send_message(msg.chat.id, 'Письмо отправлено.\n'
                                              'Проверьте спам там даа.\n'
                                              'Введите код регистрации:'
                                 )
                bot.register_next_step_handler(msg, registration_pass, passkey)
            else:
                bot.send_message(msg.chat.id, 'something wrong. try again later')
        # если неправильно имя почты
        except Mail.WrongEMail as err:
            # пользователь захотел прекратить регу
            if msg.text == '/q':
                bot.send_message(msg.chat.id, '*----Регистрация отменена----*',
                                 parse_mode='Markdown'
                                 )
                menu(msg)
            # неправильная почта
            else:
                bot.send_message(msg.chat.id, err.msg)
                bot.register_next_step_handler(msg, registration_mail)

    # начало регистрации
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text='*----Начата регистрация----*', parse_mode='Markdown')
    bot.send_message(message.chat.id, 'Напишите Ваше мыло\n/q чтобы отменить')
    bot.register_next_step_handler(message, registration_mail)


# хендлер для кнопки "назад"
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'back')
def callback_back(call):
    """Вызываются сами функции, а не изменение сообщения с новой клавиатурой.
    command - в какое меню возвращаемся, page - на какую страницу."""

    back_to = loads(call.data)['back']
    if back_to == 'menu':
        menu(call.message, True)
    elif back_to == 'all':
        callback_menu(call, command='all_courses', page=int(loads(call.data)['page']))
    elif back_to == 'my':
        callback_menu(call, command='my_courses', page=int(loads(call.data)['page']))
    elif back_to == 'teach':
        callback_menu(call, command='teach_courses', page=int(loads(call.data)['page']))


# меню // кнопки для "Все курсы" и "Мои курсы"
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'menu')
def callback_menu(call, command=None, page=0):
    """Выводится список курсов по командам all, my, teach.

    Аргумент по умолчанию command нужен для кнопки "назад". В его хендлере
    указывается параметр, чтобы знать, куда нужно возвращаться. Если не был указан,
    то значит - команда была вызвана кнопкой из главного меню.
    page нужен, чтобы знать, на какую страницу возвращаться. Если не был указан,
    то значит - команда была вызвана кнопкой из главного меню."""

    if not command:
        command = loads(call.data)['command']
        page = int(loads(call.data)['page'])
    message = call.message

    # если что-то пошло не так. но вообще, не должно быть
    markup = cfg.err_markup
    msg = cfg.err_msg
    ##

    # по сути, мне должны дать список айдишников курсов
    if command == 'all_courses':  # получаем айди всех курсов
        id = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        p = ui.Paging(id)
        markup = ui.create_markup(*[[i] for i in cbt.course(p.list(page), 'all', page)],
                                  [cbt.backward(page, command), cbt.forward(page, command)],
                                  [cbt.back('menu')],
                                  width=2
                                  )
        msg = cfg.messages['all'] + p.msg(page)
    elif command == 'my_courses':  # получаем айди записанных курсов
        id = [1]
        p = ui.Paging(id)
        markup = ui.create_markup(*[[i] for i in cbt.course(p.list(page), 'my', page)],
                                  [cbt.backward(page, command), cbt.forward(page, command)],
                                  [cbt.back('menu')],
                                  width=2
                                  )
        msg = cfg.messages['my'] + p.msg(page)
    elif command == 'teach_courses':  # получаем айди управляемых курсов
        id = [1]
        p = ui.Paging(id)
        markup = ui.create_markup(*[[i] for i in cbt.course(p.list(page), 'teach', page)],
                                  [cbt.backward(page, command), cbt.forward(page, command)],
                                  [cbt.back('menu')],
                                  width=2
                                  )
        msg = cfg.messages['teach'] + p.msg(page)

    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=msg, reply_markup=markup
                              )
    except telebot.apihelper.ApiException:
        pass


# создаю новый курс
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'new_course')
def callback_new_course(call):
    # __ проверка, что учитель

    message = call.message

    # сохранение
    def new_course_save(msg):
        dump(course_info, open('fictionDB/courses/' + course_info['name'], 'w'))
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
        elif msg.text == 'name':
            course_info['name'] = ''
            bot.send_message(message.chat.id, 'Напишите название курса\n/q чтобы отменить')
            bot.register_next_step_handler(msg, new_course_name, edit=True)
        elif msg.text == 'desc':
            course_info['desc'] = ''
            bot.send_message(msg.chat.id, 'Напишите описание курса (необязательно).\n'
                                          '/p чтобы пропустить этот шаг\n/q чтобы отменить'
                             )
            bot.register_next_step_handler(msg, new_course_description, edit=True)
        elif msg.text == 'lock':
            course_info['lock'] = 0
            bot.send_message(msg.chat.id, 'Напишите в течение скольки дней будет доступна '
                                          'запись на курс (необязательно).\n'
                                          '0 или /p чтобы пропустить этот шаг\n/q чтобы отменить'
                             )
            bot.register_next_step_handler(msg, new_course_lock)
        elif msg.text == '/g':
            new_course_save(msg)
        else:
            bot.send_message(msg.chat.id, 'Не понял. Повтори.\n')
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
                    utime = int(msg.text)
                    if utime != 0:
                        course_info['lock'] = time.time() + (utime * 24 * 60 * 60)
                except ValueError:
                    bot.send_message(msg.chat.id, 'Не понял. Повтори.\n')
                    bot.register_next_step_handler(msg, new_course_lock)

            lock = time.strftime("%d %b %Y", time.localtime(course_info['lock']))
            if course_info['lock'] == 0:
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
                if course_info['lock'] == 0:
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
            course_info['name'] = msg.text

            if edit:
                lock = time.strftime("%d %b %Y", time.localtime(course_info['lock']))
                if course_info['lock'] == 0:
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
    course_info = dict(owner_id=message.chat.id, name='', desc='', lock=0)

    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text='*----Начато создание курса----*', parse_mode='Markdown')
    bot.send_message(message.chat.id, 'Напишите название курса\n/q чтобы отменить')
    bot.register_next_step_handler(message, new_course_name)


# вывод информации о курсе
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'courses')
def callback_courses(call):
    command = loads(call.data)['command']
    back_to = loads(call.data)['prev']
    message = call.message

    # тут должен быть запрос к бд
    # взять инфу о курсе, преподе и тд
    # примерно: get_info_course(command), command будет айдишником курса

    # if 'учитель этого курса':
    #     markup = create([tbt.manage])
    # else:
    #     if 'записан':
    #         markup = create([cbt.leave])
    #     else:
    #         markup = create([cbt.enroll])

    # на время вывожу все команды
    markup = ui.create_markup([cbt.enroll], [cbt.leave], [tbt.manage],
                              [cbt.back(back_to, loads(call.data)['page'])])
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text='course_info', reply_markup=markup)


# обработка записаться и управление курса
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'a_course')
def callback_a_course(call):
    command = loads(call.data)['command']
    message = call.message

    if command == 'enroll':
        # записываемся как-то

        # пока что в главное меню
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='enroll_not_available',
                              reply_markup=cfg.markups['menu_teach'])
    elif command == 'leave':
        # отписываемся как-то

        # пока что в главное меню
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='leave_not_available',
                              reply_markup=cfg.markups['menu_teach'])
    elif command == 'manage':
        # проверяем разрешение if user is teacher
        # ...

        # пока что в главное меню
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text='manage_not_available',
                              reply_markup=cfg.markups['menu_teach'])


bot.polling()
