from Database import UserDB
from Models import Course


class InterrelatedParametersError(Exception):
	def __init__(self, *message):
		self.message = tuple(msg for msg in message)
	def __str__(self):
		return "Expected interrelated parameters: {}. You have to use only one data set from this".format(" OR ".join([str(msg) for msg in self.message]))


class TeacherAccessDeniedError(Exception):
	def __init__(self, message):
		self.message = str(message)
	def __str__(self):
		return "Access denied. {}".format(self.message)


class UserTypeError(Exception):
	def __init__(self, message):
		self.message = str(message)
	def __str__(self):
		return "Wrong type of user: '{}'. Use 'teacher' or 'student' instead".format(self.message)


class User():

	def __init__(self, id, username='', name='', group='', email=''):
		"""
		Чтобы получить пользователя из базы данных используй только параметр id
		Чтобы зарегистрировать студента в базу данных используй id, name, group, email
		Чтобы попробовать(try) зарегистрировать учителя в базу данных, используй id, username. Если учителя с таким username не ожидается, будет вызвана
		:param id: chat_id пользователя int
		:param username: username учителя
		"""
		# Checking if constructor parameters was used correctry
		if not((id and not(username or name or group or email)) or (id and username and name and not(group or email)) or (id and name and group and email and not(username))):
			raise InterrelatedParametersError(("id", "username", "name"), ("id", "name", "group", "email"), ("id"))
		self.__id = id
		if name: # Create user
			type_u = 'student'
			if username: # Trying to create teacher
				if UserDB.check_teacher_invitation(username):
					UserDB.delete_teacher_invitation(username)
					type_u = 'teacher'
				else:
					raise TeacherAccessDeniedError("Expected teacher")
			UserDB.create_user(self.__id, name, group, email, type_u)

	@property
	def type_u(self):
		user = UserDB.get_user(self.__id)
		return user["type_u"] if user else 'unlogined'

	@type_u.setter
	def type_u(self, type_u):
		if type_u in ('student', 'teacher'):
			UserDB.set_user(self.__id, 'type_u', type_u)
		else:
			raise UserTypeError(type_u)

	@property
	def id(self):
		return self.__id

	@property
	def name(self):
		user = UserDB.get_user(self.__id)
		return user["name"] if user else ""

	@name.setter
	def name(self, name):
		UserDB.set_user(self.__id, 'name', name)

	@property
	def possessions(self): # Курсы под владением
		user = UserDB.get_user(self.__id)
		return tuple(Course.Course(course_id) for course_id in UserDB.get_teacher_courses(self.__id)) if user else []

	@property
	def participation(self): # Участие в курсах
		user = UserDB.get_user(self.__id)
		return tuple(Course.Course(course_id) for course_id in UserDB.get_user_courses(self.__id)) if user else []

	def invite_teacher(self, username):
		"""
		Приглашение нового учителя по username
		"""
		user = UserDB.get_user(self.__id)
		if user and user['type_u']=='teacher':
			UserDB.create_teacher_invitation(username)
		else:
			raise TeacherAccessDeniedError("Expected Teacher")

	def create_course(self, course_name):
		"""
		Вызывается у teacher, создает курс
		:param course_name: строка
		:return: Course
		"""
		user = UserDB.get_user(self.__id)
		if user and user['type_u']=='teacher':
			return Course.Course(owner_id=self.__id, name=course_name)
		else:
			raise TeacherAccessDeniedError("Expected teacher")
		
	def delete_course(self, course_id):
		course_to_delete = Course.Course(course_id)
		if course_to_delete.owner.id == self.__id:
			course_to_delete.delete()
		else:
			raise TeacherAccessDeniedError("Expected owner of the course")
