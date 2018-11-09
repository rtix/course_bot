import telebot

def requires_permission(*args):
    def decorator(func):
        def wrapper(message):
            user = None # get user
            if type(message) is telebot.types.Message:
                if any(isinstance(user, arg) for arg in args):
                    setattr(message, 'user', user)
                    return func(message)
            return None
        return wrapper
    return decorator