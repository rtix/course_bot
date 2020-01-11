import os

import UI.buttons.common as c
import UI.buttons.teacher as t
from Bot.config import MESSAGE_DIR
from UI import ui


static_markups = {
    'menu': ui.create_markup([c.course_list_of('all'), c.course_list_of('my')], include_back=False),
    'menu_teach': ui.create_markup([c.course_list_of('all'), c.course_list_of('my')], [t.manage_list], [t.create],
                                   include_back=False
                                   )
}

messages = {
    i: open(MESSAGE_DIR + os.sep + i, encoding='utf-8').read() for i in os.listdir(MESSAGE_DIR)
}
