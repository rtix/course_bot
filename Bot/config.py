import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
MESSAGE_DIR = os.path.join(ROOT_DIR, 'messages')
USER_MOVEMENT_DIR = os.path.join(ROOT_DIR, '.usermovements')
SETTINGS_PATH = os.path.join(ROOT_DIR, 'settings.cfg')
DATABASE_PATH = os.path.join(ROOT_DIR, 'Database', 'DB_FOR_TBOT.db')

__all__ = [
    'MESSAGE_DIR',
    'ROOT_DIR',
    'USER_MOVEMENT_DIR',
    'SETTINGS_PATH',
    'DATABASE_PATH'
]
