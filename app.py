from flask import render_template, redirect, flash, request, session, url_for, send_from_directory # type: ignore
from models import app, db, Staff, Student, Class, Subject,Session, Active, CBT, Grade, date, load_user
from functions import broadsheet, results, process_image
from webforms import PostForm, StudentForm, CBTForm
from flask_login import login_user, logout_user, current_user, login_required # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from werkzeug.utils import secure_filename # type: ignore
from werkzeug.wrappers import Response # type: ignore
import os


def store(var):
	db.session.add(var)
	db.session.commit()

def rem(var):
    db.session.delete(var)
    db.session.commit()

@app.context_processor
def base():
    time = date.strftime('%Y')
    active = Active.query.first()
    account = session.get("account")
    if current_user.is_authenticated and account:
        if account == "Student":
            student = current_user 
            room = Class.query.filter_by(id=current_user.room.id).first()
            subjects = Subject.query.filter_by(room_id=room.id)
            return dict(student=student, account=account, subjects=subjects, time=time, active=active, room=room)
        elif account == "Staff":
            staff = Staff.query.filter_by(id=current_user.id).first()
            room = Class.query.filter_by(staff_id=current_user.id).first()
            if current_user.role == "Teacher" and room == None:
                flash("You've not been assigned a classroom")
            return dict(room=room, time=time, active=active, account=account)
    return dict(time=time, active=active)


@app.route("/", methods=['POST', 'GET'])
def homepage():
    form = PostForm()
    time = date.strftime('%Y')
    active = Active.query.first()
    students, staffs, classrooms, subjects = Student.query.count(), Staff.query.count(), Class.query.count(), Subject.query.count()
    if request.method == "POST":
        login_type = request.form["type"]
        user = Staff.query.filter_by(email=form.email.data.lower()).first() if login_type == "staff" else Student.query.filter_by(session_id=active.session.id, email=form.email.data.lower()).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                login_user(user)
                session["account"] = "Staff" if login_type == "staff" else "Student"
                load_user(user.id)
                return redirect("/dashboard")
            else:
                flash("Incorrect password. Try again...")
        else:
            flash("User does not exist.")
    return render_template("homepage.html", student_num=students, staff_num=staffs, subject_num=subjects, class_num=classrooms, time=time, form=form)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect('/')

 
@app.route('/download/<path:filename>')
@login_required
def download(filename):
    try:
        return send_from_directory(app.config['FILE_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        os.abort(404)


@app.route('/save_sheet/<int:active>/<int:id>')
@login_required
def save_sheet(active, id):
    class_obj = Class.query.get(id)
    sheet_data = broadsheet(active, id)
    response = Response(sheet_data.to_csv(), content_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={class_obj.title} BROADSHEET.csv"
    return response
        

@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    form = PostForm()
    id = current_user.id
    staff = Staff.query.filter_by(id=id).first()
    if request.method == "POST":
        if check_password_hash(staff.password, form.old.data):
            if form.password.data == form.check.data:
                staff.password = form.password.data
                store(staff)
                flash("Password change successful")
            else:
                flash("New password don't match")
        else:
            flash("Old password is incorrect")        
    return render_template("dashboard.html", form=form)

 
@app.route('/subject/<int:id>')
@login_required
def subject(id):
    choices.clear(), answers.clear()
    subject = Subject.query.get(id)
    grade = Grade.query.filter_by(subject_id=id, student_id=current_user.id).first()
    return render_template('subject.html', subject=subject, grade=grade)
	

choices, answers = [], []
 
@app.route("/cbt/<int:id>/<type>", methods=['POST', 'GET'])
@login_required
def cbt(id, type):
    ROWS_PER_PAGE = 1
    page = request.args.get('page', 1, type=int)
    cbts = CBT.query.filter_by(subject_id=id, type=type).paginate(page=page, per_page=ROWS_PER_PAGE)
    if request.method == "POST":
        try:
            for cbt in cbts.items:
                choices.append(request.form["option"])
                answers.append(cbt.answer)   
            if cbts.page == cbts.pages:
                score = sum(choice == answer for choice, answer in zip(choices, answers))
                record = Grade(exam=score, student_id=current_user.id, subject_id=id) if type == "Exam" else Grade(test=score, student_id=current_user.id, subject_id=id)
                store(record)
                return render_template('score.html', score=score, cbts=cbts)
            return redirect(url_for('cbt', id=id, type=type, page=cbts.next_num))
        except KeyError:
            flash('You must make a choice to continue.')
            return redirect(url_for('cbt', id=id, type=type, page=cbts.page))
    return render_template('cbt.html', id=id, type=type,cbts=cbts)


@app.route('/subject/questions/<int:id>', methods=["POST", "GET"])
@login_required
def subject_questions(id):
    form = CBTForm()
    subject = Subject.query.filter_by(id=id).first()
    page = request.args.get('page', 1, type=int)
    cbts = CBT.query.filter_by(subject_id=id).order_by(-CBT.id.desc()).paginate(page=page, per_page=10)
    if request.method == "POST":
        form_type = request.form["name"]
        if form_type == "setQ":     
            cbt = CBT(question=form.question.data, answer=form.answer.data, opt_one=form.opt_one.data, opt_two=form.opt_two.data, opt_three=form.opt_three.data, type=form.type.data, subject_id=id)
        elif form_type == "edit":
            cbt = CBT.query.filter_by(id=request.form["qst"]).first()
            cbt.question, cbt.answer, cbt.opt_one, cbt.opt_two, cbt.opt_three, cbt.type = form.question.data, form.answer.data, form.opt_one.data, form.opt_two.data, form.opt_three.data, form.type.data
        store(cbt)
        return redirect(url_for('subject_questions', id=id))
    return render_template('subject_questions.html', cbts=cbts, form=form, subject=subject)


@app.route("/sessions", methods=['POST', 'GET'])
@login_required
def sessions():
	form = PostForm()
	active = Active.query.first()
	sessions = Session.query.order_by(-Session.id)
	if request.method == "POST":
		if form.name.data == "active":
			if active:
				active.session_id = request.form["session"]
			else:
				active = Active(session_id=request.form["session"])
				db.session.add(active)
			db.session.commit()
			flash("Session activated")
		elif form.name.data == "session":
			new_session = Session(session=form.string.data, term=request.form["term"])
			store(new_session)
	return render_template("sessions.html", sessions=sessions, form=form, active=active)


@app.route('/classes', methods=['POST', 'GET'])
@login_required
def classes():
    form = PostForm()
    staff = Staff.query.filter_by(role="Teacher").order_by(Staff.id)
    classes = Class.query.order_by(Class.id)
    if request.method == "POST":
        if form.name.data == "class":
            new_class = Class(title=form.string.data.upper())
            store(new_class)
        elif form.name.data == "staff":
            selected_class = Class.query.get(request.form["room"])
            selected_class.staff_id = request.form["staff"]
            store(selected_class)
        elif form.name.data == "edit":
            selected_class = Class.query.get(request.form["room"])
            selected_class.title = form.string.data.upper()
            store(selected_class)
    return render_template('classes.html', classes=classes, form=form, staffs=staff)



@app.route("/staffs", methods=['POST', 'GET'])
@login_required
def staffs():
    form = PostForm()
    staffs = Staff.query.order_by(-Staff.id)
    if request.method == "POST":
        if form.name.data == "add":
            new_staff = Staff(name=form.string.data, email=form.email.data, role=request.form["role"], password=generate_password_hash(form.password.data))
            store(new_staff) 
        elif form.name.data == "edit":
            staff = Staff.query.filter_by(id=request.form["staff"]).first()
            staff.name = form.string.data
            staff.email = form.email.data
            staff.role = request.form["role"]
            store(staff)
        return redirect(url_for('staffs'))
    return render_template("staffs.html", form=form, staffs=staffs)
    

@app.route('/classroom/<int:id>', methods=["POST", "GET"])
@login_required
def classroom(id):
    form = PostForm()
    subjects = Subject.query.filter_by(room_id=id).order_by(-Subject.id)
    if request.method == "POST":
        if form.name.data == "subject":
            new_subject = Subject(title=form.string.data.upper(), room_id=id)
            store(new_subject)
            form.string.data = ""
        elif form.name.data == "material":
            subject = Subject.query.filter_by(id=request.form["subject"]).first()
            if subject.file:
                os.remove(os.path.join(app.config["FILE_FOLDER"], subject.file))
            file = form.file.data
            file_name = subject.room.title + "_" + secure_filename(file.filename)
            file.save(os.path.join(app.config["FILE_FOLDER"], file_name))
            subject.file = file_name
            store(subject)  
        elif form.name.data == "sub":
            subject = Subject.query.filter_by(id=request.form["subject"]).first()
            subject.title = form.string.data.upper()
            store(subject)
    return render_template('classroom.html', subjects=subjects, form=form)


@app.route("/students/<int:active>/<int:id>", methods=['POST', 'GET'])
@login_required
def students(active, id):
    form = StudentForm()
    students = Student.query.filter_by(session_id=active, room_id=id).order_by(-Student.id)
    if request.method == "POST":
        form_type = request.form["named"]
        if form_type == "add":
            new_student = Student(
            name=form.name.data.capitalize(),
            other=form.other.data.capitalize(),
            surname=form.surname.data.capitalize(),
            email=f"{form.name.data.lower()}{form.surname.data.lower()}@tsaps.edu",
            sex=form.sex.data,
            image=process_image(form.file.data) if form.file.data and process_image(form.file.data) else flash("Invalid image type. Allowed types: .png, .jpg, .jpeg"),
            password=generate_password_hash(form.password.data),
            room_id=id,
            session_id=active
            )
            store(new_student)   
        elif form_type == "edit":
            student = Student.query.filter_by(id=request.form["student"]).first()
            student.name = form.name.data
            student.other = form.other.data
            student.surname = form.surname.data
            student.sex = form.sex.data
            student.remark = form.remark.data
            student.email = f"{form.name.data.lower()}{form.surname.data.lower()}@tsaps.edu"
            store(student)
    return render_template("students.html", students=students, form=form)


@app.route('/result/<int:id>', methods=['POST', 'GET'])
@login_required
def result(id):
    choices.clear(), answers.clear()
    sheet = results(id)
    return render_template("result.html", tables=[sheet.to_html(justify="left",classes="table table-hover table-bordered")])


@app.route("/broadsheet/<int:active>/<int:id>", methods=['POST', 'GET'])
@login_required
def broadsheets(active, id):
	sheet = broadsheet(active, id)			
	return render_template("broadsheet.html", tables=[sheet.to_html(classes="table table-hover table-bordered")])
		

@app.route('/view-scores/<int:id>', methods=['POST', 'GET'])
@login_required
def view_scores(id):
    form = PostForm()
    subject = Subject.query.filter_by(id=id).first()
    students = Student.query.filter_by(room_id=subject.room.id)
    grades = Grade.query.filter_by(subject_id=subject.id)
    if request.method == "POST":
        student = request.form["student"]
        result = Grade.query.filter_by(subject_id=id, student_id=student).first()
        if result:
            if form.name.data == "exam":
                result.exam = form.number.data
                store(result)
            else:
                result.test = form.number.data
                store(result)
        else:
            result = Grade(exam=form.number.data, student_id=student, subject_id=id) if form.name.data == "exam" else Grade(test=form.number.data, student_id=student, subject_id=id)
            store(result)
    form.number.data = ""
    return render_template("view_scores.html", form=form, students=students, subject=subject, grades=grades)
		
		
@app.route('/student/delete/<int:id>/<int:num>/<int:active>')
@login_required
def student_delete(id, num, active):
    student = Student.query.get(id)
    if student.image:
        try:
            os.remove(os.path.join(app.config["FILE_FOLDER"], student.image))
        except FileNotFoundError:
            flash("File not found.")
    rem(student)
    return redirect(url_for("students", id=num, active=active))

@app.route('/subject/delete/<int:id>/<int:num>')
@login_required
def subject_delete(id, num):
    subject = Subject.query.get(id)
    if subject.file:
        try:
            os.remove(os.path.join(app.config["FILE_FOLDER"], subject.file))
        except FileNotFoundError:
            flash("File not found.")
    rem(subject)
    return redirect(url_for("classroom", id=num))

@app.route('/classroom/delete/<int:id>')
@login_required
def class_delete(id):
    room = Class.query.filter_by(id=id).first()
    rem(room)
    return redirect(url_for("classes"))

@app.route('/staff/delete/<int:id>')
@login_required
def staff_delete(id):
    staff = Staff.query.filter_by(id=id).first()
    rem(staff)
    return redirect('/staffs')

@app.route('/question/delete/<int:id>/<int:num>')
@login_required
def question_delete(id, num):
    cbt = CBT.query.get(id)
    rem(cbt)
    return redirect(url_for('subject_questions', id=num))