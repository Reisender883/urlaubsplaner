from app import db, login
from flask_login import UserMixin
from datetime import datetime, time
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    hours_per_week = db.Column(db.Integer)
    workdays = db.Column(db.String(128))
    work_start = db.Column(db.Time, default=time(9, 0))
    work_end = db.Column(db.Time, default=time(17, 0))
    break_duration = db.Column(db.Integer, default=60)  # in minutes
    assignments = db.relationship('ResourceAssignment', backref='employee', lazy='dynamic')

    def __repr__(self):
        return f'<Employee {self.name}>'

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.Text)
    min_staff_required = db.Column(db.Integer, default=1)
    assignments = db.relationship('ResourceAssignment', backref='resource', lazy='dynamic')

    def __repr__(self):
        return f'<Resource {self.name}>'

class ResourceAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    capacity_percentage = db.Column(db.Integer)
    hours_per_week = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<ResourceAssignment {self.employee_id} - {self.capacity_percentage}%>'

class VacationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    comment = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<VacationRequest {self.employee_id} {self.start_date} to {self.end_date}>'
