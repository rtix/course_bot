import User
from datetime import date
from Database import CourseDB
from Mailing import Mail

class Attendance():
	def __init__(self, course_id, cw_number, user_id):
		self.__course_id = course_id
		self.__cw_number = cw_number
		self.__user_id = user_id
		data_from_base = CourseDB.get_attendance(self.__course_id, self.__cw_number, self.__user_id)
		if data_from_base:
			self.__value = data_from_base["value"]
		else:
			self.__value = False
			CourseDB.create_attendance(self.__course_id, self.__cw_number, self.__user_id, self.__value)
	@property
	def course_id(self):
		return self.__course_id
	@property
	def cw_number(self):
		return self.__cw_number
	@property
	def user_id(self):
		return self.__user_id
	@property
	def value(self):
		return self.__value
	@value.setter
	def value(self, value):
		self.__value = value
		CourseDB.set_attendance(self.__course_id, self.__cw_number, self.__user_id, 'value', self.__value)
	def delete(self):
		CourseDB.delete_attendance(self.__course_id, self.__cw_number, self.__user_id)
		del self.__course_id, self.__cw_number, self.__user_id, self.__value

class Classwork():
	def __init__(self, course_id, cw_number=None, cw_name=None, cw_date=None):
		self.__course_id = course_id
		if cw_number:
			self.__cw_number = cw_number
			data_from_base = CourseDB.get_classwork(self.__course_id, self.__cw_number)
			self.__cw_name = data_from_base["name"]
			self.__cw_date = data_from_base["date"]
		else:
			self.__cw_name = cw_name
			self.__cw_date = cw_date
			self.__cw_number = CourseDB.create_classwork(self.__course_id, self.__cw_name, self.__cw_date)
	@property
	def course_id(self):
		return self.__course_id
	@property
	def number(self):
		return self.__cw_number
	@property
	def name(self):
		return self.__cw_name
	@name.setter
	def name(self, cw_name):
		self.__cw_name = cw_name
		CourseDB.set_classwork(self.__course_id, self.__cw_number, 'name', self.__cw_name)
	@property
	def date(self):
		return self.__cw_date
	@date.setter
	def date(self, cw_date):
		self.__cw_date = cw_date
		CourseDB.set_classwork(self.__course_id, self.__cw_number, 'date', self.__cw_date)
	def attendance(self):
		return Attendance(self.__course_id, self.__cw_number)
	def delete(self):
		CourseDB.delete_classwork(self.__course_id, self.__cw_number)
		del self.__course_id, self.__cw_number, self.__cw_name, self.__cw_date

class Mark():
	def __init__(self, course_id, task_number, user_id, mrk_date=None):
		self.__course_id = course_id
		self.__task_number = task_number
		self.__user_id = user_id
		data_from_base = CourseDB.get_mark(self.__course_id, self.__task_number, self.__user_id)
		if data_from_base:
			self.__mrk = data_from_base["mark"]
			self.__mrk_date = data_from_base["date"]
		else:
			self.__mrk = None
			self.__mrk_date = mrk_date if mrk_date else date.today()
			CourseDB.create_mark(self.__course_id, self.__task_number, self.__user_id, self.__mrk, self.__mrk_date)
	@property
	def course_id(self):
		return self.__course_id
	@property
	def task_number(self):
		return self.__task_number
	@property
	def user_id(self):
		return self.__user_id
	@property
	def value(self):
		return self.__mrk
	@value.setter
	def value(self, mrk):
		self.__mrk = mrk
		CourseDB.set_mark(self.__course_id, self.__task_number, self.__user_id, 'mark', self.__mrk)
	@property
	def date(self):
		return self.__mrk_date
	@date.setter
	def date(self, mrk_date):
		self.__mrk_date = mrk_date
		CourseDB.set_mark(self.__course_id, self.__task_number, self.__user_id, 'date', self.__mrk_date)
	def delete(self):
		CourseDB.delete_mark(self.__course_id, self.__task_number, self.__user_id)
		del self.__course_id, self.__task_number, self.__user_id, self.__mrk

class Task():
	def __init__(self, course_id, task_number=None, task_name=None, task_description=None, task_highest_mark=None):
		self.__course_id = course_id
		if task_number:
			self.__task_number = task_number
			data_from_base = CourseDB.get_task(self.__course_id, self.__task_number)
			self.__task_name = data_from_base["task_name"]
			self.__task_description = data_from_base["description"]
			self.__task_highest_mark = data_from_base["highest_mark"]
			self.__deadline = data_from_base["deadline"]
		else:
			self.__task_name = task_name
			self.__task_description = task_description
			self.__task_highest_mark = task_highest_mark
			self.__task_number = CourseDB.create_task(self.__course_id, self.__task_name, self.__task_description, self.__task_highest_mark)
			self.__deadline = None
	@property
	def course_id(self):
		return self.__course_id
	@property
	def name(self):
		return self.__task_name
	@name.setter
	def name(self, task_name):
		self.__task_name = task_name
		CourseDB.set_task(self.__course_id, self.__task_number, 'name', self.__task_name)
	@property
	def number(self):
		return self.__task_number
	@property
	def description(self):
		return self.__task_description
	@description.setter
	def description(self, description):
		self.__task_description = description
		CourseDB.set_task(self.__course_id, self.__task_number, 'description', self.__description)
	@property
	def highest_mark(self):
		return self.__task_highest_mark
	@highest_mark.setter
	def highest_mark(self, highest_mark):
		self.__task_highest_mark = highest_mark
		CourseDB.set_task(self.__course_id, self.__task_number, 'highest_mark', self.__task_highest_mark)
	@property
	def deadline(self):
		return self.__deadline
	@deadline.setter
	def deadline(self):
		CourseDB.set_task(self.__course_id, self.__task_number, 'deadline', self.__deadline)
	def mark(self, user_id):
		return Mark(self.__course_id, self.__task_number, user_id)
	def delete(self):
		CourseDB.delete_task(self.__course_id, self.__task_number)
		del self.__course_id, self.__task_number, self.__task_name, self.__task_description, self.__task_highest_mark

class Course():
	def __init__(self, course_id=None, owner_id=None, course_name=None):
		if course_id:
			self.__course_id = course_id
			data_from_base = CourseDB.get_course(self.__course_id)
			self.__course_name = data_from_base["name"]
			self.__owner_id = data_from_base["owner"]
			self.__description = data_from_base["description"]
		else:
			self.__owner_id = owner_id
			self.__course_name = course_name
			self.__course_id = CourseDB.create_course(self.__owner_id, self.__course_name)
			self.__description = None
	@property
	def id(self):
		return self.__course_id
	@property
	def name(self):
		return self.__course_name
	@property
	def owner(self):
		return User.User(self.__owner_id)
	@property
	def description(self):
		return self.__description
	def get_participants(self):
		return [User.User(user_id) for user_id in CourseDB.get_course_participants(self.__course_id)]
	@description.setter
	def description(self, description):
		self.__description = description
		CourseDB.set_course(self.__course_id, 'description', self.__description)
	@name.setter
	def name(self, course_name):
		self.__course_name = course_name
		CourseDB.set_course(self.__course_id, 'name', self.__course_name)
	def task(self, task_number=None, task_name=None, task_description=None, task_highest_mark=None):
		return Task(self.__course_id, task_number, task_name, task_description, task_highest_mark)
	def classwork(self, cw_number=None, cw_name=None, cw_date=None):
		return Classwork(self.__course_id, cw_number, cw_name, cw_date)
	def mailing(self, email, password, text):
		participants = [User.User(user_id) for user_id in CourseDB.get_course_participants(self.__course_id)]
		recipients = [participant.email for participant in participants]
		Mail(email, password).send(recipients, text)
	def delete(self):
		CourseDB.delete_course(self.__course_id)
		del self.__course_id, self.__course_name, self.__owner_id, self.__description
