import os
import time

from Bot.config import MESSAGE_DIR
from UI import buttons, markup

static_markups = {  # TODO dynamic markups
    'menu': markup.create(
        [buttons.common.course_list_of('all'), buttons.common.course_list_of('my')],
        include_back=False
    ),
    'menu_teach': markup.create(
        [buttons.common.course_list_of('all'), buttons.common.course_list_of('my')],
        [buttons.teacher.manage_list()], [buttons.teacher.new_course()],
        include_back=False
    )
}

messages = {
    i: open(MESSAGE_DIR + os.sep + i, encoding='utf-8').read() for i in os.listdir(MESSAGE_DIR)
}


def to_dtime(utime):
    return time.strftime("%d %b %Y", time.localtime(float(utime))) if utime else None
