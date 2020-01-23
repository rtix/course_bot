import os
import sys

ROOT_DIR = os.path.dirname(sys.modules['__main__'].__file__)
MESSAGE_DIR = ROOT_DIR + '/messages'
USER_MOVEMENT_DIR = ROOT_DIR + '/.usermovements'

__all__ = [
    'MESSAGE_DIR',
    'ROOT_DIR',
    'USER_MOVEMENT_DIR'
]
