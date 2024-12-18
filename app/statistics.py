from datetime import datetime, date
from collections import defaultdict
from calendar import monthrange
from app.models import Employee, VacationRequest

def get_yearly_statistics(year):
    """Erstellt eine Jahresstatistik für alle Mitarbeiter"""
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    stats = {
        'total_employees': Employee.query.count(),
        'total_vacation_days': 0,
        'approved_requests': 0,
        'pending_requests': 0,
        'rejected_requests': 0,
        'monthly_stats': defaultdict(int),
        'department_stats': defaultdict(lambda: {
            'total_days': 0,
            'used_days': 0,
            'employees': 0
        }),
        'peak_periods': []
    }
    
    # Sammle alle Urlaubsanträge für das Jahr
    vacation_requests = VacationRequest.query.filter(
        VacationRequest.start_date >= start_date,
        VacationRequest.end_date <= end_date
    ).all()
    
    # Analysiere Urlaubsanträge
    monthly_vacation_days = defaultdict(int)
    for request in vacation_requests:
        if request.status == 'approved':
            stats['approved_requests'] += 1
            days = (request.end_date - request.start_date).days + 1
            
            # Zähle Tage pro Monat
            current_date = request.start_date
            while current_date <= request.end_date:
                monthly_vacation_days[current_date.month] += 1
                current_date = date(current_date.year,
                                  current_date.month,
                                  current_date.day + 1)
                
        elif request.status == 'pending':
            stats['pending_requests'] += 1
        else:
            stats['rejected_requests'] += 1
    
    # Berechne Spitzenzeiten (Monate mit den meisten Urlaubstagen)
    if monthly_vacation_days:
        max_days = max(monthly_vacation_days.values())
        peak_months = [month for month, days in monthly_vacation_days.items()
                      if days >= max_days * 0.8]  # 80% des Maximum
        stats['peak_periods'] = peak_months
    
    # Sammle Abteilungsstatistiken
    employees = Employee.query.all()
    for employee in employees:
        dept_stats = stats['department_stats'][employee.department]
        dept_stats['employees'] += 1
        dept_stats['total_days'] += employee.annual_leave_days + employee.carried_over_days
        
        # Berechne genutzten Urlaub
        used_days = sum(
            (req.end_date - req.start_date).days + 1
            for req in employee.vacation_requests
            if req.status == 'approved' and req.start_date.year == year
        )
        dept_stats['used_days'] += used_days
    
    return stats

def get_employee_statistics(employee, year):
    """Erstellt detaillierte Statistiken für einen einzelnen Mitarbeiter"""
    stats = {
        'total_days': employee.annual_leave_days + employee.carried_over_days,
        'used_days': 0,
        'remaining_days': 0,
        'vacation_periods': [],
        'monthly_distribution': defaultdict(int),
        'approval_time_avg': 0,  # Durchschnittliche Genehmigungszeit in Tagen
        'request_history': []
    }
    
    # Analysiere Urlaubsanträge
    approval_times = []
    for request in employee.vacation_requests:
        if request.start_date.year == year:
            days = (request.end_date - request.start_date).days + 1
            
            if request.status == 'approved':
                stats['used_days'] += days
                
                # Berechne Genehmigungszeit
                if request.approved_by:
                    approval_time = request.updated_at - request.request_date
                    approval_times.append(approval_time.days)
                
                # Zähle Tage pro Monat
                current_date = request.start_date
                while current_date <= request.end_date:
                    stats['monthly_distribution'][current_date.month] += 1
                    current_date = date(current_date.year,
                                      current_date.month,
                                      current_date.day + 1)
            
            stats['request_history'].append({
                'start_date': request.start_date,
                'end_date': request.end_date,
                'days': days,
                'status': request.status,
                'comment': request.comment
            })
    
    # Berechne durchschnittliche Genehmigungszeit
    if approval_times:
        stats['approval_time_avg'] = sum(approval_times) / len(approval_times)
    
    # Berechne verbleibende Urlaubstage
    stats['remaining_days'] = stats['total_days'] - stats['used_days']
    
    return stats

def get_department_statistics(department, year):
    """Erstellt Statistiken für eine Abteilung"""
    stats = {
        'total_employees': 0,
        'total_vacation_days': 0,
        'used_vacation_days': 0,
        'monthly_distribution': defaultdict(int),
        'employee_stats': [],
        'concurrent_vacations': defaultdict(int)  # Anzahl gleichzeitiger Urlaube pro Tag
    }
    
    employees = Employee.query.filter_by(department=department).all()
    stats['total_employees'] = len(employees)
    
    # Analysiere jeden Mitarbeiter
    for employee in employees:
        employee_total_days = employee.annual_leave_days + employee.carried_over_days
        stats['total_vacation_days'] += employee_total_days
        
        employee_used_days = 0
        for request in employee.vacation_requests:
            if request.start_date.year == year and request.status == 'approved':
                days = (request.end_date - request.start_date).days + 1
                employee_used_days += days
                
                # Zähle gleichzeitige Urlaube
                current_date = request.start_date
                while current_date <= request.end_date:
                    stats['concurrent_vacations'][current_date] += 1
                    current_date = date(current_date.year,
                                      current_date.month,
                                      current_date.day + 1)
        
        stats['used_vacation_days'] += employee_used_days
        stats['employee_stats'].append({
            'name': f"{employee.first_name} {employee.last_name}",
            'total_days': employee_total_days,
            'used_days': employee_used_days,
            'remaining_days': employee_total_days - employee_used_days
        })
    
    # Finde Tage mit den meisten gleichzeitigen Urlauben
    if stats['concurrent_vacations']:
        max_concurrent = max(stats['concurrent_vacations'].values())
        stats['peak_days'] = [
            date for date, count in stats['concurrent_vacations'].items()
            if count == max_concurrent
        ]
    
    return stats
