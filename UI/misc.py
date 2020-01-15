import os

import Bot.config
from UI import buttons, markup

static_markups = {  # TODO dynamic markups
    'menu': markup.create([buttons.common.course_list_of('all'), buttons.common.course_list_of('my')],
                          include_back=False),
    'menu_teach': markup.create([buttons.common.course_list_of('all'), buttons.common.course_list_of('my')],
                                [buttons.teacher.manage_list], [buttons.teacher.new_course()],
                                include_back=False
                                )
}

messages = {
    i: open(Bot.config.MESSAGE_DIR + os.sep + i, encoding='utf-8').read() for i in os.listdir(Bot.config.MESSAGE_DIR)
}
