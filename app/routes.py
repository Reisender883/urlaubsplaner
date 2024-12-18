from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from app.models import User, Employee, ResourceAssignment
from app.forms import LoginForm, RegistrationForm, EmployeeForm, ResourceAssignmentForm
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/employees', methods=['GET', 'POST'])
@login_required
def employees():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee(
            name=form.name.data,
            hours_per_week=form.hours_per_week.data,
            workdays=','.join(form.workdays.data),
            work_start=form.work_start.data,
            work_end=form.work_end.data,
            break_duration=form.break_duration.data
        )
        db.session.add(employee)
        db.session.commit()
        flash('Employee added successfully.')
        return redirect(url_for('main.employees'))
    
    employees = Employee.query.all()
    return render_template('employees.html', title='Employees', form=form, employees=employees)

@bp.route('/resource-assignments', methods=['GET', 'POST'])
@login_required
def resource_assignments():
    form = ResourceAssignmentForm()
    if form.validate_on_submit():
        assignment = ResourceAssignment(
            employee_id=form.employee.data,
            capacity_percentage=form.capacity_percentage.data,
            hours_per_week=form.hours_per_week.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Resource assignment added successfully.')
        return redirect(url_for('main.resource_assignments'))
    
    assignments = ResourceAssignment.query.all()
    return render_template('resources.html', title='Resource Assignments', form=form, assignments=assignments)
