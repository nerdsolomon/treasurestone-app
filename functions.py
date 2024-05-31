from models import Student, Exam, Test, db, Psychomotor, Affective
import pandas as pd
from PIL import Image
import io


def broadsheet(active, id):
    student_data = Student.query.filter_by(session_id=active, room_id=id).order_by(Student.id).all()
    student_info = db.session.query(Student, Exam, Test)\
    .join(Exam, Student.id == Exam.student_id)\
    .join(Test, Student.id == Test.student_id)\
    .order_by(Student.id)\
    .filter(Exam.subject_id == Test.subject_id).all()
    
    columns = ["Student", "Subject", "Exam", "Test", "Total"]
    df = pd.DataFrame(columns=columns)
    
    for x, student in zip(range(len(student_info)), student_info):
        df.loc[x, ["Student"]] = student[0].name + " " + student[0].other + " " + student[0].surname
        df.loc[x, ["Subject"]] = student[1].subject.title
        df.loc[x, ["Exam"]] = student[1].score
        df.loc[x, ["Test"]] = student[2].score
        df.loc[x, ["Total"]] = student[1].score + student[2].score

    new = df.pivot(index="Student", columns= "Subject", values=["Test", "Exam", "Total"])
    new["Added Total"] = df.groupby("Student")[["Test", "Exam"]].sum().sum(axis=1)
    new["Average"] = new["Added Total"] / len(student_info)
    new["Remark"] = [i.remark for i in student_data]
    new.index.name = None
    broadsheet = new.swaplevel(1, 0, axis=1)
    return broadsheet



def results(id):
    try:
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
        
        result["Grade"] = pd.cut(result["Score"], bins=[0, 40, 45, 50, 60, 70, float('inf')], labels=['F', 'E', 'D', 'C', 'B', 'A'])
        return result
        
    except:
        blank = pd.DataFrame()
        return blank



def affect(id):
    affective = Affective.query.filter_by(student_id=id).first()
    if affective:
        data = {"AFFECTIVE DOMAIN": ["Attentiveness", "Honesty", "Neatness", "Politeness", "Punctuality/Assembly", "Self-Control/Calmness", "Obedience", "Reliability"], "RATING": [affective.attentive, affective.honest, affective.neat, affective.polite, affective.punctual, affective.calm, affective.obey, affective.rely]}
        frame = pd.DataFrame(data)
        return frame
    else:
        return pd.DataFrame()



def psycho(id):
    psych = Psychomotor.query.filter_by(student_id=id).first()
    if psych:
        data = {"PSYCHOMOTOR DOMAIN": ["Handling Of Tools", "Drawing And Painting", "Handwriting", "Speech Fluency", "Sport And Games", "Public Speaking"], "RATING": [psych.handle, psych.draw, psych.write, psych.speech, psych.sport, psych.public]}
        frame = pd.DataFrame(data)
        return frame
    else:
        return pd.DataFrame()



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



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS