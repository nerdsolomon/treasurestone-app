import pandas as pd
from models import Exam, Test, Student, Affective,  Psychomotor

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
