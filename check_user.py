from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    print('User exists:', user is not None)
    if user:
        print('Password hash:', user.password_hash)
        test_password = 'admin123'
        is_valid = user.check_password(test_password)
        print('Password check result:', is_valid)
