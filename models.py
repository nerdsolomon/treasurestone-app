from flask_login import UserMixin
from datetime import datetime
from myapp import app, db

date = datetime.now()

class Admin(db.Model, UserMixin):
	id =  db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String, nullable=False, unique=True)
	email = db.Column(db.String, nullable=False, unique=True)
	type = db.Column(db.String)
	password = db.Column(db.String, nullable=False)
	class_ = db.relationship('Class', backref='admin')
	

class Timeline(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	time = db.Column(db.String, default=date.strftime('%d %B %Y'))
	headline = db.Column(db.String)
	content = db.Column(db.String)
	file = db.Column(db.String)
	admin = db.Column(db.String)


class Session(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	date = db.Column(db.String, default=date.strftime('%d %B %Y'))
	session = db.Column(db.String)
	term = db.Column(db.String)
	room = db.relationship("Class", backref="session", cascade="all, delete-orphan")
	active = db.relationship("Active", backref="session", cascade="all, delete-orphan")
	student = db.relationship("Student", backref="session", cascade="all, delete-orphan")


class Active(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	session_id =  db.Column(db.Integer, db.ForeignKey("session.id", ondelete="CASCADE"))
	
	
class Class(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String, unique=True) 
	announce = db.Column(db.String)
	session_id = db.Column(db.Integer, db.ForeignKey("session.id", ondelete="CASCADE"))
	subjects = db.relationship('Subject', backref='room', cascade="all, delete-orphan")
	students = db.relationship('Student', backref='room', cascade="all, delete-orphan")
	admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
	tests = db.relationship('Test', backref='room', cascade="all, delete-orphan")
	exam = db.relationship('Exam', backref='room', cascade="all, delete-orphan")


class Subject(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String, unique=True) 
	file = db.Column(db.String)
	class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete="CASCADE"))
	cbt = db.relationship('CBT', backref='subject', cascade="all, delete-orphan")
	test = db.relationship('Test', backref='subject', cascade="all, delete-orphan")
	exam = db.relationship('Exam', backref='subject', cascade="all, delete-orphan")


class Exam(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	score = db.Column(db.Integer)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"))
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"))
	class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete="CASCADE"))


class Test(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	score = db.Column(db.Integer)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"))
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"))
	class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete="CASCADE"))


class Student(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	first_name = db.Column(db.String, nullable=False)
	last_name = db.Column(db.String, nullable=False)
	email = db.Column(db.String, nullable=False, unique=True)
	sex = db.Column(db.String, nullable=False)
	comment = db.Column(db.String)
	remark = db.Column(db.String)
	password = db.Column(db.String, nullable=False)
	class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete="CASCADE"))
	tests = db.relationship('Test', backref='student', cascade="all, delete-orphan")
	exam = db.relationship('Exam', backref='student', cascade="all, delete-orphan")
	affective = db.relationship('Affective', backref='student', cascade="all, delete-orphan")
	psycho = db.relationship('Psychomotor', backref='student', cascade="all, delete-orphan")
	session_id = db.Column(db.Integer, db.ForeignKey('session.id', ondelete="CASCADE"))


class CBT(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	question = db.Column(db.String)
	file = db.Column(db.String)
	answer = db.Column(db.String)
	option1 = db.Column(db.String)
	option2 = db.Column(db.String)
	option3 = db.Column(db.String)
	type = db.Column(db.String)
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"))


class Affective(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	attentive = db.Column(db.String)
	honest = db.Column(db.String)
	neat = db.Column(db.String)
	polite = db.Column(db.String)
	punctual = db.Column(db.String)
	calm = db.Column(db.String)
	obey = db.Column(db.String)
	rely = db.Column(db.String)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"))


class Psychomotor(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	handle = db.Column(db.String)
	draw = db.Column(db.String)
	speech = db.Column(db.String)
	write = db.Column(db.String)
	public = db.Column(db.String)
	sport = db.Column(db.String)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"))


def create_model():
	with app.app_context():
		db.create_all()
		return 'Database model created successfully'