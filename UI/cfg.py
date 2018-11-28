import UI.buttons.common as c
import UI.buttons.teacher as t
from UI import ui

# заранее созданные клавиатуры
markups = {'menu': ui.create_markup([c.all_courses, c.my_courses]),
           'menu_teach': ui.create_markup([c.all_courses, c.my_courses], [t.manage_list], [t.create])
           }

err_msg = 'something went wrong\ngoing to main menu'
err_markup = markups['menu_teach']

messages = {'start': open(ui.mespath + 'start').read(),
            'menu': 'Главное меню',
            'all': 'Все курсы',
            'my': 'Курсы, на которые Вы записаны',
            'teach': 'Ваши курсы',
            'reg_mail': open(ui.mespath + 'reg').read(),
            'new_course': open(ui.mespath + 'new_course').read()
            }
