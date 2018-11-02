import Procedures
import Course


class User:
    _id = ''
    telegram_id = ''

    def __init__(self, id):
        self._id = id


class Teacher(User):
    name = ''

    def __init__(self, id, name):
        User.__init__(self, id)
        self.name = name

    def create_new_teacher(self, id, name):
        teacher = Teacher(id,name)
        Procedures.save_teacher(teacher)

    def create_course(self,name):
        course = Course.Course(self._id, name)
        Procedures.save_course(course)

    def delete_course(self,name):
        course = Course.Course(self._id,name)
        Procedures.delete_course(course)


class Student(User):
    name = ''
    email = ''
    group = ''

    def __init__(self, id, name, email, group):
        User.__init__(self, id)
        self.name = name
        self.email = email
        self.group = group

    def join_cousre(self,name_course):
        Procedures.add_stud_course(self._id,name_course)

    def leave_course(self,name_course):
        Procedures.del_stud_course(self._id, name_course)
