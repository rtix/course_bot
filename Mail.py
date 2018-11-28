# Пример использования класса:
# mail = Mail('bot_email@mail.ru', 'password')
# При рассылке по студентам курса от имени преподавателя:
# course = Course(123)
# recipients = [participant.email for participant in course.participants]
# text = "Перенос занятия с сегодня на завтра.\nНавеки ваш, {}".format(course.owner.username)
# mail.send(recipients, text)
# При рассылке от имени бота при регистрации:
# recipient = "email_to_confirm@mail.ru"
# mail.recipients = recipient
# mail.text = "Ваш код для подтверждения почты: qwerty12345"
# mail.send()
# Здесь видно, что можно передать данные в send() класса и отправить сразу, без сохранения данных
# Или явно присвоить полям класса данные, сохранив их для последующих отправок сообщений
import re
import smtplib
from email.header import Header
from email.mime.text import MIMEText


class WrongEMail(Exception):
    def __init__(self, value):
        self.msg = value


class AuthError(Exception):
    def __init__(self, value):
        self.msg = value


def check_valid(mail):
    """
    Function for checking if email is valid

    :param mail: email as str to check
    """

    return bool(re.fullmatch(r'^[\w]\S*@[a-z]+\.[a-z]+$', mail, re.ASCII))


class Mail:
    """
    Mail.recipients : Recipient(s) as str (or list of str)
    Mail.text : Text of a message as str
    Mail.subject : Subject of a message as str
    """

    def __init__(self, email, password, smtp_host=""):
        """
        Constructor for Mail() class.

        :param email: email of sender as str
        :param password: password of sender as str
        :param smtp_host: smtp host as str. If not specified, it is considered as "smtp.{0}.{1}" for mailname@{0}.{1}
        """

        self.__email = email
        self.__password = password
        if smtp_host:
            self.__smtp_host = smtp_host
        else:
            self.__smtp_host = "smtp.{}.{}".format(*re.findall(r"@(.+)\.(\w+)", email)[0])
        self.__subject = ""
        self.__recipients = None

    def reconfigure(self, email, password, smtp_host=""):
        """
        Reconfiguring Mail() class.

        :param email: email of sender as str
        :param password: password of sender as str
        :param smtp_host: smtp host as str. If not specified, it is considered as "smtp.{0}.{1}" for mailname@{0}.{1}
        """

        self.__email = email
        self.__password = password
        if smtp_host:
            self.__smtp_host = smtp_host
        else:
            self.__smtp_host = "smtp.{}.{}".format(*re.findall(r"@(.+)\.(\w+)", email)[0])

    @property
    def recipients(self):
        return self.__recipients

    @recipients.setter
    def recipients(self, recipients):
        self.__recipients = recipients

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        self.__text = text

    @property
    def subject(self):
        return self.__subject

    @subject.setter
    def subject(self, subject):
        self.__subject = subject

    def send(self, recipients=None, subject="", text=""):
        """
        Function for sending message with given arguments or setted fields (or in combine).
        Given arguments here will not be saved as fields.

        :param recipients : Recipient(s) as str (or list of str)
        :param text : Text of a message as str
        :param subject : Subject of a message as str
        """

        subject = Header(subject, 'utf-8') if subject else Header(self.__subject, 'utf-8')
        if not recipients:
            recipients = self.__recipients
        if not text:
            text = self.__text

        msg = MIMEText(text, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = self.__email
        msg['To'] = recipients

        s = smtplib.SMTP_SSL(self.__smtp_host, 465, timeout=10)
        try:
            s.login(self.__email, self.__password)
        except smtplib.SMTPAuthenticationError as ex:
            if not re.findall('password', str(ex.smtp_error)):  # скорее всего - неверный хост
                raise AuthError(str(ex.smtp_error) + '\nIt is possible that smtp_host we determined '
                                                     'is wrong. Please, add your SMTP host in settings.cfg '
                                                     'on your own.'
                                )
            else:  # неверный логин пароль
                raise AuthError(str(ex.smtp_error))
        sent = True
        try:
            s.sendmail(from_addr=msg['From'], to_addrs=recipients, msg=msg.as_string())
        except smtplib.SMTPException:
            sent = False
        finally:
            s.quit()
        return sent
