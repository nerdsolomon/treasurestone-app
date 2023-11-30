from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import render_template, redirect, flash, request, session, url_for, send_file
from webform import AdminForm, PostForm, ClassForm, SubjectForm, StudentForm, LoginForm, CBTForm, EditForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from werkzeug.wrappers import Response
from flask_login import UserMixin
from datetime import datetime
import pandas as pd


app = Flask(__name__)
app.config["SECRET_KEY"] = "hello..."
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///gioynekgtbdyxe:da5cad955c2d1643704828ea7bf9a76bc0b3db3aa4aeb74506e2a80903a8c45a@ec2-3-210-173-88.compute-1.amazonaws.com:5432/d3ra96ptk7vuba'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

FILE_FOLDER = "static/files/"
if not os.path.exists(FILE_FOLDER):
	os.makedirs(FILE_FOLDER)
	
app.config["FILE_FOLDER"] = FILE_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(id):
	if session['account'] == 'Admin':
		return Admin.query.get(int(id))
	elif session['account'] == 'Student':
		return Student.query.get(int(id))
	else:
		return None


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



def frame(id):
	first_name = [i.student.first_name for i in Test.query.filter_by(class_id=id).order_by(Test.student_id)]
	last_name = [i.student.last_name for i in Test.query.filter_by(class_id=id).order_by(Test.student_id)]
	subject = [i.subject.title for i in Test.query.filter_by(class_id=id).order_by(Test.student_id)]
	score = [i.score for i in Test.query.filter_by(class_id=id).order_by(Test.student_id)]
	content = {"Name" : first_name, "Surname" : last_name, "Subject" : subject, "Test" : score}
	test = pd.DataFrame(content)
	
	first_names = [i.student.first_name for i in Exam.query.filter_by(class_id=id).order_by(Exam.student_id)]
	last_names = [i.student.last_name for i in Exam.query.filter_by(class_id=id).order_by(Exam.student_id)]
	subjects = [i.subject.title for i in Exam.query.filter_by(class_id=id).order_by(Exam.student_id)]
	scores = [i.score for i in Exam.query.filter_by(class_id=id).order_by(Exam.student_id)]
	contents = {"Name" : first_name, "Surname" : last_names, "Subject" : subjects, "Exam" : scores}
	exam = pd.DataFrame(contents)
		
	result = test.merge(exam)
	result["Total"] = result["Exam"] + result["Test"]
	result["Student"] = result["Name"] +" "+ result["Surname"]
	result.drop(columns=["Name", "Surname"], inplace=True)
	
	new = result.pivot("Student", "Subject")
	new["Comment"] = [i.comment for i in Student.query.filter_by(class_id=id).order_by(Student.id)]
	new["Remark"] = [i.remark for i in Student.query.filter_by(class_id=id).order_by(Student.id)]
	new["Sum Total"] = result["Test"].groupby(result["Student"]).sum() + result["Exam"].groupby(result["Student"]).sum()
	new["Average"] = new["Sum Total"] / Exam.query.filter_by(class_id=id).count()
	
	news = new.swaplevel(0, 1, 1).sort_index(1)
	return news



def frame2(id):
	subjects = [i.subject.title for i in Exam.query.filter_by(student_id=id)]
	scores = [i.score for i in Exam.query.filter_by(student_id=id)]
	datas = {"Subject" : subjects, "Exam" : scores}
	exam = pd.DataFrame(datas)
	
	subject = [i.subject.title for i in Test.query.filter_by(student_id=id)]
	score = [i.score for i in Test.query.filter_by(student_id=id)]
	data = {"Subject" : subject, "Test" : score}
	test = pd.DataFrame(data)
	
	result = test.merge(exam)
	result["Score"] = result["Exam"] + result["Test"]
	
	grade = []
	for x in range(len(result["Score"])):
		if result["Score"][x] >= 70:
			grade.append("A")
		elif result["Score"][x] >= 60:
			grade.append("B")
		elif result["Score"][x] >= 50:
			grade.append("C")
		elif result["Score"][x] >= 45:
			grade.append("D")
		elif result["Score"][x] >= 40:
			grade.append("E")
		else:
			grade.append("F")
	
	result["Grade"] = grade
	return result



def other(id):
	affective = Affective.query.filter_by(student_id=id).first()
	
	data = {"AFFECTIVE DOMAIN" : ["Attentiveness", "Honesty", "Neatness", "Politeness", "Punctuality/Assembly", "Self-Control/Calmness", "Obedience", "Reliability"], "RATING" : [affective.attentive, affective.honest, affective.neat, affective.polite, affective.punctual, affective.calm, affective.obey, affective.rely]}
	frame = pd.DataFrame(data)
	return frame

def other2(id):
	psych = Psychomotor.query.filter_by(student_id=id).first()
	
	data = {"PSYCHOMOTOR DOMAIN" : ["Handling Of Tools", "Drawing And Painting", "Handwriting", "Speech Fluency", "Sport And Games", "Public Speaking"], "RATING" : [psych.handle, psych.draw, psych.write, psych.speech, psych.sport, psych.public] }
	frame = pd.DataFrame(data)
	return frame





choices, answers = [], []

@app.context_processor
def base():
	time = date.strftime('%Y')
	active = Active.query.first()
	if current_user.is_authenticated:
		account = session["account"]
		if account == "Student":
			classed = Class.query.filter_by(session_id=active.session.id).filter_by(id=current_user.room.id).first()
			subjects = Subject.query.filter_by(class_id=classed.id)
			return dict(student=student, account=account,subjects=subjects, time=time, active=active)
		elif account == "Admin":
			admin = Admin.query.filter_by(id=current_user.id).first()
			rooms = Class.query.filter_by(session_id=active.session.id).order_by(Class.id)
			return dict(rooms=rooms, account=account, admin=admin, time=time, active=active)
	return dict(time=time, active=active)


def store(var):
	db.session.add(var)
	db.session.commit()

def rem(var):
	db.session.delete(var)
	db.session.commit()
	
	
@app.route('/setting', methods=['POST', 'GET'])
def setting():
	form = EditForm()
	active = Active.query.first()
	session = Session.query.order_by(-Session.id)
	if request.method == "POST":
		type = request.form["name"]
		if type == "session":
			new = Session(session=form.string.data, term=request.form["term"])
			db.session.add(new)
			db.session.commit()
		elif type == "active":
			if active:
				active.session_id = request.form["session"]
				db.session.add(active)
				db.session.commit()
			else:
				active = Active(session_id=request.form["session"])
				db.session.add(active)
				db.session.commit()
	return render_template("setting.html", form=form, sessions=session)


@app.route('/download/<path:filename>')
def download(filename):
    return send_file(app.config['FILE_FOLDER'] + filename)


@app.route('/cbt/<int:id>', methods=['POST', 'GET'])
@login_required
def cbt(id):
	tests = Test.query.filter_by(subject_id=id)
	for test in tests:
		if current_user.id == test.student.id:
			flash("You've already taken this test. View your Result...")
			return redirect(url_for('subject', id=id))
	
	ROWS_PER_PAGE = 1
	page = request.args.get('page', 1, type=int)
	subject = Subject.query.filter_by(id=id).first()
	cbts = CBT.query.filter_by(subject_id=id).filter_by(type="Test").paginate(page=page, per_page=ROWS_PER_PAGE)
	
	if request.method == "POST":
		try:
			choice = request.form["option"]
			for cbt in cbts.items:
				choices.append(choice)
				answers.append(cbt.answer)
			
			if cbts.page == cbts.pages:
				score = 0
				for choice, answer in zip(choices, answers):
					if choice == answer:
						score += 1
				test = Test(score=score, student_id=current_user.id, subject_id=id, class_id=current_user.room.id)
				store(test)
				return render_template('score.html', subject=subject, cbts=cbts, score=score)
		except:
			for page_num in cbts.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2):
				flash('You must make a choice to continue...')
				return redirect(url_for('cbt', page=page_num, id=subject.id))
		return redirect(url_for('cbt', page=cbts.next_num, id=subject.id))
	return render_template('cbt.html', subject=subject, cbts=cbts)



@app.route('/exam/<int:id>', methods=['POST', 'GET'])
@login_required
def exam(id):
	questions = CBT.query.filter_by(subject_id=id)
	exams = Exam.query.filter_by(subject_id=id)
	for exam in exams:
		if current_user.id == exam.student.id:
			flash("You've already taken this exam. View your Result...")
			return redirect(url_for('subject', id=id))
	
	ROWS_PER_PAGE = 1
	page = request.args.get('page', 1, type=int)
	subject = Subject.query.filter_by(id=id).first()
	cbts = CBT.query.filter_by(subject_id=id).filter_by(type="Exam").paginate(page=page, per_page=ROWS_PER_PAGE)
	
	if request.method == "POST":
		try:
			choice = request.form["option"]
			for cbt in cbts.items:
				choices.append(choice)
				answers.append(cbt.answer)
			
			if cbts.page == cbts.pages:
				score = 0
				for choice, answer in zip(choices, answers):
					if choice == answer:
						score += 1
				exam = Exam(score=score, student_id=current_user.id, subject_id=id, class_id=current_user.room.id)
				store(exam)
				return render_template('score.html', subject=subject, cbts=cbts, score=score)
		except:
			for page_num in cbts.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2):
				flash('You must make a choice to continue...')
				return redirect(url_for('cbt', page=page_num, id=subject.id))
		return redirect(url_for('cbt', page=cbts.next_num, id=subject.id))
	return render_template('cbt.html', subject=subject, cbts=cbts)



@app.route('/cbt-questions/<int:id>', methods=["POST", "GET"])
@login_required
def cbt_question(id):
	subject = Subject.query.filter_by(id=id).first()
	cbts = CBT.query.filter_by(subject_id=id)
	form = CBTForm()
	if form.validate_on_submit():
		if form.file.data:
			name = secure_filename(form.file.data.filename)
			file_name = str(uuid.uuid1()) + "-" + subject.room.title + "_" + subject.title + "_" + name
			form.file.data.save(os.path.join(app.config["FILE_FOLDER"], file_name))
			cbt = CBT(question=form.question.data, answer=form.answer.data, option1=form.option1.data, option2=form.option2.data, option3=form.option3.data, file=file_name, subject_id=id, type=request.form['type'])
			store(cbt)
		else:
			cbt = CBT(question=form.question.data, answer=form.answer.data, option1=form.option1.data, option2=form.option2.data, option3=form.option3.data, file=form.file.data.read(), subject_id=id, type=request.form['type'])
			store(cbt)
	form.question.data, form.answer.data, form.option1.data, form.option2.data, form.option3.data = ("","","","","")
	return render_template('cbt_question.html', subject=subject, cbts=cbts, form=form)
	


@app.route('/result/<int:id>', methods=['POST', 'GET'])
@login_required
def result(id):
	if session["account"] == "Student":
		try:
			psych = other2(id)
			affect = other(id)
			results = frame2(id)
			return render_template("result.html", psych=[psych.to_html(classes="table table-hover table-bordered table-sm", justify="left",index=False)], tables=[results.to_html(classes="table table-hover table-bordered table-sm", justify="left", index=False)], affect=[affect.to_html(classes="table table-hover table-bordered table-sm", justify="left",index=False)])
		except:
			flash("Result is incomplete. If you've completed Exams and Tests for all Subjects, contact your Teacher.")
			return redirect('/student')
	else:
		try:
			sheet = frame(id)
			room = Class.query.filter_by(id=id).first()
			students = Student.query.filter_by(class_id=id)
			test_st = Test.query.filter_by(class_id=id).group_by(Test.student_id)
			test_sub = Test.query.filter_by(class_id=id).group_by(Test.subject_id)
			exam_st = Exam.query.filter_by(class_id=id).group_by(Exam.student_id)
			exam_sub = Exam.query.filter_by(class_id=id).group_by(Exam.subject_id)
			if request.method == "POST":
				type = request.form["name"]
				if type == "comment":
					student = request.form["student"]
					news = Student.query.filter_by(id=student).first()
					news.comment = request.form["comment"]
					if student or news.comment == None:
						flash("You must fill all forms")
					store(news)
				elif type == "remark":
					student = request.form["student"]
					news = Student.query.filter_by(id=student).first()
					news.remark = request.form["remark"]
					if student or news.remark == None:
						flash("You must fill all forms")
					store(news)
				elif type == "test":
					student = request.form["student"]
					subject = request.form["subject"]
					test = Test.query.filter_by(subject_id=subject).filter_by(student_id=student).first()
					test.score = request.form["score"]
					if test.score or test == None:
						flash("You must fill all forms")
					store(test)
				elif type == "exam":
					student = request.form["student"]
					subject = request.form["subject"]
					exam = Exam.query.filter_by(subject_id=subject).filter_by(student_id=student).first()
					exam.score = request.form["score"]
					if exam.score or exam == None:
						flash("You must fill all forms")
					store(exam)
			return render_template("result.html", students=students,room=room, test_st=test_st, test_sub=test_sub, exam_st=exam_st,exam_sub=exam_sub, tables=[sheet.to_html(classes="table table-hover table-sm table-bordered" )])
		except:
			flash("All students must complete all Exams and Tests before you can access this page")
			return redirect("/admin")



@app.route('/save_sheet/<int:id>')
@login_required
def save_sheet(id):
	room = Class.query.filter_by(id=id).first()
	new = frame(id)
	resp = Response(new.to_csv()) 
	resp.headers={"Content-Disposition": "attachment;" "filename={}".format(room.title +" Broadsheet.csv") }
	resp.headers["Content-Type"] = "text/csv" 
	return resp



@app.route('/', methods = ['POST', 'GET'])
def timeline():
	choices.clear(), answers.clear()
	page = request.args.get('page', 1, type=int)
	posts = Timeline.query.order_by(-Timeline.id).paginate(page=page, per_page=5)
	form = PostForm()
	if form.validate_on_submit():
		if form.file.data:
			name = secure_filename(form.file.data.filename)
			file_name = str(uuid.uuid1()) + "-" + name 
			form.file.data.save(os.path.join(app.config["FILE_FOLDER"], file_name))
			post = Timeline(content=form.content.data, file=file_name, headline=form.headline.data, admin=current_user.username)
			store(post)
			return redirect('/')
		else:
			post = Timeline(content=form.content.data, file=form.file.data.read(), headline=form.headline.data, admin=current_user.username)
			try:
				store(post)
				return redirect('/')
			except:
				flash('Post not added, check forms and try again...')
	return render_template('timeline.html', posts=posts, form=form)



@app.route('/admin-login', methods = ['POST', 'GET'])
def admin_login():
	form = LoginForm()
	if form.validate_on_submit():
		admin = Admin.query.filter_by(email=form.email.data).first()
		if admin:
			passed = check_password_hash(admin.password, form.password.data)
			if passed == True:
				login_user(admin)
				session['account'] = 'Admin'
				flash("Welcome "+ current_user.username )
				return redirect('/admin')
			else:
				flash('Password is incorrect...')
		else:
			flash('User does not exist. Signup...')
	return render_template('log.html', form=form)					



@app.route('/login/<int:id>', methods = ['POST', 'GET'])
def login(id):
	form = LoginForm()
	if form.validate_on_submit():
		user = Student.query.filter_by(session_id=id).filter_by(email=form.email.data).first()
		if user:
			passed = check_password_hash(user.password, form.password.data)
			if passed == True:
				login_user(user)
				session['account'] = 'Student'
				flash("Welcome "+ current_user.first_name )
				return redirect('/student')
			else:
				flash('Password is incorrect...')
		else:
			flash('Email does not exist. Signup...')
	return render_template('login.html', form=form)



@app.route('/student', methods=["POST", "GET"])
@login_required
def student():
	id = current_user.id
	choices.clear(), answers.clear()
	form = EditForm()
	student = Student.query.filter_by(id=id).first()
	if request.method == "POST":
		type = request.form["name"]
		if type == "email":
			passed = check_password_hash(student.password, form.old_pass.data)
			if passed == True:
				student.email = form.email.data
				store(student)
			else:
				flash("Password is incorrect")
		elif type == "password":
			passed = check_password_hash(student.password, form.old_pass.data)
			if passed == True:
				student.password = generate_password_hash(form.new_pass.data)
				store(student)
				flash("Password change successful...")
			else:
				flash("Old password is incorrect")
	form.email.data = student.email
	return render_template('student.html', form=form)
	


@app.route('/admin', methods=["POST", "GET"])
@login_required
def admin():
	id = current_user.id
	form = EditForm()
	admin = Admin.query.filter_by(id=id).first()
	if request.method == "POST":
		type = request.form["name"]
		if type == "email":
			passed = check_password_hash(admin.password, form.old_pass.data)
			if passed == True:
				admin.email = form.email.data
				store(admin)
			else:
				flash("Password is incorrect")
		elif type == "password":
			passed = check_password_hash(admin.password, form.old_pass.data)
			if passed == True:
				admin.password = generate_password_hash(form.new_pass.data)
				store(admin)
				flash("Password change successful...")
			else:
				flash("Old password is incorrect")
	form.email.data = admin.email
	return render_template('admin.html', form=form)



@app.route('/students/<int:id>', methods = ['POST', 'GET'])
@login_required
def students(id):
	form = StudentForm()
	students = Student.query.filter_by(class_id=id)
	room = Class.query.filter_by(id=id).first()
	
	if form.validate_on_submit():
		user = Student(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, sex=request.form['gender'], password=generate_password_hash(form.password.data), class_id=room.id, session_id=room.session.id)
		try:
			store(user)
			flash(form.first_name.data + " " + form.last_name.data + " " + "is successfully enrolled...")
			form.first_name.data = ' '
			form.last_name.data = ' '
			form.email.data = ' ' 
		except:
			flash('Student not added. Check forms and try again...')

	return render_template('students.html', students=students, room=room, form=form)



@app.route('/subject/<int:id>')
@login_required
def subject(id):
	choices.clear(), answers.clear()
	subject = Subject.query.filter_by(id=id).first()
	return render_template('subject.html', subject=subject)



@app.route('/class/<int:id>', methods=["POST", "GET"])
@login_required
def class_(id):
	form = SubjectForm()
	room = Class.query.filter_by(id=id).first()
	subjects = Subject.query.filter_by(class_id=room.id)
	admins = Admin.query.filter_by(type="Tutor").order_by(Admin.id)
	if request.method == "POST":
		type = request.form["name"]
		if type == "announce":
			room.announce = form.content.data
			store(room)
		elif type == "material":
			if request.method == "POST":
				id = request.form["sub"]
				subject = Subject.query.filter_by(id=id).first()
				if subject.file:
					os.remove('static/files/' + subject.file)
				name = secure_filename(form.file.data.filename)
				file_name = room.title  + "_" + name 
				form.file.data.save(os.path.join(app.config["FILE_FOLDER"], file_name))
				subject.file = file_name
				store(subject)
		elif type == "subject":
			subject = Subject(title=form.title.data, class_id=id)
			store(subject)
			form.title.data = ""
	form.content.data = room.announce
	return render_template('class.html', subjects=subjects, classed=room, form=form, admins=admins) 



@app.route('/classes/<int:id>', methods=['POST', 'GET'])
@login_required
def classes(id):
	form = ClassForm()
	sessions = Session.query.filter_by(id=id).first()
	admins = Admin.query.order_by(Admin.id)
	classes = Class.query.filter_by(session_id=id).order_by(Class.id)
	if request.method == "POST":
		type = request.form["name"]
		if type == "class":
			class_ = Class(title=form.title.data, session_id=sessions.id)
			store(class_)
		elif type == "admins":
			class_ = Class.query.filter_by(id=request.form["class"]).first()
			class_.admin_id = request.form['admin']
			store(class_)
	return render_template('classes.html', classes=classes, form=form, sess=id, admins=admins) 



@app.route('/view-scores/<int:id>', methods = ['POST', 'GET'])
@login_required
def view_scores(id):
	form = EditForm()
	subject = Subject.query.filter_by(id=id).first()
	students = Student.query.filter_by(class_id=subject.room.id)
	exams = Exam.query.filter_by(subject_id=subject.id)
	tests = Test.query.filter_by(subject_id=subject.id)
	if request.method == "POST":
		type = request.form["name"]
		if type == "exam":
			student = request.form["student"]
			score = form.number.data
			result = Exam.query.filter_by(subject_id=subject.id).filter_by(student_id=student).first()
			if score == None:
				flash("You must input in all fields")
			elif result:
				flash("This student already have a Exam score for this subject")
			else:
				new = Exam(class_id=subject.room.id, score=score, student_id=student, subject_id=subject.id)
				store(new)
				form.number.data = ''
				flash("Exam score added successfully!")
		elif type == "test":
			student = request.form["student"]
			score = form.number.data
			result = Test.query.filter_by(subject_id=subject.id).filter_by(student_id=student).first()
			if score == None:
				flash("You must input in all fields")
			elif result:
				flash("This student already have a Test score for this subject")
			else:
				new = Test(class_id=subject.room.id, score=score, student_id=student, subject_id=subject.id)
				store(new)
				form.number.data = ''
				flash("Test score added successfully!")
	return render_template("view_scores.html", form=form, students=students, subject=subject, tests=tests, exams=exams)



@app.route('/post/<int:id>', methods = ['POST', 'GET'])
def post(id):
	form = PostForm()
	post = Timeline.query.filter_by(id=id).first()
	if request.method == "POST":
		post.headline = form.headline.data
		post.content = form.content.data
		store(post)
		return redirect(url_for("post", id=id))
	form.headline.data = post.headline
	form.content.data = post.content
	return render_template("post.html", post=post, form=form)



@app.route('/psych-affect/<int:id>', methods=['POST', 'GET'])
@login_required
def psych_affect(id):
	students = Student.query.filter_by(class_id=id)
	room = Class.query.filter_by(id=id).first()
	if request.method == "POST":
		type = request.form["name"]
		if type == "psych":
			psych = Psychomotor.query.filter_by(student_id=request.form["student"]).first()
			if psych:
				flash("This student is already graded for psychomotor rating")
			else:
				new = Psychomotor(student_id=request.form["student"], handle=request.form["handle"], draw=request.form["draw"], speech=request.form["speech"], write=request.form["write"], public=request.form["public"], sport=request.form["sport"])
				store(new)
				flash("Psychomotor grades added successfully!")

		if type == "affect":
			affect = Affective.query.filter_by(student_id=request.form["student"]).first()
			if affect:
				flash("This student is already graded for affective rating.")
			else:
				new = Affective(student_id=request.form["student"], attentive=request.form["attentive"], punctual=request.form["punctual"], honest=request.form["honest"], neat=request.form["neat"], polite=request.form["polite"], calm=request.form["calm"],obey=request.form["obey"],rely=request.form["rely"])
				store(new)
				flash("Affective grades added successfully!")
	return render_template("psych_affect.html", room=room,students=students)



@app.route('/contact', methods = ['POST', 'GET'])
def contact():
	choices.clear(), answers.clear()
	form = AdminForm()
	admins = Admin.query.order_by(Admin.id)
	if request.method == "POST":
		type = request.form["name"]
		if type == "add":
			user = Admin(username=form.username.data, email=form.email.data, type=request.form["type"], password=generate_password_hash(form.password.data))
			try:
				store(user)
			except:
				flash('User not added. Check forms and try again...')
			return render_template('contact.html', admins=admins, form=form)
		elif type == "edit":
			user = Admin.query.filter_by(id=request.form["id"]).first()
			user.type = request.form["type"]
			store(user)
	return render_template("contact.html", form=form, admins=admins)



@app.route('/del-admin/<int:id>')
@login_required
def del_admin(id):
	admin = Admin.query.filter_by(id=id).first()
	rem(admin)
	return redirect('/contact')


@app.route('/del-student/<int:id>/<int:num>')
@login_required
def del_student(id, num):
	student = Student.query.filter_by(id=id).first()
	rem(student)
	return redirect(url_for("students", id=num))


@app.route('/del-post/<int:id>')
@login_required
def del_post(id):
	timeline = Timeline.query.filter_by(id=id).first()
	if timeline.file:
		os.remove('static/files/' + timeline.file)
	rem(timeline)
	return redirect('/')
	
	
@app.route('/del-class/<int:id>/<int:num>')
@login_required
def del_class(id,num):
	clas = Class.query.filter_by(id=id).first()
	rem(clas)
	return redirect(url_for("classes", id=num))


@app.route('/del-subject/<int:id>/<int:num>')
@login_required
def del_subject(id,num):	
	subject = Subject.query.filter_by(id=id).first()
	if subject.file:
		os.remove('static/files/' + subject.file)
		rem(subject)
		flash("Subject delete successful")
		return redirect(url_for("class_", id=num))
	else:
		rem(subject)
		flash("Subject delete successful")
		return redirect(url_for("class_", id=num))


@app.route('/del-cbt/<int:id>/<int:num>')
@login_required
def del_cbt(id,num):	
	cbt = CBT.query.filter_by(id=id).first()
	if cbt.file:
		os.remove('static/files/' + cbt.file)
	rem(cbt)
	return redirect(url_for('cbt_question',id=num))
	
	
@app.route('/about')
def about():
	return render_template("about.html")
	
														
@app.route('/logout')
def logout():
	logout_user()
	flash("You've been logged out...")
	return redirect('/')


@app.route('/library')
def library():
	choices.clear(), answers.clear()
	page = request.args.get('page', 1, type=int)
	subject = Subject.query.order_by(-Subject.id).paginate(page=page, per_page=20)
	return render_template("library.html", subject=subject)
	