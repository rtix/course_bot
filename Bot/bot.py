import datetime
import json
import re
import time

from telebot.apihelper import ApiException as TBotApiException

import UI
from Bot import botHelper, bot
from Bot.util import (
    action,
    get_confirm_message,
    get_lang,
    goto,
    quick_action,
    save_user_movement
)
from Models import Course
from Models import User
from UI import markup as mkp
from UI import messages as msgs
from UI.buttons import common as cbt
from UI.buttons import teacher as tbt


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
        botHelper.edit_mes(text, call, markup=mkp.create_confirm(get_lang(call.message.chat.id), call.data))


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

        text = msgs[get_lang(chat_id)]['teacher']['course_create']['new_course'].format(
            name=course_info['name'], desc=course_info['desc'], lock=t, create=c
        )

        msg = botHelper.send_mes(text, chat_id)
        bot.register_next_step_handler(msg, get_user_command)

    def name(message):
        length = len(message.text)
        if UI.constants.COURSE_NAME_LENGTH_MIN <= length <= UI.constants.COURSE_NAME_LENGTH_MAX:
            course_info['name'] = message.text
            idle()
        else:
            botHelper.send_mes(msgs[lang]['teacher']['course_create']['error_name_length'], chat_id)
            message.text = '/name'
            get_user_command(message)

    def desc(message):
        length = len(message.text)
        if UI.constants.COURSE_DESC_LENGTH_MIN <= length <= UI.constants.COURSE_DESC_LENGTH_MAX:
            course_info['desc'] = message.text
            idle()
        else:
            botHelper.send_mes(msgs[lang]['teacher']['course_create']['error_desc_length'], chat_id)
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
            botHelper.send_mes(msgs[lang]['common']['wrong_input'], chat_id)
            message.text = '/lock'
            get_user_command(message)

    def get_user_command(message):
        if message.text == '/name':
            text = msgs[lang]['teacher']['course_create']['name_input'].format(
                UI.constants.COURSE_NAME_LENGTH_MIN,
                UI.constants.COURSE_NAME_LENGTH_MAX
            )

            botHelper.send_mes(text, chat_id)
            bot.register_next_step_handler(message, name)
        elif message.text == '/desc':
            text = msgs[lang]['teacher']['course_create']['desc_input'].format(
                UI.constants.COURSE_DESC_LENGTH_MIN,
                UI.constants.COURSE_DESC_LENGTH_MAX
            )

            botHelper.send_mes(text, chat_id)
            bot.register_next_step_handler(message, desc)
        elif message.text == '/lock':
            text = msgs[lang]['teacher']['course_create']['lock_input']

            botHelper.send_mes(text, chat_id)
            bot.register_next_step_handler(message, lock)
        elif message.text == '/create':
            if not course_info['name'] or not course_info['desc']:
                botHelper.send_mes(msgs[lang]['teacher']['course_create']['name_and_desc'], chat_id)
                bot.register_next_step_handler(message, get_user_command)
            else:
                c = Course.Course(owner_id=chat_id, name=course_info['name'])
                c.description = course_info['desc']
                c.entry_restriction = course_info['lock']

                botHelper.send_mes(msgs[lang]['teacher']['course_create']['created'], chat_id)
                menu_command(message)
        elif message.text == '/exit':
            botHelper.send_mes(msgs[lang]['teacher']['course_create']['canceled'], chat_id)
            menu_command(message)
        else:
            botHelper.send_mes(msgs[lang]['teacher']['course_create']['wrong_command'], chat_id)
            bot.register_next_step_handler(message, get_user_command)

    lang = get_lang(chat_id)
    creating = {
        'valid': msgs[lang]['teacher']['course_create']['creating_valid'],
        'name': msgs[lang]['teacher']['course_create']['creating_name'],
        'desc': msgs[lang]['teacher']['course_create']['creating_desc'],
        'both': msgs[lang]['teacher']['course_create']['creating_both']
    }
    course_info = dict(name=None, desc=None, lock=None)
    idle()


@bot.message_handler(commands=['start'])
def start(message):
    botHelper.send_mes(msgs[get_lang(message.chat.id)]['common']['start'], message.chat.id)


@bot.message_handler(commands=['registration'])
def registration(message):
    def name(msg):
        if re.fullmatch(r"[a-zA-Zа-яА-Я]+ [a-zA-Zа-яА-Я ]+", msg.text):
            user.name = msg.text

            menu_command(msg)
        else:
            botHelper.send_mes(msgs[lang]['common']['registration']['wrong_name'], message.chat.id)
            bot.register_next_step_handler(message, name)

    lang = get_lang(message.chat.id)

    if User.User(message.chat.id).type_u == 'unlogined':
        try:
            user = User.User(id=message.chat.id, username=message.from_user.username, name='noname')
            botHelper.send_mes(msgs[lang]['common']['registration']['teacher'], message.chat.id)
        except User.TeacherAccessDeniedError:
            user = User.User(id=message.chat.id, name='noname', group='1', email='qwe@qwe.qwe')
            botHelper.send_mes(msgs[lang]['common']['registration']['mere_human'], message.chat.id)

        botHelper.send_mes(msgs[lang]['common']['registration']['input'], message.chat.id)
        bot.register_next_step_handler(message, name)
    else:
        botHelper.send_mes(msgs[lang]['common']['registration']['already'], message.chat.id)


@bot.message_handler(commands=['menu'])
def menu_command(message):
    lang = get_lang(message.chat.id)

    if User.User(message.chat.id).type_u == 'unlogined':
        botHelper.send_mes(msgs[lang]['common']['new_user'], message.chat.id)
    else:
        if User.User(message.chat.id).type_u == 'student':
            markup = mkp.create(
                lang,
                [cbt.course_list_of('all', lang), cbt.course_list_of('my', lang)],
                include_back=False
            )

            botHelper.send_mes(
                msgs[get_lang(message.chat.id)]['common']['menu'],
                message.chat.id,
                markup=markup
            )
        else:
            markup = mkp.create(
                lang,
                [cbt.course_list_of('all', lang), cbt.course_list_of('my', lang)],
                [tbt.manage_list(lang)], [tbt.new_course(lang)],
                include_back=False
            )

            botHelper.send_mes(
                msgs[get_lang(message.chat.id)]['common']['menu'],
                message.chat.id,
                markup=markup
            )


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'menu')
def menu(call):
    lang = get_lang(call.message.chat.id)

    if User.User(call.message.chat.id).type_u == 'student':
        markup = mkp.create(
            lang,
            [cbt.course_list_of('all', lang), cbt.course_list_of('my', lang)],
            include_back=False
        )

        botHelper.edit_mes(
            msgs[lang]['common']['menu'],
            call,
            markup=markup
        )
    else:
        markup = mkp.create(
            lang,
            [cbt.course_list_of('all', lang), cbt.course_list_of('my', lang)],
            [tbt.manage_list(lang)], [tbt.new_course(lang)],
            include_back=False
        )

        botHelper.edit_mes(
            msgs[lang]['common']['menu'],
            call,
            markup=markup
        )


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'new_course')
def new_course(call):
    botHelper.edit_mes(msgs[get_lang(call.message.chat.id)]['teacher']['course_create']['begin'], call)
    create_course(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course_list')
@action
def course_list(call, lang):
    if call.data['type'] == 'all':  # TODO не добавлять закрытые курсы
        courses = [i for i in Course.fetch_all_courses()]
        text = msgs[lang]['common']['all']
    elif call.data['type'] == 'my':
        courses = [i for i in User.User(call.message.chat.id).participation]
        text = msgs[lang]['common']['my']
    elif call.data['type'] == 'teach':
        courses = [i for i in User.User(call.message.chat.id).possessions]
        text = msgs[lang]['common']['teach']
    else:
        botHelper.error(call=call)
        return
    page = call.data['page']

    p = UI.Paging(courses, sort_key='name')
    text += p.msg(call.data['page'], lang)
    if call.data['type'] == 'teach':
        markup = mkp.create_listed(lang, tbt.courses(p.list(page)), tbt.manage_list, lang, page)
    else:
        markup = mkp.create_listed(
            lang,
            cbt.courses(p.list(page)),
            cbt.course_list_of,
            call.data['type'],
            lang, page
        )
    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course')
@action
def course(call, lang):
    course_ = Course.Course(call.data['c_id'])
    num_par = len(course_.participants)
    owner = course_.owner

    if owner.id == call.message.chat.id:  # owner
        if course_.is_open:
            lock = msgs[lang]['teacher']['lock_open']
        else:
            lock = msgs[lang]['teacher']['lock_close']
        desc = course_.description
        if len(desc) > UI.constants.COURSE_INFO_DESC_LENGTH:
            desc = botHelper.remove_danger(desc[:UI.constants.COURSE_INFO_DESC_LENGTH]) + '...'

        botHelper.edit_mes(
            msgs[lang]['teacher']['course_owner_min'].format(
                name=course_.name, num=num_par, lock=lock, desc=desc
            ),
            call,
            markup=mkp.create(lang, [tbt.manage(call.data['c_id'], lang)])
        )
    elif course_.id in (c.id for c in User.User(call.message.chat.id).participation):  # enrolled
        cws = course_.classworks
        attend_text = ''
        overall = len(cws)
        if overall:
            att = sum(map(lambda cw_: cw_.attendance(call.message.chat.id).value, cws))
            attend_text = msgs[lang]['student']['attendance'].format(
                count=att,
                overall=overall,
                ratio=int(att / overall * 100)
            )

        tasks = course_.tasks
        if tasks:
            total_mark = sum(map(lambda task_: task_.mark(call.message.chat.id).value, tasks))
            mean_mark = total_mark / len(tasks)
            mark_text = msgs[lang]['student']['marks'].format(total_mark, round(mean_mark, 2))
        else:
            mark_text = ''

        text = msgs[lang]['student']['course'].format(
            name=course_.name, fio=owner.name, num=num_par, mail='', marks=mark_text, attend=attend_text
        )

        c_text = msgs[lang]['confirm']['leave_course'].format(course_.name)
        if not course_.is_open:
            c_text += msgs[lang]['confirm']['leave_course_append']

        markup = mkp.create(
            lang,
            [cbt.task_list(call.data['c_id'], lang)],
            [cbt.confirm_action(
                'leave',
                msgs[lang]['buttons']['confirm']['leave'],
                c_text,
                call.message.chat.id,
                call.message.message_id,
                c_id=course_.id
            )]
        )

        botHelper.edit_mes(text, call, markup=markup)
    else:  # not enrolled
        locked = '' if course_.is_open else msgs[lang]['student']['course_closed']
        end_entry = course_.entry_restriction
        lock = UI.to_dtime(end_entry) if end_entry else msgs[lang]['student']['lock_absent']

        text = msgs[lang]['student']['course_not_enroll'].format(
            name=course_.name, fio=owner.name, desc=course_.description, num=num_par, lock=lock, mail='', locked=locked
        )  # TODO mail

        c_text = msgs[lang]['confirm']['enroll_course'].format(course_.name)

        if locked:
            markup = mkp.create(lang)
        else:
            markup = mkp.create(
                lang,
                [cbt.confirm_action(
                        'enroll',
                        msgs[lang]['buttons']['confirm']['enroll'],
                        c_text,
                        call.message.chat.id,
                        call.message.message_id,
                        c_id=course_.id
                )]
            )

        botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'st_task_list')
@action
def st_task_list(call, lang):
    p = UI.Paging(Course.Course(call.data['c_id']).tasks, sort_key='name')

    text = msgs[lang]['student']['task_list'] + p.msg(call.data['page'], lang)

    markup = mkp.create_listed(
        lang,
        cbt.tasks(p.list(call.data['page'])),
        cbt.task_list,
        call.data['c_id'], lang, call.data['page']
    )

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'st_tsk')
@action
def st_tsk(call, lang):
    task_ = Course.Task(call.data['c_id'], call.data['t_id'])
    text = msgs[lang]['student']['student_task'].format(
        name=task_.name,
        desc=task_.description,
        mark=task_.mark(call.message.chat.id).value,
        hmark=int(task_.highest_mark)
    )

    botHelper.edit_mes(text, call, markup=mkp.create(lang))


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'course_owner')
@action
def course_owner(call, lang):
    course_ = Course.Course(call.data['c_id'])

    text = msgs[lang]['teacher']['course_owner_full'].format(
        name=course_.name,
        num=len(course_.participants),
        lock=UI.to_dtime(course_.entry_restriction),
        desc=course_.description
    )
    c_text = msgs[lang]['confirm']['delete_course'].format(course_.name)
    markup = mkp.create(
        lang,
        [tbt.user_list(call.data['c_id'], lang)],
        [tbt.task_list(call.data['c_id'], lang)],
        [tbt.classwork_list(call.data['c_id'], lang)],
        [tbt.announce(call.data['c_id'], lang)],
        [tbt.switch_lock(call.data['c_id'], True if course_.is_open else False, lang)],
        [cbt.confirm_action(
            'delete_course',
            msgs[lang]['buttons']['confirm']['delete_course'],
            c_text,
            call.message.chat.id,
            call.message.message_id,
            c_id=course_.id
        )]
    )

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'class_list')
@action
def class_list(call, lang):
    classworks = Course.Course(call.data['c_id']).classworks

    p = UI.Paging(classworks, sort_key='date')

    text = msgs[lang]['teacher']['management']['class_list'] + p.msg(call.data['page'], lang)

    markup = mkp.create_listed(
        lang,
        tbt.classworks(p.list(call.data['page'])),
        tbt.classwork_list,
        call.data['c_id'], lang, call.data['page']
    )
    mkp.add_before_back(markup, tbt.new_classwork(call.data['c_id'], lang))

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'cw')
@action
def cw(call, lang):
    course_ = Course.Course(call.data['c_id'])
    classwork = course_.classwork(call.data['cw_id'])

    p = UI.Paging(course_.participants, sort_key='name')

    text = msgs[lang]['teacher']['management']['classwork'].format(date=classwork.date) + p.msg(call.data['page'], lang)

    c_text = msgs[lang]['confirm']['delete_class'].format(classwork.name)

    markup = mkp.create_listed(
        lang,
        tbt.user_attendance_list(p.list(call.data['page']), call.data['c_id'], call.data['cw_id']),
        tbt.classwork,
        call.data['c_id'], call.data['cw_id'], lang, call.data['page']
    )
    mkp.add_before_back(markup, tbt.invert_attendance(call.data['c_id'], call.data['cw_id'], lang))
    mkp.add_before_back(markup, tbt.change_cw_date(call.data['c_id'], call.data['cw_id'], lang))
    mkp.add_before_back(markup, cbt.confirm_action(
        'del_class',
        msgs[lang]['buttons']['confirm']['del_class'],
        c_text,
        call.message.chat.id,
        call.message.message_id,
        c_id=call.data['c_id'], cw_id=call.data['cw_id']
    ))

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'task_list')
@action
def task_list(call, lang):
    tasks = Course.Course(call.data['c_id']).tasks

    p = UI.Paging(tasks, sort_key='name')

    text = msgs[lang]['teacher']['management']['task_list'] + p.msg(call.data['page'], lang)

    markup = mkp.create_listed(
        lang,
        tbt.tasks(p.list(call.data['page'])),
        tbt.task_list,
        call.data['c_id'], lang, call.data['page']
    )
    mkp.add_before_back(markup, tbt.new_task(call.data['c_id'], lang))

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'task')
@action
def task(call, lang):
    course_ = Course.Course(call.data['c_id'])
    task_ = course_.task(call.data['t_id'])

    p = UI.Paging(course_.participants, sort_key='name')

    text = msgs[lang]['teacher']['management']['task'].format(name=task_.name, hmark=int(task_.highest_mark)) \
        + p.msg(call.data['page'], lang)

    c_text = msgs[lang]['confirm']['delete_task'].format(task_.name)

    markup = mkp.create_listed(
        lang,
        tbt.user_tasks_list(p.list(call.data['page']), call.data['c_id'], call.data['t_id']),
        tbt.task,
        call.data['c_id'], call.data['t_id'], lang, call.data['page']
    )
    mkp.add_before_back(markup, cbt.confirm_action(
        'del_task',
        msgs[lang]['buttons']['confirm']['del_task'],
        c_text,
        call.message.chat.id,
        call.message.message_id,
        c_id=call.data['c_id'], t_id=call.data['t_id']
    ))

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'user_list')
@action
def user_list(call, lang):
    p = UI.Paging(Course.Course(call.data['c_id']).participants, sort_key='name')

    text = msgs[lang]['teacher']['management']['user_list'] + p.msg(call.data['page'], lang)

    markup = mkp.create_listed(
        lang,
        tbt.users(p.list(call.data['page']), call.data['c_id']),
        tbt.user_list,
        call.data['c_id'], lang, call.data['page']
    )

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'usr_mng')
@action
def usr_mng(call, lang):
    course_ = Course.Course(call.data['c_id'])
    tasks = course_.tasks
    user = User.User(call.data['u_id'])
    cws = course_.classworks

    if tasks:
        total_mark = sum(filter(None, map(lambda x: x.mark(call.data['u_id']).value, tasks)))
        mean_mark = total_mark / len(tasks)
    else:
        total_mark = None
        mean_mark = None

    if cws:
        overall = len(cws)
        att = sum(map(lambda cw_: cw_.attendance(call.data['u_id']).value, cws))
    else:
        overall = None
        att = None

    text = msgs[lang]['teacher']['management']['user'].format(
        course=course_.name,
        name=user.name,
        email='',
        mean=mean_mark,
        total=total_mark,
        attend=att,
        attend_tot=overall
    )

    c_text = msgs[lang]['confirm']['kick'].format(user.name)

    markup = mkp.create(
        lang,
        [
            cbt.confirm_action(
                'kick',
                msgs[lang]['buttons']['confirm']['kick'],
                c_text,
                call.message.chat.id,
                call.message.message_id,
                c_id=call.data['c_id'], u_id=call.data['u_id']
            )
        ]
    )

    botHelper.edit_mes(text, call, markup=markup)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'enroll')
@quick_action
def enroll(call, lang):
    if call.data['c_id'] not in (c.id for c in User.User(call.message.chat.id).participation):
        c = Course.Course(call.data['c_id'])
        c.append_student(call.message.chat.id)
        bot.answer_callback_query(call.id, msgs[lang]['callback']['course_enrolled'] + c.name)
    else:
        bot.answer_callback_query(call.id, msgs[lang]['callback']['course_enrolled_already'], show_alert=True)

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'leave')
@quick_action
def leave(call, lang):
    if call.data['c_id'] in (c.id for c in User.User(call.message.chat.id).participation):
        c = Course.Course(call.data['c_id'])
        c.remove_student(call.message.chat.id)
        bot.answer_callback_query(call.id, msgs[lang]['callback']['course_leave'] + c.name)
    else:
        bot.answer_callback_query(call.id, msgs[lang]['callback']['course_not_enrolled'], show_alert=True)

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'delete_course')
@quick_action
def delete_course(call, lang):
    course_ = Course.Course(call.data['c_id'])

    if call.message.chat.id == course_.owner.id:
        course_.delete()
        bot.answer_callback_query(call.id, msgs[lang]['callback']['course_deleted'])
    else:
        bot.answer_callback_query(call.id, msgs[lang]['callback']['not_owner'], show_alert=True)

    back(call, True, 2)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'switch_lock')
@quick_action
def switch_lock(call, lang):
    if call.data['lock']:
        Course.Course(call.data['c_id']).entry_restriction = time.time()
        bot.answer_callback_query(call.id, msgs[lang]['callback']['course_closed'])
    else:
        Course.Course(call.data['c_id']).entry_restriction = None
        bot.answer_callback_query(call.id, msgs[lang]['callback']['course_opened'])

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'announce')
def announce(call):
    def return_to_menu():
        new_mes = botHelper.send_mes('empty', call.message.chat.id)
        botHelper.renew_menu(call, new_mes)
        back(call, True)

    def cancel():
        botHelper.send_mes(msgs[lang]['teacher']['announce']['cancel'])
        return_to_menu()

    def send():
        course_ = Course.Course(call.data['c_id'])

        for part in course_.participants:
            try:
                botHelper.send_mes(
                    msgs[lang]['teacher']['announce']['got_announce'].format(
                        course_.name
                    ),
                    part.id
                )
                botHelper.send_mes(announce_info['text'], part.id)
                for file, caption in zip(announce_info['file'], announce_info['file_caption']):
                    bot.send_document(part.id, file, caption=caption)
            except TBotApiException:
                continue

        botHelper.send_mes(
            msgs[lang]['teacher']['announce']['sent'],
            call.message.chat.id
        )

        return_to_menu()

    def get_file(message):
        if message.text == '/exit':
            cancel()
        elif message.text == '/send':
            send()
        else:
            if message.document:
                announce_info['file'].append(message.document.file_id)
                announce_info['file_caption'].append(message.caption)
                bot.register_next_step_handler(message, get_file)

    def get_text(message):
        if message.text == '/exit':
            cancel()
        else:
            announce_info['text'] = message.text

            botHelper.send_mes(msgs[lang]['teacher']['announce']['files'], call.message.chat.id)
            bot.register_next_step_handler(message, get_file)

    call.data = json.loads(call.data)
    lang = get_lang(call.message.chat.id)
    announce_info = {'text': '', 'file': [], 'file_caption': []}

    botHelper.edit_mes(msgs[lang]['teacher']['announce']['begin'], call)
    botHelper.send_mes(msgs[lang]['teacher']['announce']['input_text'], call.message.chat.id)
    bot.register_next_step_handler(call.message, get_text)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'new_class')
@quick_action
def new_class(call, lang):
    d = UI.to_dtime(time.time())
    cw_id = Course.Classwork(call.data['c_id'], name=d, date=d).number
    for user in Course.Course(call.data['c_id']).participants:
        Course.Attendance(call.data['c_id'], cw_id, user.id).value = 0

    back(call, True)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'del_class')
@quick_action
def del_class(call, lang):
    if call.message.chat.id == Course.Course(call.data['c_id']).owner.id:
        Course.Classwork(call.data['c_id'], call.data['cw_id']).delete()
        bot.answer_callback_query(call.id, msgs[lang]['callback']['class_deleted'])
    else:
        bot.answer_callback_query(call.id, msgs[lang]['callback']['class_not_exists'], show_alert=True)

    back(call, True, 2)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'attend')
@quick_action
def attend(call, lang):
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

    def cancel():
        botHelper.send_mes(
            msgs[lang]['teacher']['task_create']['canceled'],
            call.message.chat.id
        )
        return_to_menu()

    def create():
        name = task_info['name']
        if not name:
            name = msgs[lang]['teacher']['task_create']['name'] + str(len(Course.Course(call.data['c_id']).tasks) + 1)

        Course.Task(
            course_id=call.data['c_id'],
            name=name,
            description=task_info['desc'].format(task_info['hmark']),
            highest_mark=task_info['hmark']
        )

        botHelper.send_mes(
            msgs[lang]['teacher']['task_create']['created'],
            call.message.chat.id
        )
        return_to_menu()

    def get_hmark(message):
        if message.text == '/exit':
            cancel()
        else:
            if message.text != '0' and re.fullmatch(r'\d+', message.text):
                task_info['hmark'] = int(message.text)

                create()
            else:
                botHelper.send_mes(msgs[lang]['teacher']['task_create']['error_max_mark'], call.message.chat.id)
                bot.register_next_step_handler(message, get_hmark)

    def get_desc(message):
        if message.text == '/exit':
            cancel()
        else:
            if len(message.text) <= UI.constants.TASK_DESC_MAX_LENGTH:
                if message.text != '/no':
                    task_info['desc'] += message.text

                botHelper.send_mes(msgs[lang]['teacher']['task_create']['input_max_mark'], call.message.chat.id)
                bot.register_next_step_handler(message, get_hmark)
            else:
                botHelper.send_mes(
                    msgs[lang]['teacher']['task_create']['error_length'].format(UI.constants.TASK_DESC_MAX_LENGTH),
                    call.message.chat.id
                )
                bot.register_next_step_handler(message, get_desc)

    def get_name(message):
        if message.text == '/exit':
            cancel()
            return_to_menu()
        else:
            if len(message.text) <= UI.constants.TASK_NAME_MAX_LENGTH:
                if message.text != '/no':
                    task_info['name'] = message.text

                botHelper.send_mes(msgs[lang]['teacher']['task_create']['input_desc'], call.message.chat.id)
                bot.register_next_step_handler(message, get_desc)
            else:
                botHelper.send_mes(
                    msgs[lang]['teacher']['task_create']['error_length'].format(UI.constants.TASK_NAME_MAX_LENGTH),
                    call.message.chat.id
                )
                bot.register_next_step_handler(message, get_name)

    call.data = json.loads(call.data)
    lang = get_lang(call.message.chat.id)
    task_info = {'name': '', 'desc': msgs[lang]['teacher']['task_create']['max_mark'], 'hmark': 0}

    botHelper.edit_mes(msgs[lang]['teacher']['task_create']['begin'], call)
    botHelper.send_mes(msgs[lang]['teacher']['task_create']['input_name'], call.message.chat.id)
    bot.register_next_step_handler(call.message, get_name)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'del_task')
@quick_action
def del_task(call, lang):
    if call.message.chat.id == Course.Course(call.data['c_id']).owner.id:
        Course.Task(call.data['c_id'], call.data['t_id']).delete()
        bot.answer_callback_query(call.id, msgs[lang]['callback']['task_deleted'])
    else:
        bot.answer_callback_query(call.id, msgs[lang]['callback']['task_not_exists'], show_alert=True)

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
                botHelper.send_mes(msgs[get_lang(call.message.chat.id)]['teacher']['management']['error_mark'])
                bot.register_next_step_handler(message, get_mark)
        else:
            botHelper.send_mes(msgs[get_lang(call.message.chat.id)]['teacher']['management']['wrong_input'])
            bot.register_next_step_handler(message, get_mark)

    call.data = json.loads(call.data)
    task_ = Course.Task(call.data['c_id'], call.data['t_id'])
    mark = Course.Mark(call.data['c_id'], call.data['t_id'], call.data['u_id'])

    text = msgs['mark_one'].format(
        task=task_.name,
        user=User.User(call.data['u_id']).name,
        mark=mark.value,
        max=task_.highest_mark
    )

    botHelper.edit_mes(text, call)
    bot.register_next_step_handler(call.message, get_mark)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'kick')
@quick_action
def kick(call, lang):
    course_ = Course.Course(call.data['c_id'])

    if User.User(call.message.chat.id).type_u == 'teacher':
        if course_.id in (c.id for c in User.User(call.data['u_id']).participation):
            course_.remove_student(call.data['u_id'])
            bot.answer_callback_query(call.id, msgs[lang]['callback']['student_kicked'].format(
                name=User.User(call.data['u_id']).name
            ))
        else:
            bot.answer_callback_query(call.id, msgs[lang]['callback']['student_not_enrolled'], show_alert=True)
    else:
        bot.answer_callback_query(call.id, msgs[lang]['callback']['not_teacher'], show_alert=True)

    back(call, True, 2)


@bot.callback_query_handler(func=lambda call: goto(call.data) == 'cw_date')
def cw_date(call):
    def return_to_menu():
        new_mes = botHelper.send_mes('empty', call.message.chat.id)
        botHelper.renew_menu(call, new_mes)
        back(call, True)

    def get_date(message):
        if message.text == '/exit':
            return_to_menu()
        elif re.fullmatch(r'\d{1,2}\s\d{1,2}\s\d{1,2}', message.text):
            in_date = message.text.split()
            cw_ = Course.Classwork(call.data['c_id'], call.data['cw_id'])

            try:
                date = datetime.date(2000 + int(in_date[0]), int(in_date[1]), int(in_date[2])).strftime('%d %b %Y')
            except ValueError:
                botHelper.send_mes(
                    msgs[get_lang(call.message.chat.id)]['teacher']['management']['wrong_input'],
                    message.messasge_id
                )
                bot.register_next_step_handler(message, get_date)
            else:
                cw_.date = date
                cw_.name = date

                return_to_menu()
        else:
            botHelper.send_mes(
                msgs[get_lang(call.message.chat.id)]['teacher']['management']['wrong_input'],
                message.messasge_id
            )
            bot.register_next_step_handler(message, get_date)

    call.data = json.loads(call.data)

    botHelper.edit_mes(msgs[get_lang(call.message.chat.id)]['teacher']['management']['input_date'], call)
    bot.register_next_step_handler(call.message, get_date)


# DEBUG
@bot.message_handler(commands=['su_s'])
def sus(message):
    User.User(message.chat.id).type_u = 'student'


# DEBUG
@bot.message_handler(commands=['su_t'])
def sut(message):
    User.User(message.chat.id).type_u = 'teacher'

# TODO проверки существования сущностей
