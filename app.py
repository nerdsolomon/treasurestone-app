from flask import render_template, redirect, flash, request, session, url_for, send_from_directory
from models import app, db, Staff, Student, Class, Subject,Session, Active, CBT, Exam, Test, Slide, date, Psychomotor, Affective
from functions import broadsheet, results, crop_image, allowed_file, ALLOWED_EXTENSIONS, affect, psycho
from webforms import PostForm, StudentForm, CBTForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from werkzeug.wrappers import Response
from werkzeug.security import generate_password_hash, check_password_hash
import calendar
#from google.cloud import storage

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "student_login"
login_manager.login_view = "staff_login"

@login_manager.user_loader
def load_user(id):
	if session['account'] == "Staff":
		return Staff.query.get(int(id))
	elif session['account'] == 'Student':
		return Student.query.get(int(id))
	else:
		return None


FILE_FOLDER = "static/storage"
if not os.path.exists(FILE_FOLDER):
	os.makedirs(FILE_FOLDER)
app.config["FILE_FOLDER"] = FILE_FOLDER

#client = storage.Client()
#bucket_name = "hdrive-bucket-name"
#bucket = client.get_bucket(bucket_name)


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
            return dict(student=student, account=account, subjects=subjects, time=time, active=active)
        elif account == "Staff":
            staff = Staff.query.filter_by(id=current_user.id).first()
            room = Class.query.filter_by(staff_id=current_user.id).first()
            if current_user.role == "Teacher" and room == None:
            	flash("You've not been assigned a classroom")
            	return dict(time=time, active=active)
            return dict(room=room, account=account, staff=staff, time=time, active=active)
    return dict(time=time, active=active)
    


@app.route("/")
def homepage():
	choices.clear(), answers.clear()
	slides = Slide.query.order_by(Slide.id.desc())
	year, month = int(date.strftime('%Y')), int(date.strftime('%m'))
	today, current = int(date.strftime('%d')), date.strftime('%B, %Y')
	students, staffs = Student.query.count(), Staff.query.count()
	classrooms, subjects = Class.query.count(), Subject.query.count()
	return render_template("homepage.html", slides=slides, year=year, today=today,month=month, calendar=calendar, current=current, student_num=students, staff_num=staffs, subject_num=subjects, class_num=classrooms)

 
 
@app.route('/download/<path:filename>')
@login_required
def download(filename):
    file = filename
    try:
        return send_from_directory(app.config['FILE_FOLDER'], file, as_attachment=True)
    except FileNotFoundError:
        abort(404)


#@app.route('/download/<path:filename>')
#@login_required
#def download(filename):
#    file = filename
#    try:
#        blob = bucket.get_blob(file)
#        file_data = blob.download_as_string()
#        return send_from_directory(BytesIO(file_data), file, as_attachment=True)
#    except FileNotFoundError:
#        abort(404)



@app.route('/save_sheet/<int:active>/<int:id>')
@login_required
def save_sheet(active, id):
    class_obj = Class.query.get(id)
    if class_obj:
        sheet_data = broadsheet(active, id)
        response = Response(sheet_data.to_csv(), content_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={class_obj.title} BROADSHEET.csv"
        return response
    else:
        abort(404)
        
        
        
@app.route('/staff/login', methods=['POST', 'GET'])
def staff_login():
    form = PostForm()
    if request.method == "POST":
        staff = Staff.query.filter_by(email=form.email.data.lower()).first()
        if staff:
            if check_password_hash(staff.password,form.password.data):
                login_user(staff)
                session['account'] = "Staff"
                flash(f"Welcome, {current_user.name}!")
                return redirect("/")
            else:
                flash('Incorrect password. Please try again.')
        else:
            flash('User does not exist.')
    return render_template('staff_login.html', form=form)
 
 
 
@app.route('/student/login/<int:active>', methods=['POST', 'GET'])
def student_login(active):
    form = PostForm()
    if request.method == "POST":
        user = Student.query.filter_by(session_id=active, email=form.email.data.lower()).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                session['account'] = "Student"
                flash(f"Welcome, {current_user.name}!")
                return redirect("/")
            else:
                flash('Incorrect password. Please try again.')
        else:
            flash('User does not exist.')
    return render_template('student_login.html', form=form)

 
 
@app.route('/subject/<int:id>')
@login_required
def subject(id):
	choices.clear(), answers.clear()
	subject = Subject.query.get(id)
	return render_template('subject.html', subject=subject)
	
	

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash("You're logged out.")
	return redirect('/')



choices, answers = [], []
 
@app.route("/cbt/<int:id>/<type>", methods=['POST', 'GET'])
@login_required
def cbt(id, type):
    record = Exam.query.filter_by(subject_id=id, student_id=current_user.id).all() if type == "Exam" else Test.query.filter_by(subject_id=id, student_id=current_user.id).all()
    if record:
        flash("Assessment already taken.")
        return redirect(url_for('subject', id=id)) 
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
                record = Exam(score=score, student_id=current_user.id, subject_id=id) if type == "Exam" else Test(score=score, student_id=current_user.id, subject_id=id)
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
    questions_per_page = 20
    try:
    	page = request.args.get('page', 1, type=int)
    	cbts = CBT.query.filter_by(subject_id=id).order_by(CBT.id.desc()).paginate(page=page, per_page=questions_per_page)
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for("/"))

    if request.method == "POST":
    	form_type = request.form["name"]
    	if form_type == "setQ":
    		if form.image.data:
    			file = form.image.data
    			if file and allowed_file(file.filename):
    				file_name = str(uuid.uuid1()) + ".jpg"
    				image = crop_image(file.read())
                    #blob = bucket.blob(file_name)
                    #blob.upload_from_string(image.read(), content_type=file.content_type)
                    #blob.make_public()
    				image.save(os.path.join(app.config["FILE_FOLDER"], file_name))
    				cbt = CBT(question=form.question.data, answer=form.answer.data, opt_one=form.opt_one.data, opt_two=form.opt_two.data, opt_three=form.opt_three.data, image=file_name, type=form.type.data, subject_id=id)
    				store(cbt)
    			else:
    				flash("Invalid file type. Allowed types: {}".format(", ".join(ALLOWED_EXTENSIONS)))
    		else:
    			cbt = CBT(question=form.question.data, answer=form.answer.data, opt_one=form.opt_one.data, opt_two=form.opt_two.data, opt_three=form.opt_three.data, type=form.type.data, subject_id=id)
    			store(cbt)
    		flash("Question added.")
    		return redirect(url_for('subject_questions', id=id))
    	
    	elif form_type == "edit":
    		cbt = CBT.query.filter_by(id=request.form["qst"]).first()
    		cbt.question, cbt.answer, cbt.opt_one, cbt.opt_two, cbt.opt_three, cbt.type = form.question.data, form.answer.data, form.opt_one.data, form.opt_two.data, form.opt_three.data, form.type.data
    		store(cbt)
    		flash("Question Edited")
    		return redirect(url_for('subject_questions', id=id))	
    return render_template('subject_questions.html', cbts=cbts, form=form, subject=subject)



@app.route("/operation", methods=['POST', 'GET'])
@login_required
def operation():
	form = PostForm()
	slides = Slide.query.order_by(Slide.id.desc())
	active = Active.query.first()
	sessions = Session.query.order_by(-Session.id)
	
	if request.method == "POST":
		form_type = form.name.data
		if form_type == "slide":
			file = form.file.data
			if file and allowed_file(file.filename):
				file_name = str(uuid.uuid1()) + ".jpg"
				image = crop_image(file.read())
                #blob = bucket.blob(file_name)
                #blob.upload_from_string(image.read(), content_type=file.content_type)
                #blob.make_public()
				image.save(os.path.join(app.config["FILE_FOLDER"], file_name))
				images = Slide(image=file_name)
				store(images)
				flash("Image added.")
			else:
				flash("Invalid file type. Allowed types: {}".format(", ".join(ALLOWED_EXTENSIONS)))
				
		elif form_type == "active":
			if active:
				active.session_id = request.form["session"]
			else:
				active = Active(session_id=request.form["session"])
				db.session.add(active)
			db.session.commit()
			flash("Session activated")
		
		elif form_type == "session":
			new_session = Session(session=form.string.data, term=request.form["term"])
			db.session.add(new_session)
			db.session.commit()
			flash("Session added.")
			
	return render_template("operation.html", sessions=sessions,slides=slides, form=form)



@app.route('/classes', methods=['POST', 'GET'])
@login_required
def classes():
    form = PostForm()
    staff = Staff.query.filter_by(role="Teacher").order_by(Staff.id)
    classes = Class.query.order_by(Class.id)

    if request.method == "POST":
        action_type = form.name.data
        if action_type == "class":
            new_class = Class(title=form.string.data.upper())
            store(new_class)
        elif action_type == "staff":
            selected_class = Class.query.get(request.form["room"])
            selected_class.staff_id = request.form["staff"]
            store(selected_class)
            flash("Teacher assigned.")
        elif action_type == "edit":
            selected_class = Class.query.get(request.form["room"])
            selected_class.title = form.string.data.upper()
            store(selected_class)
    return render_template('classes.html', classes=classes, form=form, staffs=staff)



@app.route("/staffs", methods=['POST', 'GET'])
@login_required
def staffs():
    form = PostForm()
    staffs = Staff.query.order_by(Staff.id)
    if request.method == "POST":
        form_type = form.name.data
        if form_type == "add":
            new_staff = Staff(name=form.string.data, email=form.email.data, role=request.form["role"], password=generate_password_hash(form.password.data))
            store(new_staff)
            flash("Staff added")
            
        elif form_type == "edit":
            staff = Staff.query.filter_by(id=request.form["staff"]).first()
            staff.name = form.string.data
            staff.email = form.email.data
            staff.role = request.form["role"]
            store(staff)
        return redirect(url_for('staffs'))
    return render_template("staffs.html", form=form, staffs=staffs)
    


@app.route("/staff/edit/<int:id>", methods=['POST', 'GET'])
@login_required
def staff_edit(id):
    form = PostForm()
    staff = Staff.query.filter_by(id=id).first()

    if request.method == "POST":
        action_type = form.name.data
        if action_type == "profile":
            if check_password_hash(staff.password, form.password.data):
                staff.name = form.string.data
                staff.email = form.email.data
                store(staff)
                flash("Profile editted")
            else:
                flash("Password incorrect")
        elif action_type == "password":
            if check_password_hash(staff.password, form.old.data):
                if form.password.data == form.check.data:
                    staff.password = generate_password_hash(form.password.data)
                    store(staff)
                    flash("Password updated")
                else:
                    flash("Passwords don't match")
            else:
                flash("Old password is incorrect")
    form.string.data = staff.name
    form.email.data = staff.email             
    return render_template("edit_staff.html", form=form)
    
    
    
@app.route('/classroom/<int:id>', methods=["POST", "GET"])
@login_required
def classroom(id):
    form = PostForm()
    subjects = Subject.query.filter_by(room_id=id)

    if request.method == "POST":
        action_type = form.name.data

        if action_type == "subject":
            new_subject = Subject(title=form.string.data.upper(), room_id=id)
            store(new_subject)
            flash(f"{form.string.data} added.")
            form.string.data = ""
            
        elif action_type == "material":
            subject = Subject.query.filter_by(id=request.form["subject"]).first()
            if subject.file:
                os.remove(os.path.join(app.config["FILE_FOLDER"], subject.file))
            file = form.file.data
            file_name = subject.room.title + "-" + secure_filename(file.filename)
            #blob = bucket.blob(file_name)
            #blob.upload_from_string(file.read(), content_type=file.content_type)
            #blob.make_public()
            file.save(os.path.join(app.config["FILE_FOLDER"], file_name))
            subject.file = file_name
            store(subject)
            flash(f"File added for {subject.title}")
            
        elif action_type == "sub":
            subject = Subject.query.filter_by(id=request.form["subject"]).first()
            subject.title = form.string.data.upper()
            store(subject)

    return render_template('classroom.html', subjects=subjects, form=form)



@app.route("/students/<int:active>/<int:id>", methods=['POST', 'GET'])
@login_required
def students(active, id):
    form = StudentForm()
    students = Student.query.filter_by(session_id=active, room_id=id)

    if request.method == "POST":
        form_type = request.form["named"]
        
        if form_type == "add":
            file = form.file.data
            if file and allowed_file(file.filename):
                file_name = str(uuid.uuid1()) + ".jpg"
                image = crop_image(file.read())
                #blob = bucket.blob(file_name)
                #blob.upload_from_string(image.read(), content_type=file.content_type)
                #blob.make_public()
                image.save(os.path.join(app.config["FILE_FOLDER"], file_name))
                
                new_student = Student(
                name=form.name.data.capitalize(),
                other=form.other.data.capitalize(),
                surname=form.surname.data.capitalize(),
                email=f"{form.name.data.lower()}{form.surname.data.lower()}@tsaps.edu",
                sex=form.sex.data,
                image=file_name,
                password=generate_password_hash(form.password.data),
                room_id=id,
                session_id=active
                )
                store(new_student)
                flash(f"{form.surname.data} added")
            else:
                flash("Invalid file type. Allowed types: {}".format(", ".join(ALLOWED_EXTENSIONS)))
                
        elif form_type == "edit":
            student = Student.query.filter_by(id=request.form["student"]).first()
            student.name = form.name.data
            student.other = form.other.data
            student.surname = form.surname.data
            student.sex = form.sex.data
            student.email = f"{form.name.data.lower()}{form.surname.data.lower()}@tsaps.edu"
            store(student)
    return render_template("students.html", students=students, form=form)



@app.route("/broadsheet/<int:active>/<int:id>", methods=['POST', 'GET'])
@login_required
def broadsheets(active, id):
	try:
		form = PostForm()
		students = Student.query.filter_by(session_id=active, room_id=id)
		sheet = broadsheet(active, id)
		if request.method == "POST":
				try:
					student_id = request.form["student"]
					student = Student.query.filter_by(id=student_id).first()
					student.remark = form.text.data
					if not student_id or not form.text.data:
						flash("You must fill all forms")
					else:
						store(student)
				except KeyError:
					flash("Invalid form submission")			
		return render_template("broadsheet.html", tables=[sheet.to_html(classes="table table-hover table-sm table-bordered")], students=students, form=form)
	except:
		flash("All Student must have a score for every subject.")
		return redirect("/")
		


@app.route('/view-scores/<int:id>', methods=['POST', 'GET'])
@login_required
def view_scores(id):
    form = PostForm()
    subject = Subject.query.filter_by(id=id).first()
    students = Student.query.filter_by(room_id=subject.room.id)
    exams = Exam.query.filter_by(subject_id=subject.id)
    tests = Test.query.filter_by(subject_id=subject.id)
    
    if request.method == "POST":
        action_type = form.name.data
        student = request.form["student"]
        score = int(form.number.data)
        
        if action_type == "exam":
            existing_result = Exam.query.filter_by(subject_id=id, student_id=student).first()
            if existing_result:
                existing_result.score = score
                store(existing_result)
            else:
                new_result = Exam(score=score, student_id=student, subject_id=id)
                store(new_result)
        else:
            existing_result = Test.query.filter_by(subject_id=id, student_id=student).first()
            if existing_result:
                existing_result.score = score
                store(existing_result)
            else:
                new_result = Test(score=score, student_id=student, subject_id=id)
                store(new_result)

    form.number.data = ' '
    return render_template("view_scores.html", form=form, students=students, subject=subject, tests=tests, exams=exams)
     


@app.route('/slide/delete/<int:id>')
@login_required
def slide_delete(id):
    slide = Slide.query.get(id)
    if slide:
        if slide.image:
            try:
                os.remove(os.path.join(app.config["FILE_FOLDER"], slide.image))
            except FileNotFoundError:
                flash("File not found.")
        db.session.delete(slide)
        db.session.commit()
        flash("Picture deleted.")
    else:
        flash("Picture not found.")
    return redirect(url_for("operation"))



@app.route('/result/<int:id>', methods=['POST', 'GET'])
@login_required
def result(id):
    choices.clear(), answers.clear()
	try:
	   sheet, psych, affective = results(id), psycho(id), affect(id)
	   return render_template("result.html", tables=[sheet.to_html(justify="left",classes="table table-hover table-sm table-bordered")], psych=[psych.to_html(justify="left",classes="table table-hover table-sm table-bordered")], affective=[affective.to_html(justify="left",classes="table table-hover table-sm table-bordered")])
	except:
		flash("Final result not ready.")
		return redirect(url_for("student", id=id))
		
		
		
@app.route('/student/delete/<int:id>/<int:num>/<int:active>')
@login_required
def student_delete(id, num, active):
    student = Student.query.get(id)
    if student:
        if student.image:
            try:
                os.remove(os.path.join(app.config["FILE_FOLDER"], student.image))
            except FileNotFoundError:
                flash("File not found.")
        rem(student)
        flash("Student deleted.")
    else:
        flash("Student not found.")
    return redirect(url_for("students", id=num, active=active))



@app.route('/subject/delete/<int:id>/<int:num>')
@login_required
def subject_delete(id, num):
    subject = Subject.query.get(id)
    if subject:
        if subject.file:
            try:
                os.remove(os.path.join(app.config["FILE_FOLDER"], subject.file))
            except FileNotFoundError:
                flash("File not found.")
        rem(subject)
        flash("Subject deleted.")
    else:
        flash("Subject not found.")
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
    if cbt:
        try:
            if cbt.image:
                file_path = os.path.join(app.config["FILE_FOLDER"], cbt.image)
                if os.path.exists(file_path):
                    os.remove(file_path)
                else:
                    flash("Image not found.")      
            rem(cbt)
            flash("Question deleted.")
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
    return redirect(url_for('subject_questions', id=num))
    
    

@app.route('/psych-affect/<int:active>/<int:id>', methods=['POST', 'GET'])
@login_required
def psych_affect(id, active):
    students = Student.query.filter_by(room_id=id, session_id=active)
    
    if request.method == "POST":
        action_type = request.form["name"]
        student_id = request.form["student"]

        if action_type == "psych":
            existing_psych = Psychomotor.query.filter_by(student_id=student_id).first()
            if existing_psych:
                flash("This student is already graded for psychomotor rating.")
            else:
                new_psych = Psychomotor(student_id=student_id,
                    handle=request.form["handle"], draw=request.form["draw"],
                    speech=request.form["speech"], write=request.form["write"],
                    public=request.form["public"], sport=request.form["sport"]
                )
                store(new_psych)
                flash("Psychomotor graded")

        elif action_type == "affect":
            existing_affect = Affective.query.filter_by(student_id=student_id).first()
            if existing_affect:
                flash("This student is already graded for affective rating.")
            else:
                new_affect = Affective(student_id=student_id,
                    attentive=request.form["attentive"], punctual=request.form["punctual"],
                    honest=request.form["honest"], neat=request.form["neat"],
                    polite=request.form["polite"], calm=request.form["calm"],
                    obey=request.form["obey"], rely=request.form["rely"]
                )
                store(new_affect)
                flash("Affective graded")
    return render_template("psych_affect.html",students=students)

