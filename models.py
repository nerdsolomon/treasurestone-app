from flask import Flask, session # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_migrate import Migrate # type: ignore
from flask_login import LoginManager, UserMixin # type: ignore
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "school"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///school.db"
#app.config["SECRET_KEY"] = os.environ['KEY']
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_URI']
#app.config['GOOGLE_APPLICATION_CREDENTIALS'] = os.environ['CREDENTIALS']

FILE_FOLDER = "static/storage"
if not os.path.exists(FILE_FOLDER):
	os.makedirs(FILE_FOLDER)
app.config["FILE_FOLDER"] = FILE_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)
date = datetime.now()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "homepage"

@login_manager.user_loader
def load_user(user):
    return Staff.query.get(user) if session.get("account") == "Staff" else Student.query.get(user)


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
	grade_id = db.relationship('Grade', backref='student', cascade="all, delete-orphan")
 
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
	grade_id = db.relationship('Grade', backref='subject', cascade="all, delete-orphan")
	
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
	type = db.Column(db.String)
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"))
	
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam = db.Column(db.Float, default=0)
    test = db.Column(db.Float, default=0)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"), nullable=False)

def create_model():
	with app.app_context():
		db.create_all()
		return 'Database model created successfully'