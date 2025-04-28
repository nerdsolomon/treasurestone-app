from models import Student, Grade, db, app
import pandas as pd # type: ignore
from PIL import Image # type: ignore
import io
import os
import uuid as uuid

def broadsheet(active, id):
    student_data = Student.query.filter_by(session_id=active, room_id=id).order_by(Student.id).all()
    student_info = db.session.query(Student, Grade).join(Grade, Student.id == Grade.student_id).order_by(Student.id)
    columns = ["Student", "SUBJECTS", "Exam", "Test", "Total"]
    df = pd.DataFrame(columns=columns)
    
    for x, student in zip(range(student_info.count()), student_info):
        df.loc[x, ["Student"]] = f"{student[0].name}  {student[0].other}  {student[0].surname}"
        df.loc[x, ["SUBJECTS"]] = student[1].subject.title
        df.loc[x, ["Exam"]] = student[1].exam
        df.loc[x, ["Test"]] = student[1].test
        df.loc[x, ["Total"]] = student[1].exam + student[1].test

    new = df.pivot(index="Student", columns= "SUBJECTS", values=["Test", "Exam", "Total"])
    new["Grand Total"] = df.groupby("Student")[["Test", "Exam"]].sum().sum(axis=1)
    new["Average"] = new["Grand Total"] / student_info.count()
    new["Remark"] = [i.remark for i in student_data]
    new.index.name = None
    broadsheet = new.swaplevel(1, 0, axis=1).sort_index(axis=1)
    return broadsheet

def results(id):
    try:
        grades = Grade.query.filter_by(student_id=id).all()
        content = {"Subject": [i.subject.title for i in grades], "Exam": [i.exam for i in grades], "Test": [i.test for i in grades]}
        result = pd.DataFrame(content)
        result["Total"] = result["Exam"].fillna(0) + result["Test"].fillna(0)
        result["Grade"] = pd.cut(result["Total"], bins=[0, 40, 45, 50, 60, 70, float('inf')], labels=['F', 'E', 'D', 'C', 'B', 'A'])
        return result   
    except:
        return pd.DataFrame()

def crop_image(img):
    image = Image.open(io.BytesIO(img))
    width, height = image.size
    if width == height:
        return image
    offset  = int(abs(height-width)/2)
    image = image.crop([offset,0,width-offset,height]) if width > height else image.crop([0,offset,width,height-offset])
    return image
           
def process_image(file):
    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'bmp'}:
        file_name = f"{uuid.uuid1()}{file.filename}"
        image = crop_image(file.read())
        image.save(os.path.join(app.config["FILE_FOLDER"], file_name))
        return file_name