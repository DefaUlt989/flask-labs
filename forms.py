from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import SubmitField, StringField, FileField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email


class Calculator(FlaskForm):
    obj_1 = IntegerField('Obj 1', validators=[InputRequired()])
    operand = SelectField('Operation', choices=[('+', '+'), ('-', '-'), ('*', '*'), ('/', '/')])
    obj_2 = IntegerField('Obj 2', validators=[InputRequired()])
    submit = SubmitField('Calculate')


class BlogForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[InputRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Publish')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Register')

class EditBlogForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[InputRequired()])
    submit = SubmitField('Update')