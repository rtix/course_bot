import User
from datetime import date
from Database import CourseDB
from Mail import Mail

class InterrelatedParametersError(Exception):
	def __init__(self, *message):
		self.message = tuple(msg for msg in message)
	def __str__(self):
		return "Expected interrelated parameters: {}. You have to use only one data set from this".format(" OR ".join([str(msg) for msg in self.message]))

class Literature():
	def __init__(self, course_id, number=None, name="", description="", file=None, url=""):
		# Checking if constructor parameters was used correctry
		if not((number and not(name or description or file or url)) or (not number and name)):
			raise InterrelatedParametersError(("course_id", "number"), ("course_id", "name", "optional: description", "optional: file", "optional: url"))
		self.__course_id = course_id
		if number:
			self.__lit_number = number
			data_from_base = CourseDB.get_literature(self.__course_id, self.__lit_number)
			self.__name = data_from_base["name"]
			self.__description = data_from_base["description"]
			self.__file = data_from_base["file"]
			self.__url = data_from_base["url"]
		else:
			self.__name = name
			self.__description = description
			self.__file = file
			self.__url = url
			self.__lit_number = CourseDB.create_literature(self.__course_id, self.__name, self.__description, self.__file, self.__url)
	@property
	def course_id(self):
		return self.__course_id
	@property
	def number(self):
		return self.__lit_number
	@property
	def name(self):
		return self.__name
	@name.setter
	def name(self, name):
		self.__name = name
		CourseDB.set_literature(self.__course_id, self.__lit_number, 'name', self.__name)
	@property
	def description(self):
		return self.__description
	@description.setter
	def description(self, description):
		self.__description = description
		CourseDB.set_literature(self.__course_id, self.__lit_number, 'description', self.__description)
	@property
	def file(self):
		return self.__file
	@file.setter
	def file(self, file):
		self.__file = file
		CourseDB.set_literature(self.__course_id, self.__lit_number, 'file', self.__file)
	@property
	def url(self):
		return self.__url
	@url.setter
	def url(self, url):
		self.__url = url
		CourseDB.set_literature(self.__course_id, self.__lit_number, 'url', self.__url)
	def delete(self):
		CourseDB.delete_literature(self.__course_id, self.__lit_number)
		del self.__course_id, self.__lit_number, self.__name, self.__description, self.__file, self.__url

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
	def classwork_number(self):
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
	def __init__(self, course_id, number=None, name="", date=None):
		# Checking if constructor parameters was used correctry
		if not((number and not(name or date)) or (not number and name)):
			raise InterrelatedParametersError(("course_id", "number"), ("course_id", "name", "optional: date"))
		self.__course_id = course_id
		if number:
			self.__cw_number = number
			data_from_base = CourseDB.get_classwork(self.__course_id, self.__cw_number)
			self.__cw_name = data_from_base["name"]
			self.__cw_date = data_from_base["date"]
		else:
			self.__cw_name = name
			self.__cw_date = date
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
	def name(self, name):
		self.__cw_name = name
		CourseDB.set_classwork(self.__course_id, self.__cw_number, 'name', self.__cw_name)
	@property
	def date(self):
		return self.__cw_date
	@date.setter
	def date(self, date):
		self.__cw_date = date
		CourseDB.set_classwork(self.__course_id, self.__cw_number, 'date', self.__cw_date)
	def attendance(self):
		return Attendance(self.__course_id, self.__cw_number)
	def delete(self):
		CourseDB.delete_classwork(self.__course_id, self.__cw_number)
		del self.__course_id, self.__cw_number, self.__cw_name, self.__cw_date

class Mark():
	def __init__(self, course_id, task_number, user_id):
		self.__course_id = course_id
		self.__task_number = task_number
		self.__user_id = user_id
		data_from_base = CourseDB.get_mark(self.__course_id, self.__task_number, self.__user_id)
		if data_from_base:
			self.__mrk = data_from_base["mark"]
			self.__mrk_date = data_from_base["date"]
		else:
			self.__mrk = None
			self.__mrk_date = None
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
		if not self.__mrk_date:
			self.__mrk_date = date.today()
		CourseDB.set_mark(self.__course_id, self.__task_number, self.__user_id, 'mark', self.__mrk)
		CourseDB.set_mark(self.__course_id, self.__task_number, self.__user_id, 'date', self.__mrk_date)
	@property
	def date(self):
		return self.__mrk_date
	@date.setter
	def date(self, date):
		self.__mrk_date = date
		CourseDB.set_mark(self.__course_id, self.__task_number, self.__user_id, 'date', self.__mrk_date)
	def delete(self):
		CourseDB.delete_mark(self.__course_id, self.__task_number, self.__user_id)
		del self.__course_id, self.__task_number, self.__user_id, self.__mrk

class Task():
	def __init__(self, course_id, number=None, name="", description="", highest_mark=None):
		# Checking if constructor parameters was used correctry
		if not((number and not(name or description or highest_mark)) or (not number and name and description and highest_mark)):
			raise InterrelatedParametersError(("course_id", "number"), ("course_id", "name", "description", "highest_mark"))
		self.__course_id = course_id
		if number:
			self.__task_number = number
			data_from_base = CourseDB.get_task(self.__course_id, self.__task_number)
			self.__task_name = data_from_base["task_name"]
			self.__task_description = data_from_base["description"]
			self.__task_highest_mark = data_from_base["highest_mark"]
			self.__deadline = data_from_base["deadline"]
		else:
			self.__task_name = name
			self.__task_description = description
			self.__task_highest_mark = highest_mark
			self.__task_number = CourseDB.create_task(self.__course_id, self.__task_name, self.__task_description, self.__task_highest_mark)
			self.__deadline = None
	@property
	def course_id(self):
		return self.__course_id
	@property
	def name(self):
		return self.__task_name
	@name.setter
	def name(self, name):
		self.__task_name = name
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
	def __init__(self, course_id=None, owner_id=None, name=""):
		# Checking if constructor parameters was used correctry
		if not((course_id and not(owner_id or name)) or (not course_id and owner_id and name)):
			raise InterrelatedParametersError(("course_id"), ("owner_id", "name"))
		if course_id:
			self.__course_id = course_id
			data_from_base = CourseDB.get_course(self.__course_id)
			self.__course_name = data_from_base["name"]
			self.__owner_id = data_from_base["owner"]
			self.__description = data_from_base["description"]
			self.__participants = data_from_base["participants"]
			self.__blacklist = data_from_base["blacklist"]
			self.__task_numbers = data_from_base["task_numbers"]
			self.__cw_numbers = data_from_base["cw_numbers"]
			self.__lit_numbers = data_from_base["lit_numbers"]
			self.__entry_restriction = data_from_base["entry_restriction"]
		else:
			self.__owner_id = owner_id
			self.__course_name = name
			self.__course_id = CourseDB.create_course(self.__owner_id, self.__course_name)
			self.__description = ""
			self.__participants = []
			self.__blacklist = []
			self.__task_numbers = []
			self.__cw_numbers = []
			self.__lit_numbers = []
			self.__entry_restriction = None
	@property
	def id(self):
		return self.__course_id
	@property
	def name(self):
		return self.__course_name
	@name.setter
	def name(self, name):
		self.__course_name = name
		CourseDB.set_course(self.__course_id, 'name', self.__course_name)
	@property
	def owner(self):
		return User.User(self.__owner_id)
	@property
	def description(self):
		return self.__description
	@description.setter
	def description(self, description):
		self.__description = description
		CourseDB.set_course(self.__course_id, 'description', self.__description)
	@property
	def entry_restriction(self):
		return self.__entry_restriction
	@entry_restriction.setter
	def entry_restriction(self, restriction_date):
		self.__entry_restriction = restriction_date
		CourseDB.set_course(self.__course_id, "entry_restriction", self.__entry_restriction)
	@property
	def participants(self):
		return tuple(User.User(user_id) for user_id in self.__participants)
	@property
	def blacklist(self):
		return tuple(User.User(user_id) for user_id in self.__blacklist)
	@property
	def tasks(self):
		return tuple(Task(self.__course_id, task_number) for task_number in self.__task_numbers)
	@property
	def classworks(self):
		return tuple(Classwork(self.__course_id, cw_number) for cw_number in self.__cw_numbers)
	@property
	def literatures(self):
		return tuple(Literature(self.__course_id, lit_number) for lit_number in self.__lit_numbers)
	def append_student(self, user_id):
		self.__participants.append(user_id)
		CourseDB.append_user_course(user_id, self.__course_id)
	def remove_student(self, user_id):
		self.__participants.remove(user_id)
		CourseDB.remove_user_course(user_id, self.__course_id)
	def append_to_blacklist(self, user_id):
		self.__blacklist.append(user_id)
		CourseDB.append_to_blacklist(self.__course_id, user_id)
	def remove_from_blacklist(self, user_id):
		self.__blacklist.remove(user_id)
		CourseDB.remove_from_blacklist(self.__course_id, user_id)
	def task(self, task_number=None, task_name="", task_description="", task_highest_mark=None):
		return Task(self.__course_id, task_number, task_name, task_description, task_highest_mark)
	def classwork(self, cw_number=None, cw_name="", cw_date=None):
		return Classwork(self.__course_id, cw_number, cw_name, cw_date)
	def literature(self, lit_number=None, name="", description="", file=None, url=""):
		return Literature(self.__course_id, lit_number, name, description, file, url)
	def mailing(self, email, password, text):
		participants = [User.User(user_id) for user_id in self.__participants]
		recipients = [participant.email for participant in participants]
		Mail(email, password).send(recipients, text)
	def delete(self):
		CourseDB.delete_course(self.__course_id)
		del self.__course_id, self.__course_name, self.__owner_id, self.__description
