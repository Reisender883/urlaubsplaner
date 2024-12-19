from app import db, login
from flask_login import UserMixin
from datetime import datetime, time, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    annual_leave_days = db.Column(db.Integer, default=30)
    carried_over_days = db.Column(db.Integer, default=0)
    
    # Relationships
    vacation_requests = db.relationship('VacationRequest', 
                                      foreign_keys='VacationRequest.employee_id',
                                      backref='employee', 
                                      lazy='dynamic')
    substitute_requests = db.relationship('VacationRequest', 
                                        foreign_keys='VacationRequest.substitute_id',
                                        backref='substitute', 
                                        lazy='dynamic')

    @property
    def remaining_days(self):
        used_days = sum(
            request.work_days if request.work_days is not None else request.calculate_work_days()
            for request in self.vacation_requests
            if request.status in ['pending', 'approved']
        )
        return float(self.annual_leave_days + self.carried_over_days) - used_days

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
        return f'<ResourceAssignment {self.employee_id} -> {self.resource_id}>'

class Holiday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False)
    state = db.Column(db.String(50), default='Bayern')
    half_day = db.Column(db.Boolean, default=False)
    recurring = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Holiday {self.name} {self.date}>'

class VacationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    substitute_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')
    comment = db.Column(db.Text)
    work_days = db.Column(db.Float)

    def calculate_work_days(self):
        if not self.start_date or not self.end_date:
            return 0
            
        current_date = self.start_date
        work_days = 0
        
        while current_date <= self.end_date:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                # Check for holidays
                holiday = Holiday.query.filter_by(date=current_date).first()
                if holiday:
                    if holiday.half_day:
                        work_days += 0.5
                    # If not half day, skip this day (it's a full holiday)
                else:
                    work_days += 1
                    
            current_date += timedelta(days=1)
            
        return work_days

    def __repr__(self):
        return f'<VacationRequest {self.employee_id} ({self.start_date} - {self.end_date})>'
