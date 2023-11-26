from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, FileField, EmailField, IntegerField
from wtforms.validators import DataRequired


class AdminForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = EmailField('Email', validators=[DataRequired()])
	password = PasswordField('Password',validators=[DataRequired()])
	submit = SubmitField('Add')

class PostForm(FlaskForm):
	headline = TextAreaField("Headline")
	content = TextAreaField('Content')
	file = FileField('Photos')
	submit = SubmitField("Post")
	
class ClassForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content')
	submit = SubmitField('Add Class')
	
class SubjectForm(FlaskForm):
	content = TextAreaField('Content')
	title = StringField('Title', validators=[DataRequired()])
	file = FileField('Upload PDF File')
	submit = SubmitField('Add Subject')
	
class StudentForm(FlaskForm):
	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	email = EmailField('Email', validators=[DataRequired()])
	password = PasswordField('Password',validators=[DataRequired()])
	submit = SubmitField('Sign up')
	
class LoginForm(FlaskForm):
	email = EmailField('Email', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Sign in')
	
class CBTForm(FlaskForm):
	question = TextAreaField('Question', validators=[DataRequired()])
	answer = StringField('Answer', validators=[DataRequired()])
	option1 = StringField('Option 1')
	option2  = StringField('Option 2')
	option3 = StringField('Option 3')
	file = FileField('Image')
	submit = SubmitField('Add')
	
class EditForm(FlaskForm):
	number = IntegerField()
	string = StringField()
	content = TextAreaField()
	file = FileField()
	old_pass = PasswordField()
	new_pass = PasswordField()
	email = EmailField()
	submit = SubmitField("Done")
	