from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS
from app.api.resources import (EmployeeResource, EmployeeListResource,
                             VacationRequestResource, VacationRequestListResource,
                             DepartmentVacationResource)

api_bp = Blueprint('api', __name__)
CORS(api_bp)  # Aktiviere CORS für alle API-Routen
api = Api(api_bp)

# API Routen
api.add_resource(EmployeeResource, '/employees/<int:employee_id>')
api.add_resource(EmployeeListResource, '/employees')
api.add_resource(VacationRequestResource, '/vacation-requests/<int:request_id>')
api.add_resource(VacationRequestListResource, '/vacation-requests')
api.add_resource(DepartmentVacationResource, '/departments/<string:department>/vacation-requests')
