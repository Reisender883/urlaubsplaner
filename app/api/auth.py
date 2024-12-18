from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from app.models import Employee

def generate_token(employee):
    """Generiert ein JWT Token für einen Mitarbeiter"""
    payload = {
        'user_id': employee.id,
        'is_admin': employee.is_admin,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    """Decorator für geschützte API-Routen"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token fehlt!'}), 401
        
        if not token:
            return jsonify({'message': 'Token fehlt!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Employee.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token ungültig!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator für Admin-geschützte API-Routen"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin-Rechte erforderlich!'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated
