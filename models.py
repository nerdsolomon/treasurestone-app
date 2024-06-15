from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from datetime import datetime
import os


app = Flask(__name__)
#app.config["SECRET_KEY"] = "school"
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///school.db"
app.config["SECRET_KEY"] = os.environ['KEY']
app.config['SQLALCHEMY_DATABASE_URI'] =os.environ['DB_URI']

db = SQLAlchemy(app)
migrate = Migrate(app, db)
date = datetime.now()


class Slide(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	image = db.Column(db.String)


class Staff(db.Model, UserMixin):
	id =  db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String, nullable=False)
	email = db.Column(db.String, nullable=False)
	password = db.Column(db.String, nullable=False)
	role = db.Column(db.String)
	room_id = db.relationship('Class', backref="staff")


class Student(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String, nullable=False)
	other = db.Column(db.String)
	surname = db.Column(db.String, nullable=False)
	image = db.Column(db.String)
	email = db.Column(db.String, nullable=False)
	sex = db.Column(db.String, nullable=False)
	password = db.Column(db.String, nullable=False)
	remark = db.Column(db.String)
	session_id = db.Column(db.Integer, db.ForeignKey('session.id', ondelete="CASCADE"))
	room_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete="CASCADE"))
	test_id = db.relationship('Test', backref='student', cascade="all, delete-orphan")
	exam_id = db.relationship('Exam', backref='student', cascade="all, delete-orphan")
	psych_id = db.relationship("Psychomotor", backref='student', cascade="all, delete-orphan")
	affect_id = db.relationship("Affective", backref='student', cascade="all, delete-orphan")
	
	
class Class(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String, nullable=False)
	staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"))
	subject_id = db.relationship('Subject', backref='room', cascade="all, delete-orphan")
	student_id = db.relationship('Student', backref='room', cascade="all, delete-orphan")


class Subject(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String, nullable=False) 
	file = db.Column(db.String)
	room_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete="CASCADE"))
	cbt_id = db.relationship('CBT', backref='subject', cascade="all, delete-orphan")
	test_id = db.relationship('Test', backref='subject', cascade="all, delete-orphan")
	exam_id = db.relationship('Exam', backref='subject', cascade="all, delete-orphan")
	
	
class Session(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	date = db.Column(db.String, default=date.strftime('%B %Y'))
	session = db.Column(db.String, nullable=False)
	term = db.Column(db.String, nullable=False)
	active_id = db.relationship("Active", backref="session", cascade="all, delete-orphan")
	student_id = db.relationship("Student", backref="session", cascade="all, delete-orphan")
	

class Active(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	session_id =  db.Column(db.Integer, db.ForeignKey("session.id", ondelete="CASCADE"))
	

class CBT(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	question = db.Column(db.String)
	answer = db.Column(db.String)
	opt_one = db.Column(db.String)
	opt_two = db.Column(db.String)
	opt_three = db.Column(db.String)
	image = db.Column(db.String)
	type = db.Column(db.String)
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"))
	
	
class Exam(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	score = db.Column(db.Integer)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"), nullable=False)
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"))
	

class Test(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	score = db.Column(db.Integer)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"), nullable=False)
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"))


class Affective(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	attentive = db.Column(db.String, nullable=False)
	honest = db.Column(db.String, nullable=False)
	neat = db.Column(db.String, nullable=False)
	polite = db.Column(db.String, nullable=False)
	punctual = db.Column(db.String, nullable=False)
	calm = db.Column(db.String, nullable=False)
	obey = db.Column(db.String, nullable=False)
	rely = db.Column(db.String, nullable=False)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"), nullable=False)


class Psychomotor(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	handle = db.Column(db.String, nullable=False)
	draw = db.Column(db.String, nullable=False)
	speech = db.Column(db.String, nullable=False)
	write = db.Column(db.String, nullable=False)
	public = db.Column(db.String, nullable=False)
	sport = db.Column(db.String, nullable=False)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"),nullable=False)


	
def create_model():
	with app.app_context():
		db.create_all()
		return 'Database model created successfully'
		
