from User import User
from Database import CourseDB

class Attendance():
	pass

class Mark():
	def __init__(self, course_id, task_number, user_id):
		self.__course_id = int(course_id)
		self.__task_number = int(task_number)
		self.__user_id = int(user_id)
		data_from_base = dict(CourseDB.get_mark(self.__course_id, self.__task_number, self.__user_id))
		self.__mrk = data_from_base["mark"]

class Task():
	def __init__(self, course_id, task_number=None, task_name=None, task_description=None, task_highest_mark=None):
		self.__course_id = task_number
		if task_number:
			self.__task_number = int(task_number)
			data_from_base = dict(CourseDB.get_task(self.__course_id, self.__task_number))
			self.__task_name = str(data_from_base["task_name"])
			self.__task_description = str(data_from_base["description"])
			self.__task_highest_mark = int(data_from_base["highest_mark"])
		else:
			self.__task_name = str(task_name)
			self.__task_description = str(task_description)
			self.__task_highest_mark = int(task_highest_mark)
			self.__task_number = int(CourseDB.create_task(self.__course_id, self.__task_name, self.__task_description, self.__task_highest_mark))
	@property
	def name(self):
		return self.__task_name
	@property
	def number(self):
		return self.__task_number
	@property
	def description(self):
		return self.__task_description
	@property
	def highest_mark(self):
		return self.__task_highest_mark
	@name.setter
	def name(self, task_name):
		self.__task_name = task_name
		CourseDB.task_set(self.__course_id, self.__task_number, 'name', self.__task_name)
	@description.setter
	def description(self, description):
		self.__task_description = description
		CourseDB.task_set(self.__course_id, self.__task_number, 'description', self.__description)
	@highest_mark.setter
	def highest_mark(self, highest_mark):
		self.__task_highest_mark = highest_mark
		CourseDB.task_set(self.__course_id, self.__task_number, 'highest_mark', self.__task_highest_mark)
	def get_mark(self, task_number, user_id):
		return Mark(self.__course_id, task_number, user_id)

class Course():
	def __init__(self, course_id=None, owner_id=None, course_name=None):
		if course_id:
			self.__course_id = int(course_id)
			data_from_base = dict(CourseDB.get_course(self.__course_id))
			self.__course_name = str(data_from_base["course_name"])
			self.__owner_id = str(data_from_base["owner_id"])
			self.__description = str(data_from_base["description"])
		else:
			self.__owner_id = int(owner_id)
			self.__course_name = str(course_name)
			self.__course_id = CourseDB.create_course(self.__owner_id, self.__course_name)
	@property
	def id(self):
		return self.__course_id
	@property
	def name(self):
		return self.__course_name
	@property
	def owner(self):
		return User(self.__owner_id)
	@property
	def description(self):
		return self.__description
	@property
	def participants(self):
		return list(CourseDB.get_course_participants(self.__id))
	@description.setter
	def description(self, description):
		self.__description = description
		CourseDB.course_set(self.__course_id, 'description', self.__description)
	@name.setter
	def name(self, course_name):
		self.__course_name = str(course_name)
		CourseDB.course_set(self.__course_id, 'name', self.__course_name)
	def get_task(self, task_number):
		return Task(self.__course_id, task_number)
	def create_task(self, task_name, task_description, task_highest_mark):
		task_number = int(CourseDB.create_task(self.__course_id, task_name, task_description, task_highest_mark))
		return Task(self.__course_id, task_number, task_name, task_description, task_highest_mark)
