from app import create_app, db
from app.models import User, VacationRequest
from datetime import datetime, timedelta

def create_test_data():
    app = create_app()
    with app.app_context():
        print("Creating test vacation requests...")
        
        # Get our users
        maria = User.query.filter_by(username='maria').first()
        thomas = User.query.filter_by(username='thomas').first()
        anna = User.query.filter_by(username='anna').first()
        
        if not all([maria, thomas, anna]):
            print("Error: Not all users found in database!")
            return
            
        # Create some test vacation requests
        requests = [
            # Maria's requests
            {
                'employee': maria,
                'substitute': thomas,
                'start_date': datetime(2024, 7, 1).date(),
                'end_date': datetime(2024, 7, 14).date(),
                'comment': 'Sommerurlaub mit Familie',
                'status': 'approved'
            },
            {
                'employee': maria,
                'substitute': anna,
                'start_date': datetime(2024, 12, 23).date(),
                'end_date': datetime(2024, 12, 31).date(),
                'comment': 'Weihnachtsurlaub',
                'status': 'pending'
            },
            # Thomas's requests
            {
                'employee': thomas,
                'substitute': maria,
                'start_date': datetime(2024, 8, 15).date(),
                'end_date': datetime(2024, 8, 30).date(),
                'comment': 'Sommerurlaub in Italien',
                'status': 'approved'
            },
            {
                'employee': thomas,
                'substitute': anna,
                'start_date': datetime(2024, 5, 21).date(),
                'end_date': datetime(2024, 5, 24).date(),
                'comment': 'Kurzurlaub',
                'status': 'pending'
            },
            # Anna's requests
            {
                'employee': anna,
                'substitute': maria,
                'start_date': datetime(2024, 6, 3).date(),
                'end_date': datetime(2024, 6, 14).date(),
                'comment': 'Familienurlaub',
                'status': 'approved'
            },
            {
                'employee': anna,
                'substitute': thomas,
                'start_date': datetime(2024, 10, 28).date(),
                'end_date': datetime(2024, 11, 1).date(),
                'comment': 'Herbsturlaub',
                'status': 'pending'
            }
        ]
        
        # Create the vacation requests
        for request_data in requests:
            request = VacationRequest(
                employee_id=request_data['employee'].id,
                substitute_id=request_data['substitute'].id,
                start_date=request_data['start_date'],
                end_date=request_data['end_date'],
                comment=request_data['comment'],
                status=request_data['status']
            )
            # Calculate and store work days
            request.work_days = request.calculate_work_days()
            db.session.add(request)
        
        try:
            db.session.commit()
            print("Successfully created test vacation requests!")
            
            # Print summary
            print("\nCreated vacation requests:")
            for user in [maria, thomas, anna]:
                requests = VacationRequest.query.filter_by(employee_id=user.id).all()
                print(f"\n{user.username}'s requests:")
                for req in requests:
                    print(f"- {req.start_date} to {req.end_date} ({req.status})")
                    print(f"  Work days: {req.work_days}, Substitute: {User.query.get(req.substitute_id).username}")
                print(f"  Remaining days: {user.remaining_days}")
            
        except Exception as e:
            print(f"Error creating test data: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_data()
