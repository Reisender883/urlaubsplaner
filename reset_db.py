import os
from app import create_app, db
from app.models import User, Employee, Holiday
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def reset_database():
    # Delete existing database
    if os.path.exists('app.db'):
        os.remove('app.db')
        logger.info("Deleted existing database")
    
    # Create new database
    app = create_app()
    with app.app_context():
        logger.info("Creating new database...")
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            annual_leave_days=30,
            carried_over_days=0
        )
        admin.set_password('admin')
        db.session.add(admin)
        logger.info("Created admin user")
        
        # Create cleaning staff users with different scenarios
        users = [
            {
                'username': 'maria',
                'email': 'maria@reinigung.de',
                'password': 'maria123',
                'annual_leave_days': 30,
                'carried_over_days': 5  # Has some days carried over from last year
            },
            {
                'username': 'thomas',
                'email': 'thomas@reinigung.de',
                'password': 'thomas123',
                'annual_leave_days': 30,
                'carried_over_days': 0  # Standard case
            },
            {
                'username': 'anna',
                'email': 'anna@reinigung.de',
                'password': 'anna123',
                'annual_leave_days': 25,  # Part-time employee
                'carried_over_days': 2
            }
        ]
        
        for user_data in users:
            try:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    annual_leave_days=user_data['annual_leave_days'],
                    carried_over_days=user_data['carried_over_days']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                logger.info(f"Created user: {user_data['username']}")
            except Exception as e:
                logger.error(f"Error creating user {user_data['username']}: {str(e)}")
                db.session.rollback()
                raise
        
        # Initialize default holidays
        holidays = [
            {'name': 'Neujahr', 'date': '2024-01-01'},
            {'name': 'Heilige Drei Könige', 'date': '2024-01-06'},
            {'name': 'Karfreitag', 'date': '2024-03-29'},
            {'name': 'Ostermontag', 'date': '2024-04-01'},
            {'name': 'Tag der Arbeit', 'date': '2024-05-01'},
            {'name': 'Christi Himmelfahrt', 'date': '2024-05-09'},
            {'name': 'Pfingstmontag', 'date': '2024-05-20'},
            {'name': 'Fronleichnam', 'date': '2024-05-30'},
            {'name': 'Mariä Himmelfahrt', 'date': '2024-08-15'},
            {'name': 'Tag der Deutschen Einheit', 'date': '2024-10-03'},
            {'name': 'Allerheiligen', 'date': '2024-11-01'},
            {'name': 'Heiligabend', 'date': '2024-12-24', 'half_day': True},
            {'name': '1. Weihnachtstag', 'date': '2024-12-25'},
            {'name': '2. Weihnachtstag', 'date': '2024-12-26'},
            {'name': 'Silvester', 'date': '2024-12-31', 'half_day': True}
        ]
        
        for holiday_data in holidays:
            try:
                date = datetime.strptime(holiday_data['date'], '%Y-%m-%d').date()
                holiday = Holiday(
                    name=holiday_data['name'],
                    date=date,
                    half_day=holiday_data.get('half_day', False)
                )
                db.session.add(holiday)
                logger.info(f"Created holiday: {holiday_data['name']}")
            except Exception as e:
                logger.error(f"Error creating holiday {holiday_data['name']}: {str(e)}")
                db.session.rollback()
                raise
        
        try:
            db.session.commit()
            logger.info("Successfully committed all changes to database")
        except Exception as e:
            logger.error(f"Error committing changes: {str(e)}")
            db.session.rollback()
            raise
        
        # Verify users were created
        users = User.query.all()
        logger.info(f"\nVerifying users in database:")
        for user in users:
            logger.info(f"- {user.username} (Email: {user.email}, Admin: {user.is_admin})")
            logger.info(f"  Password hash exists: {bool(user.password_hash)}")

if __name__ == '__main__':
    reset_database()
