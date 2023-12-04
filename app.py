from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import render_template, redirect, flash, request, session, url_for, send_file, abort, send_from_directory
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
from PIL import Image
import io


app = Flask(__name__)
app.config["SECRET_KEY"] = "hello..."
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://beqmdjbioqowdx:31f36efcea974bbbe4828329bfabfb45d6481f10808597d0c878de22213db68f@ec2-44-214-132-149.compute-1.amazonaws.com:5432/d3lhkcoo7tvp7d'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

FILE_FOLDER = "static"
#if not os.path.exists(FILE_FOLDER):
#	os.makedirs(FILE_FOLDER)
	
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


class Gallery(db.Model):
	id =  db.Column(db.Integer, primary_key = True)
	file = db.Column(db.String)


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


def crop_image(img):
	image = Image.open(io.BytesIO(img))
	width, height = image.size
	if width == height:
	   return image
	offset  = int(abs(height-width)/2)
	if width>height:
		image = image.crop([offset,0,width-offset,height])
	else:
		image = image.crop([0,offset,width,height-offset])
	return image


def frame(id):
    student_data = Student.query.filter_by(class_id=id).order_by(Student.id).all()
    student_info = db.session.query(Student, Exam, Test)\
    .join(Exam, Student.id == Exam.student_id)\
    .join(Test, Student.id == Test.student_id)\
    .filter_by(class_id=id).order_by(Student.id)\
    .filter(Exam.subject_id == Test.subject_id).all()
    
    columns = ["Student", "Subject", "Exam", "Test", "Total"]
    df = pd.DataFrame(columns=columns)
    
    for x, student in zip(range(len(student_info)), student_info):
        df.loc[x, ["Student"]] = student[0].first_name + " " + student[0].last_name
        df.loc[x, ["Subject"]] = student[1].subject.title
        df.loc[x, ["Exam"]] = student[1].score
        df.loc[x, ["Test"]] = student[2].score
        df.loc[x, ["Total"]] = student[1].score + student[2].score

    new = df.pivot("Student", "Subject")
    new["Added Total"] = df.groupby("Student")[["Test", "Exam"]].sum().sum(axis=1)
    new["Average"] = new["Added Total"] / len(student_info)
    new["Comment"] = [i.comment for i in student_data]
    new["Remark"] = [i.remark for i in student_data]
    news = new.swaplevel(0, 1, 1).sort_index(1)
    return news



def frame2(id):
    exam_data = Exam.query.filter_by(student_id=id).all()
    test_data = Test.query.filter_by(student_id=id).all()

    exam_content = {"Subject": [i.subject.title for i in exam_data],
                    "Exam": [i.score for i in exam_data]}

    test_content = {"Subject": [i.subject.title for i in test_data],
                    "Test": [i.score for i in test_data]}

    exam_df = pd.DataFrame(exam_content)
    test_df = pd.DataFrame(test_content)

    result = test_df.merge(exam_df, on="Subject", how="outer", suffixes=('_Test', '_Exam'))
    result["Score"] = result["Exam"].fillna(0) + result["Test"].fillna(0)

    # Use vectorized operations for assigning grades
    result["Grade"] = pd.cut(result["Score"], bins=[0, 40, 45, 50, 60, 70, float('inf')], labels=['F', 'E', 'D', 'C', 'B', 'A'])

    return result


def other(id):
    affective = Affective.query.filter_by(student_id=id).first()

    if affective:
        data = {"AFFECTIVE DOMAIN": ["Attentiveness", "Honesty", "Neatness", "Politeness", "Punctuality/Assembly", "Self-Control/Calmness", "Obedience", "Reliability"], "RATING": [affective.attentive, affective.honest, affective.neat, affective.polite, affective.punctual, affective.calm, affective.obey, affective.rely]}
        frame = pd.DataFrame(data)
        return frame
    else:
        return pd.DataFrame()  # or handle the case where affective data is not found

def other2(id):
    psych = Psychomotor.query.filter_by(student_id=id).first()

    if psych:
        data = {"PSYCHOMOTOR DOMAIN": ["Handling Of Tools", "Drawing And Painting", "Handwriting", "Speech Fluency", "Sport And Games", "Public Speaking"], "RATING": [psych.handle, psych.draw, psych.write, psych.speech, psych.sport, psych.public]}
        frame = pd.DataFrame(data)
        return frame
    else:
        return pd.DataFrame()  # or handle the case where psychomotor data is not found



choices = []
answers = []


def store(var):
	db.session.add(var)
	db.session.commit()

def rem(var):
	db.session.delete(var)
	db.session.commit()
	

# Define the allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.context_processor
def base():
    time = date.strftime('%Y')
    active = Active.query.first()
    account = session.get("account")

    if current_user.is_authenticated and account:
        if account == "Student":
            student = current_user  # Use the authenticated student
            classed = Class.query.filter_by(session_id=active.session.id, id=current_user.room.id).first()
            subjects = Subject.query.filter_by(class_id=classed.id)
            return dict(student=student, account=account, subjects=subjects, time=time, active=active)
        elif account == "Admin":
            admin = Admin.query.filter_by(id=current_user.id).first()
            rooms = Class.query.filter_by(session_id=active.session.id).order_by(Class.id)
            return dict(rooms=rooms, account=account, admin=admin, time=time, active=active)

    return dict(time=time, active=active)



@app.route('/setting', methods=['POST', 'GET'])
def setting():
    form = EditForm()
    active = Active.query.first()
    sessions = Session.query.order_by(-Session.id)

    if request.method == "POST":
        action_type = request.form["name"]

        if action_type == "session":
            new_session = Session(session=form.string.data, term=request.form["term"])
            db.session.add(new_session)
            db.session.commit()
            flash("New session added successfully.")
        elif action_type == "active":
            if active:
                active.session_id = request.form["session"]
            else:
                active = Active(session_id=request.form["session"])
                db.session.add(active)
            
            db.session.commit()
            flash("Active session updated successfully.")

    return render_template("setting.html", form=form, sessions=sessions)




@app.route('/download/<path:filename>')
def download(filename):
    # Validate and sanitize the filename
    filename = secure_filename(filename)
    try:
        return send_from_directory(app.config['FILE_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)  # Adjust the response code according to your project's needs




@app.route('/cbt/<int:id>', methods=['POST', 'GET'])
@login_required
def cbt(id):
    tests = Test.query.filter_by(subject_id=id, student_id=current_user.id).all()
    if tests:
        flash("You've already taken this test. View your result.")
        return redirect(url_for('subject', id=id))

    ROWS_PER_PAGE = 1
    page = request.args.get('page', 1, type=int)
    subject = Subject.query.filter_by(id=id).first()
    cbts = CBT.query.filter_by(subject_id=id, type="Test").paginate(page=page, per_page=ROWS_PER_PAGE)

    if request.method == "POST":
        try:
            choice = request.form["option"]
            for cbt in cbts.items:
                choices.append(choice)
                answers.append(cbt.answer)

            if cbts.page == cbts.pages:
                score = sum(choice == answer for choice, answer in zip(choices, answers))
                test = Test(score=score, student_id=current_user.id, subject_id=id, class_id=current_user.room.id)
                store(test)
                return render_template('score.html', subject=subject, cbts=cbts, score=score)

        except KeyError:
            flash('You must make a choice to continue...')
            return redirect(url_for('cbt', page=cbts.next_num, id=subject.id))
    return render_template('cbt.html', subject=subject, cbts=cbts)



@app.route('/exam/<int:id>', methods=['POST', 'GET'])
@login_required
def exam(id):
    exams_taken = Exam.query.filter_by(subject_id=id, student_id=current_user.id).all()
    if exams_taken:
        flash("You've already taken this exam. View your result.")
        return redirect(url_for('subject', id=id))

    ROWS_PER_PAGE = 1
    page = request.args.get('page', 1, type=int)
    subject = Subject.query.filter_by(id=id).first()
    cbts = CBT.query.filter_by(subject_id=id, type="Exam").paginate(page=page, per_page=ROWS_PER_PAGE)

    if request.method == "POST":
        try:
            choice = request.form["option"]
            for cbt in cbts.items:
                choices.append(choice)
                answers.append(cbt.answer)

            if cbts.page == cbts.pages:
                score = sum(choice == answer for choice, answer in zip(choices, answers))
                exam_taken = Exam(score=score, student_id=current_user.id, subject_id=id, class_id=current_user.room.id)
                store(exam_taken)
                return render_template('score.html', subject=subject, cbts=cbts, score=score)

        except KeyError:
            flash('You must make a choice to continue...')
            return redirect(url_for('exam', page=cbts.next_num, id=subject.id))
    return render_template('exam.html', subject=subject, cbts=cbts)



@app.route('/cbt-questions/<int:id>', methods=["POST", "GET"])
@login_required
def cbt_question(id):
    subject = Subject.query.filter_by(id=id).first()
    cbts = CBT.query.filter_by(subject_id=id)
    form = CBTForm()

    if form.validate_on_submit():
        try:
            if form.file.data:
                file = form.file.data
                if file and allowed_file(file.filename):
                    file_name = secure_filename(file.filename)
                    file_path = os.path.join(app.config["FILE_FOLDER"], file_name)
                    crop_image(file.read()).save(file_path)
                    cbt = CBT(question=form.question.data, answer=form.answer.data,
                              option1=form.option1.data, option2=form.option2.data, option3=form.option3.data,
                              file=file_name, subject_id=id, type=request.form['type'])
                    store(cbt)
                else:
                    flash("Invalid file type. Allowed types: {}".format(", ".join(ALLOWED_EXTENSIONS)))
            else:
                cbt = CBT(question=form.question.data, answer=form.answer.data,
                          option1=form.option1.data, option2=form.option2.data, option3=form.option3.data,
                          subject_id=id, type=request.form['type'])
                store(cbt)

            flash("Question added successfully.")
        except Exception as e:
            flash("An error occurred while adding the question: {}".format(str(e)))

        return redirect(url_for('cbt_question', id=id))

    return render_template('cbt_question.html', subject=subject, cbts=cbts, form=form)



@app.route('/result/<int:id>', methods=['POST', 'GET'])
@login_required
def result(id):
    #try:
    account_type = session.get("account")
    
    if account_type == "Student":
        psych = other2(id)
        affect = other(id)
        results = frame2(id)
        return render_template("result.html", psych=[psych.to_html(classes="table table-hover table-bordered table-sm", justify="left", index=False)], tables=[results.to_html(classes="table table-hover table-bordered table-sm", justify="left", index=False)],affect=[affect.to_html(classes="table table-hover table-bordered table-sm", justify="left", index=False)])
    
    else:
        sheet = frame(id)
        room = Class.query.filter_by(id=id).first()
        students = Student.query.filter_by(class_id=id)
        test_st = db.session.query(Test, db.func.avg(Test.student_id)).filter_by(class_id=id).group_by(Test.student_id)
        test_sub = db.session.query(Test, db.func.avg(Test.subject_id)).filter_by(class_id=id).group_by(Test.subject_id)
        exam_st = db.session.query(Exam, db.func.avg(Exam.student_id)).filter_by(class_id=id).group_by(Exam.student_id)
        exam_sub = db.session.query(Exam, db.func.avg(Exam.subject_id)).filter_by(class_id=id).group_by(Exam.subject_id)
        
        if request.method == "POST":
            try:
                form_type = request.form["name"]
                if form_type == "comment" or form_type == "remark":
                    student_id = request.form["student"]
                    student = Student.query.filter_by(id=student_id).first()
                    
                    if form_type == "comment":
                        student.comment = request.form["comment"]
                    elif form_type == "remark":
                        student.remark = request.form["remark"]
                        
                    if not student_id or not request.form[form_type]:
                        flash("You must fill all forms")
                    else:
                        store(student)
                
                elif form_type == "test" or form_type == "exam":
                    student_id = request.form["student"]
                    subject_id = request.form["subject"]
                    
                    if form_type == "test":
                        test = Test.query.filter_by(subject_id=subject_id, student_id=student_id).first()
                        test.score = request.form["score"]
                    elif form_type == "exam":
                        exam = Exam.query.filter_by(subject_id=subject_id, student_id=student_id).first()
                        exam.score = request.form["score"]

                    if not student_id or not subject_id or not request.form["score"]:
                        flash("You must fill all forms")
                    else:
                        store(test) if form_type == "test" else store(exam)
            
            except KeyError:
                flash("Invalid form submission")
                
            return redirect(url_for('result', id=id))
        
        return render_template("result.html", students=students, room=room, test_st=test_st, test_sub=test_sub, exam_st=exam_st, exam_sub=exam_sub, tables=[sheet.to_html(classes="table table-hover table-sm table-bordered")])

    #except:
        #flash("All Student must have a score for every subject.")
        #return redirect("/")



@app.route('/save_sheet/<int:id>')
@login_required
def save_sheet(id):
    class_obj = Class.query.get(id)

    if class_obj:
        sheet_data = frame(id)
        response = Response(sheet_data.to_csv(), content_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={class_obj.title} Broadsheet.csv"
        return response
    else:
        abort(404)  # Adjust the response code according to your project's needs



@app.route('/', methods=['POST', 'GET'])
def timeline():
    page = request.args.get('page', 1, type=int)
    posts = Timeline.query.order_by(Timeline.id.desc()).paginate(page=page, per_page=5)
    picts = Gallery.query.order_by(Gallery.id.desc())
    form = PostForm()

    if request.method == "POST":
        action_type = request.form.get("name")

        if action_type == "news":
            try:
                if form.file.data:
                    file = form.file.data
                    if file and allowed_file(file.filename):
                        file_name = str(uuid.uuid1()) + "-" + secure_filename(file.filename)
                        file_path = os.path.join(app.config["FILE_FOLDER"], file_name)
                        crop_image(file.read()).save(file_path)
                        post = Timeline(content=form.content.data, file=file_name, headline=form.headline.data, admin=current_user.username)
                        store(post)
                    else:
                        flash("Invalid file type. Allowed types: {}".format(", ".join(ALLOWED_EXTENSIONS)))
                else:
                    post = Timeline(content=form.content.data, headline=form.headline.data, admin=current_user.username)
                    store(post)

                flash("Post added successfully.")

            except Exception as e:
                flash("An error occurred while adding the post: {}".format(str(e)))

            return redirect(url_for('timeline'))

        elif action_type == "gallery":
            try:
                file = form.file.data
                if file and allowed_file(file.filename):
                    file_name = str(uuid.uuid1()) + "-" + secure_filename(file.filename)
                    file_path = os.path.join(app.config["FILE_FOLDER"], file_name)
                    crop_image(file.read()).save(file_path)
                    post = Gallery(file=file_name)
                    store(post)
                    flash("Picture added successfully.")
                else:
                    flash("Invalid file type. Allowed types: {}".format(", ".join(ALLOWED_EXTENSIONS)))

            except Exception as e:
                flash("An error occurred while adding the picture: {}".format(str(e)))

            return redirect(url_for('timeline'))

    return render_template('timeline.html', posts=posts, picts=picts, form=form)



					

@app.route('/admin-login', methods=['POST', 'GET'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        admin = Admin.query.filter_by(email=email).first()

        if admin:
            if check_password_hash(admin.password, password):
                login_user(admin)
                session['account'] = 'Admin'
                flash(f"Welcome, {current_user.username}!")
                return redirect('/admin')
            else:
                flash('Incorrect password. Please try again.')
        else:
            flash('User does not exist. Please sign up.')
    return render_template('log.html', form=form)



@app.route('/login/<int:id>', methods=['POST', 'GET'])
def login(id):
    form = LoginForm()
    if form.validate_on_submit():
        user = Student.query.filter_by(session_id=id, email=form.email.data).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                session['account'] = 'Student'
                flash(f"Welcome, {current_user.first_name}!")
                return redirect('/student')
            else:
                flash('Incorrect password. Please try again.')
        else:
            flash('Email does not exist. Sign up...')
    return render_template('login.html', form=form)



@app.route('/student', methods=["POST", "GET"])
@login_required
def student():
    user_id = current_user.id
    choices.clear()
    answers.clear()

    form = EditForm()
    student = Student.query.filter_by(id=user_id).first()

    if request.method == "POST":
        action_type = request.form["name"]
        
        if action_type == "email":
            old_password_correct = check_password_hash(student.password, form.old_pass.data)
            if old_password_correct:
                student.email = form.email.data
                store(student)
                flash("Email change successful.")
            else:
                flash("Incorrect password for email change.")
        elif action_type == "password":
            old_password_correct = check_password_hash(student.password, form.old_pass.data)
            if old_password_correct:
                student.password = generate_password_hash(form.new_pass.data)
                store(student)
                flash("Password change successful.")
            else:
                flash("Incorrect old password for password change.")
    
    form.email.data = student.email
    return render_template('student.html', form=form)



@app.route('/admin', methods=["POST", "GET"])
@login_required
def admin():
    user_id = current_user.id
    form = EditForm()
    admin = Admin.query.filter_by(id=user_id).first()

    if request.method == "POST":
        action_type = request.form["name"]
        
        if action_type == "email":
            old_password_correct = check_password_hash(admin.password, form.old_pass.data)
            if old_password_correct:
                admin.email = form.email.data
                store(admin)
                flash("Email change successful.")
            else:
                flash("Incorrect password for email change.")
        elif action_type == "password":
            old_password_correct = check_password_hash(admin.password, form.old_pass.data)
            if old_password_correct:
                admin.password = generate_password_hash(form.new_pass.data)
                store(admin)
                flash("Password change successful.")
            else:
                flash("Incorrect old password for password change.")
    
    form.email.data = admin.email
    return render_template('admin.html', form=form)



@app.route('/students/<int:id>', methods=['POST', 'GET'])
@login_required
def students(id):
    form = StudentForm()
    students = Student.query.filter_by(class_id=id)
    room = Class.query.filter_by(id=id).first()

    if form.validate_on_submit():
        user = Student(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            sex=request.form['gender'],
            password=generate_password_hash(form.password.data),
            class_id=room.id,
            session_id=room.session.id
        )
        try:
            store(user)
            flash(f"{form.first_name.data} {form.last_name.data} successfully enrolled.")
            form.first_name.data = ''
            form.last_name.data = ''
            form.email.data = ''
        except Exception as e:
            flash(f"Student not added. Error: {str(e)}. Check forms and try again.")

    return render_template('students.html', students=students, room=room, form=form)




@app.route('/subject/<int:id>')
@login_required
def subject(id):
	choices.clear(), answers.clear()
	subject = Subject.query.get(id)
	return render_template('subject.html', subject=subject)



@app.route('/class/<int:id>', methods=["POST", "GET"])
@login_required
def class_(id):
    form = SubjectForm()
    room = Class.query.get(id)
    subjects = Subject.query.filter_by(class_id=room.id)
    admins = Admin.query.filter_by(type="Tutor").order_by(Admin.id)

    if request.method == "POST":
        action_type = request.form["name"]

        if action_type == "announce":
            room.announce = form.content.data
            store(room)
            flash("Announcement updated successfully.")
        elif action_type == "material":
            subject_id = request.form["sub"]
            subject = Subject.query.get(subject_id)
            if subject.file:
                try:
                    os.remove(os.path.join(app.config["FILE_FOLDER"], subject.file))
                except FileNotFoundError:
                    pass  # File might have been deleted or not exist
            name = secure_filename(form.file.data.filename)
            file_name = f"{room.title}_{name}"
            file_path = os.path.join(app.config["FILE_FOLDER"], file_name)
            
            try:
                form.file.data.save(file_path)
                subject.file = file_name
                store(subject)
                flash("Material uploaded successfully.")
            except Exception as e:
                flash(f"Failed to upload material. Error: {str(e)}")
        elif action_type == "subject":
            new_subject = Subject(title=form.title.data, class_id=id)
            store(new_subject)
            flash(f"Subject '{form.title.data}' added successfully.")
            form.title.data = ""

    form.content.data = room.announce
    return render_template('class.html', subjects=subjects, classed=room, form=form, admins=admins)



@app.route('/classes/<int:id>', methods=['POST', 'GET'])
@login_required
def classes(id):
    form = ClassForm()
    sessions = Session.query.get(id)
    admins = Admin.query.order_by(Admin.id)
    classes = Class.query.filter_by(session_id=id).order_by(Class.id)

    if request.method == "POST":
        action_type = request.form["name"]

        try:
            if action_type == "class":
                new_class = Class(title=form.title.data, session_id=sessions.id)
                store(new_class)
                flash("Class added successfully.")
                
            elif action_type == "admins":
                selected_class = Class.query.get(request.form["class"])
                selected_class.admin_id = request.form['admin']
                store(selected_class)
                flash("Admin assigned successfully.")
        
        except Exception as e:
            flash(f"An error occurred: {str(e)}")

    return render_template('classes.html', classes=classes, form=form, sess=id, admins=admins)



@app.route('/view-scores/<int:id>', methods=['POST', 'GET'])
@login_required
def view_scores(id):
    form = EditForm()
    subject = Subject.query.get(id)
    students = Student.query.filter_by(class_id=subject.room.id)
    exams = Exam.query.filter_by(subject_id=subject.id)
    tests = Test.query.filter_by(subject_id=subject.id)

    if request.method == "POST":
        action_type = request.form["name"]

        if action_type == "exam" or action_type == "test":
            student_id = request.form["student"]
            score = form.number.data

            if score is None:
                flash("Please enter a valid score.")
            else:
                score = int(score)

                if action_type == "exam":
                    existing_result = Exam.query.filter_by(subject_id=subject.id, student_id=student_id).first()
                else:  # action_type == "test"
                    existing_result = Test.query.filter_by(subject_id=subject.id, student_id=student_id).first()

                if existing_result:
                    flash(f"This student already has a {action_type.capitalize()} score for this subject.")
                else:
                    if action_type == "exam":
                        new_result = Exam(class_id=subject.room.id, score=score, student_id=student_id, subject_id=subject.id)
                    else:  # action_type == "test"
                        new_result = Test(class_id=subject.room.id, score=score, student_id=student_id, subject_id=subject.id)

                    store(new_result)
                    form.number.data = ''
                    flash(f"{action_type.capitalize()} score added successfully!")

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
    room = Class.query.get(id)

    if request.method == "POST":
        action_type = request.form["name"]
        student_id = request.form["student"]

        if action_type == "psych":
            existing_psych = Psychomotor.query.filter_by(student_id=student_id).first()
            if existing_psych:
                flash("This student is already graded for psychomotor rating.")
            else:
                new_psych = Psychomotor(
                    student_id=student_id,
                    handle=request.form["handle"],
                    draw=request.form["draw"],
                    speech=request.form["speech"],
                    write=request.form["write"],
                    public=request.form["public"],
                    sport=request.form["sport"]
                )
                if handle or draw or speech or write or public or sport == "":
                    flash("Must fill all forms!")
                else:
                    store(new_psych)
                    flash("Psychomotor grades added successfully!")

        elif action_type == "affect":
            existing_affect = Affective.query.filter_by(student_id=student_id).first()
            if existing_affect:
                flash("This student is already graded for affective rating.")
            else:
                new_affect = Affective(
                    student_id=student_id,
                    attentive=request.form["attentive"],
                    punctual=request.form["punctual"],
                    honest=request.form["honest"],
                    neat=request.form["neat"],
                    polite=request.form["polite"],
                    calm=request.form["calm"],
                    obey=request.form["obey"],
                    rely=request.form["rely"]
                )
                if attentive or punctual or honest or neat or polite or calm or obey or rely == "":
                    flash("Must fill all forms!")
                else:
                    store(new_affect)
                    flash("Affective grades added successfully!")

    return render_template("psych_affect.html", room=room, students=students)



@app.route('/contact', methods=['POST', 'GET'])
def contact():
    form = AdminForm()
    admins = Admin.query.order_by(Admin.id)

    if request.method == "POST":
        action_type = request.form["name"]

        if action_type == "add":
            new_admin = Admin(
                username=form.username.data,
                email=form.email.data,
                type=request.form["type"],
                password=generate_password_hash(form.password.data)
            )
            try:
                store(new_admin)
                flash("User added successfully!")
            except:
                flash('User not added. Check forms and try again.')

        elif action_type == "edit":
            admin_id = request.form["id"]
            edited_admin = Admin.query.get(admin_id)
            edited_admin.type = request.form["type"]
            store(edited_admin)
            flash("User updated successfully!")

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
    student = Student.query.get(id)

    if student:
        try:
            rem(student)
            flash("Student deletion successful.")
        except Exception as e:
            flash(f"An error occurred: {str(e)}")

    return redirect(url_for("students", id=num))



@app.route('/del-post/<int:id>')
@login_required
def del_post(id):
    timeline = Timeline.query.get(id)
    if timeline:
        try:
            if timeline.file:
                file_path = os.path.join(app.config["FILE_FOLDER"], timeline.file)
                if os.path.exists(file_path):
                    os.remove(file_path)
                else:
                    flash("File not found.")  
            rem(timeline)
            flash("Post deletion successful.")        
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
    return redirect('/')

	
	
@app.route('/del-class/<int:id>/<int:num>')
@login_required
def del_class(id,num):
	clas = Class.query.filter_by(id=id).first()
	rem(clas)
	return redirect(url_for("classes", id=num))



@app.route('/del-subject/<int:id>/<int:num>')
@login_required
def del_subject(id, num):
    subject = Subject.query.get(id)
    if subject:
        if subject.file:
            try:
                os.remove(os.path.join(app.config["FILE_FOLDER"], subject.file))
            except FileNotFoundError:
                flash("File not found.")
        rem(subject)
        flash("Subject deletion successful.")
    else:
        flash("Subject not found.")
    return redirect(url_for("class_", id=num))


@app.route('/del-gallery/<int:id>')
@login_required
def del_gallery(id):
    gallery = Gallery.query.get(id)
    if gallery:
        if gallery.file:
            try:
                os.remove(os.path.join(app.config["FILE_FOLDER"], gallery.file))
            except FileNotFoundError:
                flash("File not found.")
        rem(gallery)
        flash("Picture deletion successful.")
    else:
        flash("Picture not found.")
    return redirect(url_for("timeline"))



@app.route('/del-cbt/<int:id>/<int:num>')
@login_required
def del_cbt(id, num):
    cbt = CBT.query.get(id)
    if cbt:
        try:
            if cbt.file:
                file_path = os.path.join(app.config["FILE_FOLDER"], cbt.file)
                if os.path.exists(file_path):
                    os.remove(file_path)
                else:
                    flash("File not found.")      
            rem(cbt)
            flash("CBT deletion successful.")
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
    return redirect(url_for('cbt_question', id=num))

	
	
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
    subjects_per_page = 20
    try:
        page = request.args.get('page', 1, type=int)
        subjects = Subject.query.order_by(Subject.id.desc()).paginate(page=page, per_page=subjects_per_page)
        return render_template("library.html", subject=subjects)
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('timeline'))  # Redirect to a suitable page in case of an error

	