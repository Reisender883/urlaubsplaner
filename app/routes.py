from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user, logout_user
from app.models import Employee, VacationRequest
from app import db

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@login_required
def index():
    return render_template('index.html')

@main.route('/calendar')
@login_required
def calendar():
    vacation_requests = VacationRequest.query.all()
    return render_template('calendar.html', vacation_requests=vacation_requests)

@main.route('/request_vacation', methods=['GET', 'POST'])
@login_required
def request_vacation():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        comment = request.form.get('comment')
        
        vacation_request = VacationRequest(
            employee_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            comment=comment
        )
        db.session.add(vacation_request)
        db.session.commit()
        flash('Urlaubsantrag wurde eingereicht.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('request_vacation.html')

@main.route('/my_requests')
@login_required
def my_requests():
    requests = VacationRequest.query.filter_by(employee_id=current_user.id).all()
    return render_template('my_requests.html', requests=requests)
