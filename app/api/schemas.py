from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from app.models import Employee, VacationRequest

class EmployeeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        include_relationships = True
        load_instance = True
    
    id = auto_field()
    username = auto_field()
    email = auto_field()
    first_name = auto_field()
    last_name = auto_field()
    department = auto_field()
    annual_leave_days = auto_field()
    carried_over_days = auto_field()
    is_admin = auto_field()
    vacation_requests = fields.Nested('VacationRequestSchema', many=True, exclude=('employee',))

class VacationRequestSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = VacationRequest
        include_relationships = True
        load_instance = True
    
    id = auto_field()
    employee_id = auto_field()
    substitute_id = auto_field()
    start_date = auto_field()
    end_date = auto_field()
    status = auto_field()
    comment = auto_field()
    request_date = auto_field()
    approved_by = auto_field()
    employee = fields.Nested(EmployeeSchema, exclude=('vacation_requests',))
    substitute = fields.Nested(EmployeeSchema, exclude=('vacation_requests',))

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)
vacation_request_schema = VacationRequestSchema()
vacation_requests_schema = VacationRequestSchema(many=True)
