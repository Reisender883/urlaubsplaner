from app import create_app, db
from app.models import User, Holiday, VacationRequest

def check_database():
    app = create_app()
    with app.app_context():
        print("\nUsers in database:")
        users = User.query.all()
        for user in users:
            print(f"- {user.username} (Email: {user.email}, Admin: {user.is_admin})")
            print(f"  Annual leave: {user.annual_leave_days}, Carried over: {user.carried_over_days}")
            
            # Check password hash
            print(f"  Has password hash: {'Yes' if user.password_hash else 'No'}")
        
        print("\nHolidays in database:")
        holidays = Holiday.query.all()
        for holiday in holidays:
            print(f"- {holiday.name} ({holiday.date}, Half day: {holiday.half_day})")
            
        print("\nVacation Requests in database:")
        requests = VacationRequest.query.all()
        for request in requests:
            employee = User.query.get(request.employee_id)
            substitute = User.query.get(request.substitute_id)
            print(f"- {employee.username} -> {substitute.username}")
            print(f"  {request.start_date} to {request.end_date} ({request.status})")
            print(f"  Work days: {request.work_days}")

if __name__ == '__main__':
    check_database()
