from flask import jsonify, request
from flask_restful import Resource
from app import db
from app.models import Employee, VacationRequest
from app.api.schemas import (employee_schema, employees_schema,
                           vacation_request_schema, vacation_requests_schema)
from app.api.auth import token_required, admin_required
from app.email import (send_vacation_request_notification,
                      send_vacation_status_notification,
                      send_substitute_notification)
from datetime import datetime

class EmployeeResource(Resource):
    @token_required
    def get(current_user, self, employee_id):
        """Einzelnen Mitarbeiter abrufen"""
        if not current_user.is_admin and current_user.id != employee_id:
            return {'message': 'Keine Berechtigung!'}, 403
        
        employee = Employee.query.get_or_404(employee_id)
        return employee_schema.dump(employee)

class EmployeeListResource(Resource):
    @token_required
    @admin_required
    def get(current_user, self):
        """Alle Mitarbeiter abrufen"""
        employees = Employee.query.all()
        return employees_schema.dump(employees)
    
    @token_required
    @admin_required
    def post(current_user, self):
        """Neuen Mitarbeiter anlegen"""
        json_data = request.get_json()
        if not json_data:
            return {'message': 'Keine Daten erhalten'}, 400
        
        try:
            employee = employee_schema.load(json_data)
            db.session.add(employee)
            db.session.commit()
            return employee_schema.dump(employee), 201
        except Exception as e:
            return {'message': str(e)}, 400

class VacationRequestResource(Resource):
    @token_required
    def get(current_user, self, request_id):
        """Einzelnen Urlaubsantrag abrufen"""
        vacation_request = VacationRequest.query.get_or_404(request_id)
        
        if not current_user.is_admin and current_user.id != vacation_request.employee_id:
            return {'message': 'Keine Berechtigung!'}, 403
        
        return vacation_request_schema.dump(vacation_request)
    
    @token_required
    def put(current_user, self, request_id):
        """Urlaubsantrag aktualisieren"""
        vacation_request = VacationRequest.query.get_or_404(request_id)
        
        if not current_user.is_admin and current_user.id != vacation_request.employee_id:
            return {'message': 'Keine Berechtigung!'}, 403
        
        json_data = request.get_json()
        if not json_data:
            return {'message': 'Keine Daten erhalten'}, 400
        
        try:
            if current_user.is_admin:
                if 'status' in json_data:
                    vacation_request.status = json_data['status']
                    vacation_request.approved_by = current_user.id
                    send_vacation_status_notification(vacation_request)
            
            if current_user.id == vacation_request.employee_id:
                if 'comment' in json_data:
                    vacation_request.comment = json_data['comment']
            
            db.session.commit()
            return vacation_request_schema.dump(vacation_request)
        except Exception as e:
            return {'message': str(e)}, 400

class VacationRequestListResource(Resource):
    @token_required
    def get(current_user, self):
        """Urlaubsanträge abrufen"""
        if current_user.is_admin:
            requests = VacationRequest.query.all()
        else:
            requests = VacationRequest.query.filter_by(employee_id=current_user.id).all()
        
        return vacation_requests_schema.dump(requests)
    
    @token_required
    def post(current_user, self):
        """Neuen Urlaubsantrag erstellen"""
        json_data = request.get_json()
        if not json_data:
            return {'message': 'Keine Daten erhalten'}, 400
        
        try:
            # Validiere verfügbare Urlaubstage
            start_date = datetime.strptime(json_data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(json_data['end_date'], '%Y-%m-%d').date()
            days = (end_date - start_date).days + 1
            
            remaining_days = current_user.annual_leave_days + current_user.carried_over_days
            used_days = sum([(req.end_date - req.start_date).days + 1 
                           for req in current_user.vacation_requests
                           if req.status != 'rejected'])
            
            if days > (remaining_days - used_days):
                return {'message': 'Nicht genügend Urlaubstage verfügbar!'}, 400
            
            # Erstelle Urlaubsantrag
            json_data['employee_id'] = current_user.id
            vacation_request = vacation_request_schema.load(json_data)
            
            db.session.add(vacation_request)
            db.session.commit()
            
            # Sende Benachrichtigungen
            admins = Employee.query.filter_by(is_admin=True).all()
            send_vacation_request_notification(vacation_request, admins)
            if vacation_request.substitute:
                send_substitute_notification(vacation_request)
            
            return vacation_request_schema.dump(vacation_request), 201
        except Exception as e:
            return {'message': str(e)}, 400

class DepartmentVacationResource(Resource):
    @token_required
    @admin_required
    def get(current_user, self, department):
        """Urlaubsanträge einer Abteilung abrufen"""
        employees = Employee.query.filter_by(department=department).all()
        employee_ids = [e.id for e in employees]
        
        requests = VacationRequest.query.filter(
            VacationRequest.employee_id.in_(employee_ids)
        ).all()
        
        return vacation_requests_schema.dump(requests)
