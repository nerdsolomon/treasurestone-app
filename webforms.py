from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, FileField, EmailField, IntegerField


class LoginForm(FlaskForm):
	email = EmailField(validators=[DataRequired()])
	password = PasswordField(validators=[DataRequired()])
	submit = SubmitField('Sign in')
	
	
class PostForm(FlaskForm):
	number = IntegerField(validators=[DataRequired()])
	string = StringField(validators=[DataRequired()])
	text = TextAreaField(validators=[DataRequired()])
	file = FileField(validators=[DataRequired()])
	password = PasswordField(validators=[DataRequired()])
	old = PasswordField(validators=[DataRequired()])
	check = PasswordField(validators=[DataRequired()])
	email = EmailField(validators=[DataRequired()])
	submit = SubmitField("Done")


class StudentForm(FlaskForm):
	name = StringField(validators=[DataRequired()])
	other = StringField(validators=[DataRequired()])
	surname = StringField(validators=[DataRequired()])
	email = EmailField(validators=[DataRequired()])
	password = PasswordField(validators=[DataRequired()])
	file = FileField(validators=[DataRequired()])
	submit = SubmitField("Done")
	

class CBTForm(FlaskForm):
	question = TextAreaField(validators=[DataRequired()])
	answer = StringField(validators=[DataRequired()])
	opt_one = StringField(validators=[DataRequired()])
	opt_two  = StringField(validators=[DataRequired()])
	opt_three = StringField(validators=[DataRequired()])
	image = FileField()
	submit = SubmitField("Done")
	