import telebot
from json import loads
import bot_token
import UI.ui as ui
from UI.buttons import common as cbt, teacher as tbt
import UI.cfg as cfg

bot = telebot.TeleBot(bot_token.token)


@bot.message_handler(commands=['start'])
def start(message):
    # надо проверять, кто юзер
    bot.send_message(message.chat.id, cfg.messages['start'],
                     reply_markup=cfg.menu_button
                     )


@bot.message_handler(commands=['menu'])
def menu(message):
    bot.send_message(message.chat.id, cfg.messages['menu'],
                     reply_markup=cfg.markups['menu_teach']
                     )


@bot.message_handler(func=lambda message: message.text == 'Меню')
def menu_(message):
    bot.send_message(message.chat.id, cfg.messages['menu'],
                     reply_markup=cfg.markups['menu_teach']
                     )


# хендлер для кнопки "назад"
@bot.callback_query_handler(func=lambda call: loads(call.data)['type'] == 'back')
def callback_back(call):
    """Вызываются сами функции, а не изменение сообщения с новой клавиатурой.
    command - в какое меню возвращаемся, page - на какую страницу."""
    back_to = loads(call.data)['back']
    if back_to == 'menu':
        menu(call.message)
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
        if page < 0:
            page = 0
        elif page > p.last_page:
            page = p.last_page
        print(page)
        markup = ui.create_markup(*[[i] for i in cbt.course(p.list(page), 'all', page)],
                               [cbt.backward(page, command), cbt.forward(page, command)],
                               [cbt.back('menu')],
                               width=2
                               )
        msg = cfg.messages['all'] + p.msg(page)
    elif command == 'my_courses':  # получаем айди записанных курсов
        id = [1]
        p = ui.Paging(id)
        if page < 0:
            page = 0
        elif page > p.last_page:
            page = p.last_page
        markup = ui.create_markup(*[[i] for i in cbt.course(p.list(page), 'my')],
                                  [cbt.backward(page, command), cbt.forward(page, command)],
                                  [cbt.back('menu')],
                                  width=2
                                  )
        msg = cfg.messages['my'] + p.msg(page)
    elif command == 'teach_courses':  # получаем айди управляемых курсов
        id = [1]
        p = ui.Paging(id)
        if page < 0:
            page = 0
        elif page > p.last_page:
            page = p.last_page
        markup = ui.create_markup(*[[i] for i in cbt.course(p.list(page), 'teach')],
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
    # тут как-то создаю новый курс
    # пока что в главное меню
    message = call.message
    markup = cfg.markups['menu']
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text='new_course_not_available\nyou are a student now lol',
                          reply_markup=markup
                          )


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
