import os
from UI.ui import create_markup as create
import UI.buttons.teacher as t
import UI.buttons.common as c

menu_button = c.keyboard

# заранее созданные клавиатуры
markups = {'menu': create([c.all_courses, c.my_courses]),
           'menu_teach': create([c.all_courses, c.my_courses], [t.manage_list], [t.create])
           }

err_msg = 'something went wrong\ngoing to main menu'
err_markup = markups['menu_teach']

messages = {'start': open('UI' + os.sep + 'messages' + os.sep + 'start').read(),
            'menu': 'Главное меню',
            'all': 'Все курсы',
            'my': 'Курсы, на которые Вы записаны',
            'teach': 'Ваши курсы',
            }


