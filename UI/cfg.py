import os

import Bot.config as config
import UI.buttons.common as c
import UI.buttons.teacher as t
import UI.ui as ui

static_markups = {  # TODO dynamic markups
    'menu': ui.create_markup([c.course_list_of('all'), c.course_list_of('my')], include_back=False),
    'menu_teach': ui.create_markup([c.course_list_of('all'), c.course_list_of('my')],
                                   [t.manage_list], [t.new_course()],
                                   include_back=False
                                   )
}

messages = {
    i: open(config.MESSAGE_DIR + os.sep + i, encoding='utf-8').read() for i in os.listdir(config.MESSAGE_DIR)
}

course_name_length_min = 5
course_name_length_max = 50

course_desc_length_min = 10
course_desc_length_max = 300

course_info_desc_length = 33
