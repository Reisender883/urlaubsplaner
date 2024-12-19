from app import create_app, db
import logging
from logging.handlers import RotatingFileHandler
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
handler.setFormatter(formatter)

app = create_app()
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)
app.logger.info('Urlaubsplaner startup')

if __name__ == '__main__':
    with app.app_context():
        try:
            # Test database connection
            from app.models import User
            users = User.query.all()
            app.logger.info(f'Found {len(users)} users in database')
            for user in users:
                app.logger.info(f'User: {user.username} (Admin: {user.is_admin})')
                app.logger.info(f'  Email: {user.email}')
                app.logger.info(f'  Password hash: {user.password_hash[:20]}...')
                app.logger.info(f'  Annual leave: {user.annual_leave_days}')
                app.logger.info(f'  Carried over: {user.carried_over_days}')
                
        except Exception as e:
            app.logger.error(f'Error during startup: {str(e)}', exc_info=True)
            raise
            
    app.run(debug=True, use_reloader=False)
