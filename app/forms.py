from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, DateField, SelectField, SubmitField, IntegerField, SelectMultipleField, FloatField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, URL, NumberRange
from app.models import Employee, User
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    hours_per_week = IntegerField('Hours per Week', validators=[DataRequired(), NumberRange(min=1, max=168)])
    workdays = SelectMultipleField('Work Days', choices=[
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], validators=[DataRequired()])
    work_start = TimeField('Work Start Time', validators=[DataRequired()])
    work_end = TimeField('Work End Time', validators=[DataRequired()])
    break_duration = IntegerField('Break Duration (minutes)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Employee')

class ResourceAssignmentForm(FlaskForm):
    employee = SelectField('Employee', coerce=int, validators=[DataRequired()])
    capacity_percentage = IntegerField('Capacity Percentage', validators=[DataRequired(), NumberRange(min=1, max=100)])
    hours_per_week = IntegerField('Hours per Week', validators=[NumberRange(min=1)])
    submit = SubmitField('Add Assignment')

    def __init__(self, *args, **kwargs):
        super(ResourceAssignmentForm, self).__init__(*args, **kwargs)
        self.employee.choices = [(e.id, e.name) for e in Employee.query.all()]
