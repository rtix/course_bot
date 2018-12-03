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
	def __init__(self, course_id, number=None, name="", description="", file_id=None, url=""):
		# Checking if constructor parameters was used correctry
		if not((number and not(name or description or file_id or url)) or (not number and name)):
			raise InterrelatedParametersError(("course_id", "number"), ("course_id", "name", "optional: description", "optional: file_id", "optional: url"))
		self.__course_id = course_id
		if number:
			self.__lit_number = number
		else:
			self.__lit_number = CourseDB.create_literature(self.__course_id, name, description, file_id, url)
	@property
	def course_id(self):
		return self.__course_id
	@property
	def number(self):
		return self.__lit_number
	@property
	def name(self):
		return CourseDB.get_literature(self.__course_id, self.__lit_number)["name"]
	@name.setter
	def name(self, name):
		CourseDB.set_literature(self.__course_id, self.__lit_number, 'name', name)
	@property
	def description(self):
		return CourseDB.get_literature(self.__course_id, self.__lit_number)["description"]
	@description.setter
	def description(self, description):
		CourseDB.set_literature(self.__course_id, self.__lit_number, 'description', description)
	@property
	def file_id(self):
		return CourseDB.get_literature(self.__course_id, self.__lit_number)["file_id"]
	@file_id.setter
	def file_id(self, file_id):
		CourseDB.set_literature(self.__course_id, self.__lit_number, 'file_id', file_id)
	@property
	def url(self):
		return CourseDB.get_literature(self.__course_id, self.__lit_number)["url"]
	@url.setter
	def url(self, url):
		self.__url = url
		CourseDB.set_literature(self.__course_id, self.__lit_number, 'url', url)
	def delete(self):
		CourseDB.delete_literature(self.__course_id, self.__lit_number)
		del self.__course_id, self.__lit_number

class Attendance():
	def __init__(self, course_id, cw_number, user_id):
		self.__course_id = course_id
		self.__cw_number = cw_number
		self.__user_id = user_id
		if not(CourseDB.get_attendance(self.__course_id, self.__cw_number, self.__user_id)):
			CourseDB.create_attendance(self.__course_id, self.__cw_number, self.__user_id, False)
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
		return CourseDB.get_attendance(self.__course_id, self.__cw_number, self.__user_id)["value"]
	@value.setter
	def value(self, value):
		CourseDB.set_attendance(self.__course_id, self.__cw_number, self.__user_id, 'value', value)
	def delete(self):
		CourseDB.delete_attendance(self.__course_id, self.__cw_number, self.__user_id)
		del self.__course_id, self.__cw_number, self.__user_id

class Classwork():
	def __init__(self, course_id, number=None, name="", date=None):
		# Checking if constructor parameters was used correctry
		if not((number and not(name or date)) or (not number and name)):
			raise InterrelatedParametersError(("course_id", "number"), ("course_id", "name", "optional: date"))
		self.__course_id = course_id
		if number:
			self.__cw_number = number
		else:
			self.__cw_number = CourseDB.create_classwork(self.__course_id, name, date)
	@property
	def course_id(self):
		return self.__course_id
	@property
	def number(self):
		return self.__cw_number
	@property
	def name(self):
		return CourseDB.get_classwork(self.__course_id, self.__cw_number)["name"]
	@name.setter
	def name(self, name):
		CourseDB.set_classwork(self.__course_id, self.__cw_number, 'name', name)
	@property
	def date(self):
		return CourseDB.get_classwork(self.__course_id, self.__cw_number)["date"]
	@date.setter
	def date(self, date):
		CourseDB.set_classwork(self.__course_id, self.__cw_number, 'date', date)
	def attendance(self, user_id):
		return Attendance(self.__course_id, self.__cw_number, user_id)
	def delete(self):
		CourseDB.delete_classwork(self.__course_id, self.__cw_number)
		del self.__course_id, self.__cw_number

class Mark():
	def __init__(self, course_id, task_number, user_id):
		self.__course_id = course_id
		self.__task_number = task_number
		self.__user_id = user_id
		if not(CourseDB.get_mark(self.__course_id, self.__task_number, self.__user_id)):
			CourseDB.create_mark(self.__course_id, self.__task_number, self.__user_id, None, None)
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
		return CourseDB.get_mark(self.__course_id, self.__task_number, self.__user_id)["mark"]
	@value.setter
	def value(self, mrk):
		if not(CourseDB.get_mark(self.__course_id, self.__task_number, self.__user_id)["date"]):
			CourseDB.set_mark(self.__course_id, self.__task_number, self.__user_id, 'date', date.today())
		CourseDB.set_mark(self.__course_id, self.__task_number, self.__user_id, 'mark', mrk)
	@property
	def date(self):
		return CourseDB.get_mark(self.__course_id, self.__task_number, self.__user_id)["date"]
	@date.setter
	def date(self, date):
		CourseDB.set_mark(self.__course_id, self.__task_number, self.__user_id, 'date', date)
	def delete(self):
		CourseDB.delete_mark(self.__course_id, self.__task_number, self.__user_id)
		del self.__course_id, self.__task_number, self.__user_id

class Task():
	def __init__(self, course_id, number=None, name="", description="", highest_mark=None):
		# Checking if constructor parameters was used correctry
		if not((number and not(name or description or highest_mark)) or (not number and name and description and highest_mark)):
			raise InterrelatedParametersError(("course_id", "number"), ("course_id", "name", "description", "highest_mark"))
		self.__course_id = course_id
		if number:
			self.__task_number = number
		else:
			self.__task_number = CourseDB.create_task(self.__course_id, name, description, highest_mark, None)
	@property
	def course_id(self):
		return self.__course_id
	@property
	def name(self):
		return CourseDB.get_task(self.__course_id, self.__task_number)["name"]
	@name.setter
	def name(self, name):
		CourseDB.set_task(self.__course_id, self.__task_number, 'name', name)
	@property
	def number(self):
		return self.__task_number
	@property
	def description(self):
		return CourseDB.get_task(self.__course_id, self.__task_number)["description"]
	@description.setter
	def description(self, description):
		CourseDB.set_task(self.__course_id, self.__task_number, 'description', description)
	@property
	def highest_mark(self):
		return CourseDB.get_task(self.__course_id, self.__task_number)["highest_mark"]
	@highest_mark.setter
	def highest_mark(self, highest_mark):
		CourseDB.set_task(self.__course_id, self.__task_number, 'highest_mark', highest_mark)
	@property
	def deadline(self):
		return CourseDB.get_task(self.__course_id, self.__task_number)["deadline"]
	@deadline.setter
	def deadline(self, deadline):
		CourseDB.set_task(self.__course_id, self.__task_number, 'deadline', deadline)
	def mark(self, user_id):
		return Mark(self.__course_id, self.__task_number, user_id)
	def delete(self):
		CourseDB.delete_task(self.__course_id, self.__task_number)
		del self.__course_id, self.__task_number

class Course():
	def __init__(self, course_id=None, owner_id=None, name=""):
		# Checking if constructor parameters was used correctry
		if not((course_id and not(owner_id or name)) or (not course_id and owner_id and name)):
			raise InterrelatedParametersError(("course_id"), ("owner_id", "name"))
		if course_id:
			self.__course_id = course_id
		else:
			self.__course_id = CourseDB.create_course(owner_id, name)
	@property
	def id(self):
		return self.__course_id
	@property
	def name(self):
		return CourseDB.get_course(self.__course_id)["name"]
	@name.setter
	def name(self, name):
		CourseDB.set_course(self.__course_id, 'name', name)
	@property
	def owner(self):
		return User.User(CourseDB.get_course(self.__course_id)["owner"])
	@property
	def description(self):
		return CourseDB.get_course(self.__course_id)["description"]
	@description.setter
	def description(self, description):
		CourseDB.set_course(self.__course_id, 'description', description)
	@property
	def entry_restriction(self):
		return CourseDB.get_course(self.__course_id)["entry_restriction"]
	@entry_restriction.setter
	def entry_restriction(self, restriction_date):
		CourseDB.set_course(self.__course_id, "entry_restriction", restriction_date)
	@property
	def participants(self):
		return tuple(User.User(user_id) for user_id in CourseDB.get_course(self.__course_id)["participants"])
	@property
	def blacklist(self):
		return tuple(User.User(user_id) for user_id in CourseDB.get_course(self.__course_id)["blacklist"])
	@property
	def tasks(self):
		return tuple(Task(self.__course_id, task_number) for task_number in CourseDB.get_course(self.__course_id)["task_numbers"])
	@property
	def classworks(self):
		return tuple(Classwork(self.__course_id, cw_number) for cw_number in CourseDB.get_course(self.__course_id)["cw_numbers"])
	@property
	def literatures(self):
		return tuple(Literature(self.__course_id, lit_number) for lit_number in CourseDB.get_course(self.__course_id)["lit_numbers"])
	def append_student(self, user_id):
		CourseDB.append_user_course(user_id, self.__course_id)
	def remove_student(self, user_id):
		CourseDB.remove_user_course(user_id, self.__course_id)
	def append_to_blacklist(self, user_id):
		CourseDB.append_to_blacklist(self.__course_id, user_id)
		CourseDB.remove_user_course(user_id, self.__course_id)
	def remove_from_blacklist(self, user_id):
		CourseDB.remove_from_blacklist(self.__course_id, user_id)
	def task(self, task_number=None, task_name="", task_description="", task_highest_mark=None):
		return Task(self.__course_id, task_number, task_name, task_description, task_highest_mark)
	def classwork(self, cw_number=None, cw_name="", cw_date=None):
		return Classwork(self.__course_id, cw_number, cw_name, cw_date)
	def literature(self, lit_number=None, name="", description="", file_id=None, url=""):
		return Literature(self.__course_id, lit_number, name, description, file_id, url)
	def mailing(self, email, password, text):
		participants = [User.User(user_id) for user_id in CourseDB.get_course(self.__course_id)["participants"]]
		recipients = [participant.email for participant in participants]
		Mail(email, password).send(recipients, text)
	def delete(self):
		CourseDB.delete_course(self.__course_id)
		del self.__course_id

def fetch_all_courses():
	return tuple(Course(course_id) for course_id in CourseDB.fetch_all_courses())
