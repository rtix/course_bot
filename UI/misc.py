import json
import os
import time

from Bot.config import MESSAGE_DIR

messages = {
    i.split('.')[0]: json.load(open(os.path.join(MESSAGE_DIR, i))) for i in os.listdir(MESSAGE_DIR)
}


def to_dtime(utime):
    return time.strftime("%d %b %Y", time.localtime(float(utime))) if utime else None
