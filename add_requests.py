from app import create_app, db
from app.models import User, VacationRequest
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_test_requests():
    app = create_app()
    with app.app_context():
        # Get users
        maria = User.query.filter_by(username='maria').first()
        thomas = User.query.filter_by(username='thomas').first()
        anna = User.query.filter_by(username='anna').first()
        
        if not all([maria, thomas, anna]):
            logger.error("Not all users found in database!")
            return
            
        # Create vacation requests
        requests = [
            # Maria's summer vacation (approved)
            {
                'employee': maria,
                'substitute': thomas,
                'start_date': datetime(2024, 7, 15).date(),
                'end_date': datetime(2024, 7, 26).date(),
                'comment': 'Sommerurlaub mit Familie',
                'status': 'approved'
            },
            # Thomas's Christmas vacation (pending)
            {
                'employee': thomas,
                'substitute': anna,
                'start_date': datetime(2024, 12, 23).date(),
                'end_date': datetime(2024, 12, 31).date(),
                'comment': 'Weihnachtsurlaub',
                'status': 'pending'
            }
        ]
        
        for request_data in requests:
            try:
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
                logger.info(f"Created request for {request_data['employee'].username}: "
                          f"{request_data['start_date']} - {request_data['end_date']} "
                          f"({request.work_days} work days)")
                
            except Exception as e:
                logger.error(f"Error creating request: {str(e)}")
                db.session.rollback()
                return
        
        try:
            db.session.commit()
            logger.info("Successfully added all vacation requests!")
            
            # Print summary of all requests
            for user in [maria, thomas, anna]:
                requests = VacationRequest.query.filter_by(employee_id=user.id).all()
                logger.info(f"\n{user.username}'s requests:")
                for req in requests:
                    substitute = User.query.get(req.substitute_id)
                    logger.info(f"- {req.start_date} to {req.end_date} ({req.status})")
                    logger.info(f"  Work days: {req.work_days}, Substitute: {substitute.username}")
                logger.info(f"  Remaining days: {user.remaining_days}")
                
        except Exception as e:
            logger.error(f"Error committing changes: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    add_test_requests()
