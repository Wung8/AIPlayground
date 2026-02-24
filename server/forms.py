from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp

from server.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Regexp(r'^[A-Za-z0-9_]{3,20}$',message="Username must be 3-20 characters and contain only letters, numbers, or underscores.")])
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UploadAgentForm(FlaskForm):
    agent_file = FileField('Upload Agent',
                            validators=[FileRequired(), FileAllowed(['py'], "python files only")])
    submit = SubmitField('Update')


class PostForm(FlaskForm):
    title = StringField('Title',
                            validators=[DataRequired()])
    content = TextAreaField('Content',
                            validators=[DataRequired()])
    submit = SubmitField('Post')

