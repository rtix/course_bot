import configparser
import os


def main():
    sets.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.cfg'))

    import Bot.bot as b
    b.go()


if __name__ == '__main__':
    sets = configparser.ConfigParser()
    main()
