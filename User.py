from Database import UserDB
from Database import CourseDB
import Course


class User:
    def __init__(self, id, username):
        """
        :param id: chat_id пользователя int
        :param username: username пользователя, если юзернэйма нет передай '' строка
        """
        u = UserDB.is_teacher_username(username)
        if u[0]:
            self._id = id
            self.name = u[1]
            self.group = ''
            self.email = ''
            self.type_u = 'teacher'
            UserDB.create_user(id, self.name, self.group, self.email, self.type_u)
        else:
            user = UserDB.get_user_by_id(id)
            if user is not None:
                self._id = id
                self.name = user['name']
                self.group = user['group_n']
                self.email = user['email']
                self.type_u = user['type_u']
            else:
                self._id = id
                self.name = ''
                self.group = ''
                self.email = ''
                self.type_u = 'unlogined'

    def create_teacher(self, username, name):
        """
        Добовление нового учителя по юзернэйму
        """
        if self.type_u == 'teacher':
            UserDB.write_teacher_username(username, name)

    def join_course(self, course_id):
        if self.type_u == 'student':
            UserDB.add_course_stud(self._id, course_id)

    def leave_course(self, course_id):
        if self.type_u == 'student':
            UserDB.del_course_stud(self._id, course_id)

    def create_course(self, course_name):
        """
        вызывается у тичера, созлдает курс
        :param course_name: строка
        :return: ничего
        """
        if self.type_u == 'teacher':
            CourseDB.create_course(self._id, course_name)

    def get_courses_for_teacher(self):
        """
        :return: список куров которые создал этот тичер, если таких курсов нет []
        """
        if self.type_u == 'teacher':
            courses_id = UserDB.get_teacher_courses(self._id)
            if courses_id is not None:
                courses = []
                for x in courses_id:
                    courses.append(Course.Course(x))
                return courses
            else:
                return []

    def delete_course(self,course_id):
        if self.type_u == 'teacher':
            courses_id = UserDB.get_teacher_courses(self._id)
            if courses_id is not None:
                if course_id in courses_id:
                    CourseDB.delete_course(course_id)

    def get_courses_for_student(self):
        """
        :return: список куров на которые записан студент, если не записан вернет []
        """
        if self.type_u == 'student':
            courses_id = UserDB.get_user_courses(self._id)
            if courses_id is not None:
                courses = []
                for x in courses_id:
                    courses.append(Course.Course(x))
                return courses
            else:
                return []


    def show_user(self):
        """
        Печатает в консоль данные юзера, нужна для отладки
        """
        print('---', '\n', 'id', self._id,' name', self.name, 'group', self.group, 'type', self.type_u, '\n', '---')
