from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user, login_user, logout_user
from flask_mail import Message
from app.models import User, Employee, ResourceAssignment, VacationRequest, Holiday
from app.forms import LoginForm, RegistrationForm, EmployeeForm, ResourceAssignmentForm, VacationRequestForm
from app import db, mail
from datetime import timedelta, datetime

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    
    # Get all vacation requests for the current user
    vacation_requests = VacationRequest.query.filter_by(employee_id=current_user.id).all()
    
    # Get substitute requests where the current user is the substitute
    substitute_requests = VacationRequest.query.filter_by(substitute_id=current_user.id).all()
    
    return render_template('index.html', 
                         title='Home',
                         vacation_requests=vacation_requests,
                         substitute_requests=substitute_requests)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    print("Login route accessed")  # Debug print
    if current_user.is_authenticated:
        print("User already authenticated, redirecting to index")  # Debug print
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        print(f"Form validated, username: {form.username.data}")  # Debug print
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None:
            print("User not found")  # Debug print
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
            
        if not user.check_password(form.password.data):
            print("Invalid password")  # Debug print
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
            
        print(f"Login successful for user: {user.username}")  # Debug print
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
            
        print(f"Redirecting to: {next_page}")  # Debug print
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            annual_leave_days=30,
            carried_over_days=0
        )
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

@bp.route('/request-vacation', methods=['GET', 'POST'])
@login_required
def request_vacation():
    form = VacationRequestForm()
    # Get all users except current user for substitute selection
    form.substitute.choices = [(u.id, u.username) for u in User.query.filter(User.id != current_user.id).all()]
    
    if form.validate_on_submit():
        vacation_request = VacationRequest(
            employee_id=current_user.id,
            substitute_id=form.substitute.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            comment=form.comment.data,
            status='pending'
        )
        
        # Calculate and store work days
        vacation_request.work_days = vacation_request.calculate_work_days()
        
        # Check if user has enough vacation days
        if vacation_request.work_days > current_user.remaining_days:
            flash('Sie haben nicht genügend Urlaubstage.', 'error')
            return redirect(url_for('main.request_vacation'))
        
        try:
            db.session.add(vacation_request)
            db.session.commit()
            
            # Send email to substitute
            substitute = User.query.get(form.substitute.data)
            if substitute and substitute.email:
                msg = Message('Neuer Urlaubsantrag',
                            sender=current_app.config['MAIL_DEFAULT_SENDER'],
                            recipients=[substitute.email])
                msg.html = render_template('email/vacation_request.html',
                                        user=current_user,
                                        request=vacation_request)
                mail.send(msg)
            
            flash('Ihr Urlaubsantrag wurde erfolgreich eingereicht!', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.', 'error')
            return redirect(url_for('main.request_vacation'))
    
    return render_template('request_vacation.html', 
                         title='Urlaub beantragen', 
                         form=form)

@bp.route('/approve-vacation/<int:id>/<string:action>')
@login_required
def approve_vacation(id, action):
    if not current_user.is_admin:
        flash('Sie haben keine Berechtigung für diese Aktion.', 'error')
        return redirect(url_for('main.index'))
        
    vacation_request = VacationRequest.query.get_or_404(id)
    
    if action not in ['approve', 'reject']:
        flash('Ungültige Aktion.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        vacation_request.status = 'approved' if action == 'approve' else 'rejected'
        db.session.commit()
        
        # Send email to employee
        if vacation_request.employee.email:
            msg = Message('Urlaubsantrag Status Update',
                        sender=current_app.config['MAIL_DEFAULT_SENDER'],
                        recipients=[vacation_request.employee.email])
            msg.html = render_template('email/vacation_status.html',
                                    request=vacation_request)
            mail.send(msg)
        
        flash(f'Urlaubsantrag wurde {"genehmigt" if action == "approve" else "abgelehnt"}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.', 'error')
    
    return redirect(url_for('main.index'))

@bp.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html', title='Urlaubskalender')

@bp.route('/calendar/events')
@login_required
def calendar_events():
    vacation_requests = VacationRequest.query.all()
    events = []
    
    for request in vacation_requests:
        status_colors = {
            'pending': '#ffc107',  # Yellow
            'approved': '#28a745',  # Green
            'rejected': '#dc3545'   # Red
        }
        
        events.append({
            'title': f'{request.employee.name} - Urlaub',
            'start': request.start_date.isoformat(),
            'end': (request.end_date + timedelta(days=1)).isoformat(),
            'color': status_colors.get(request.status, '#6c757d'),
            'employee': request.employee.name,
            'status': request.status,
            'comment': request.comment
        })
    
    return jsonify(events)

@bp.route('/my-requests')
@login_required
def my_requests():
    # TODO: Get user's vacation requests
    requests = []  # Replace with actual database query
    return render_template('my_requests.html', title='My Requests', requests=requests)

@bp.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Sie haben keine Berechtigung für diese Seite.', 'error')
        return redirect(url_for('main.index'))
        
    # Get all vacation requests
    vacation_requests = VacationRequest.query.all()
    
    # Get all users except admin
    users = User.query.filter(User.is_admin == False).all()
    
    return render_template('admin.html', 
                         title='Admin',
                         vacation_requests=vacation_requests,
                         users=users)

@bp.route('/holidays', methods=['GET', 'POST'])
@login_required
def holidays():
    if not current_user.is_admin:
        flash('You do not have permission to manage holidays.')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        if request.form.get('action') == 'add':
            holiday = Holiday(
                name=request.form.get('name'),
                date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
                half_day=bool(request.form.get('half_day')),
                recurring=bool(request.form.get('recurring'))
            )
            db.session.add(holiday)
            db.session.commit()
            flash('Holiday added successfully.')
        
        elif request.form.get('action') == 'delete':
            holiday_id = request.form.get('holiday_id')
            holiday = Holiday.query.get_or_404(holiday_id)
            db.session.delete(holiday)
            db.session.commit()
            flash('Holiday deleted successfully.')
        
        elif request.form.get('action') == 'edit':
            holiday_id = request.form.get('holiday_id')
            holiday = Holiday.query.get_or_404(holiday_id)
            holiday.name = request.form.get('name')
            holiday.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            holiday.half_day = bool(request.form.get('half_day'))
            holiday.recurring = bool(request.form.get('recurring'))
            db.session.commit()
            flash('Holiday updated successfully.')
    
    holidays = Holiday.query.order_by(Holiday.date).all()
    return render_template('holidays.html', title='Manage Holidays', holidays=holidays)

def init_holidays():
    """Initialize default Bavarian holidays"""
    default_holidays = [
        ('Neujahr', '01-01', True),
        ('Heilige Drei Könige', '01-06', True),
        ('Karfreitag', '03-29', True),  # Date varies, needs manual update
        ('Ostermontag', '04-01', True),  # Date varies, needs manual update
        ('Tag der Arbeit', '05-01', True),
        ('Christi Himmelfahrt', '05-09', True),  # Date varies, needs manual update
        ('Pfingstmontag', '05-20', True),  # Date varies, needs manual update
        ('Fronleichnam', '05-30', True),  # Date varies, needs manual update
        ('Mariä Himmelfahrt', '08-15', True),
        ('Tag der Deutschen Einheit', '10-03', True),
        ('Allerheiligen', '11-01', True),
        ('Heiligabend', '12-24', True, True),  # Half day
        ('1. Weihnachtstag', '12-25', True),
        ('2. Weihnachtstag', '12-26', True),
        ('Silvester', '12-31', True, True),  # Half day
    ]
    
    year = datetime.now().year
    for name, date_str, recurring, *half_day in default_holidays:
        date = datetime.strptime(f'{year}-{date_str}', '%Y-%m-%d').date()
        if not Holiday.query.filter_by(name=name, date=date).first():
            holiday = Holiday(
                name=name,
                date=date,
                recurring=recurring,
                half_day=half_day[0] if half_day else False
            )
            db.session.add(holiday)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
