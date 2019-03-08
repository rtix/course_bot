import UI.buttons.common as c
import UI.buttons.teacher as t
from UI import ui


# заранее созданные клавиатуры
markups = {'menu': ui.create_markup([c.all_courses, c.my_courses]),
           'menu_teach': ui.create_markup([c.all_courses, c.my_courses], [t.manage_list], [t.create])
           }

err_msg = 'something went wrong\ngoing to main menu'
err_markup = markups['menu_teach']

messages = {'start': open(ui.mespath + 'start', encoding='utf-8').read(),
            'menu': 'Главное меню',
            'all': 'Все курсы',
            'my': 'Курсы, на которые Вы записаны',
            'teach': 'Ваши курсы',
            'reg_mail': open(ui.mespath + 'reg', encoding='utf-8').read(),
            'new_course': open(ui.mespath + 'new_course', encoding='utf-8').read(),
            'course': open(ui.mespath + 'course', encoding='utf-8').read(),
            'red': open(ui.mespath + 'redact', encoding='utf-8').read(),
            'user': open(ui.mespath + 'user', encoding='utf-8').read(),
            'mark_o': open(ui.mespath + 'mark_one', encoding='utf-8').read(),
            'mark_a': open(ui.mespath + 'mark_all', encoding='utf-8').read(),
            'new_announce': open(ui.mespath + 'new_announce', encoding='utf-8').read(),
            'announce': open(ui.mespath + 'announce', encoding='utf-8').read()}
