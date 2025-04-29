from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, FileField, EmailField, FloatField


class PostForm(FlaskForm):
	name = StringField(validators=[DataRequired()])
	number = FloatField(validators=[DataRequired()])
	string = StringField(validators=[DataRequired()])
	text = TextAreaField(validators=[DataRequired()])
	file = FileField()
	password = PasswordField(validators=[DataRequired()])
	old = PasswordField(validators=[DataRequired()])
	check = PasswordField(validators=[DataRequired()])
	email = EmailField(validators=[DataRequired()])
	submit = SubmitField("Done")


class StudentForm(FlaskForm):
	name = StringField(validators=[DataRequired()])
	other = StringField(validators=[DataRequired()])
	surname = StringField(validators=[DataRequired()])
	sex = StringField(validators=[DataRequired()])
	email = EmailField(validators=[DataRequired()])
	password = PasswordField(validators=[DataRequired()])
	file = FileField()
	remark = TextAreaField()
	submit = SubmitField("Done")
	

class CBTForm(FlaskForm):
	question = TextAreaField(validators=[DataRequired()])
	answer = StringField(validators=[DataRequired()])
	opt_one = StringField(validators=[DataRequired()])
	opt_two  = StringField(validators=[DataRequired()])
	opt_three = StringField(validators=[DataRequired()])
	type = StringField(validators=[DataRequired()])
	submit = SubmitField("Done")
	