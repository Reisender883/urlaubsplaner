from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText
from caldav import DAVClient
from caldav.elements import dav, cdav
import vobject
from flask import current_app, url_for
from app.models import VacationRequest, Employee

def create_ical_event(vacation_request):
    """Erstellt ein iCal-Event für einen Urlaubsantrag"""
    event = Event()
    
    # Grundlegende Event-Informationen
    event.add('summary', f'Urlaub: {vacation_request.employee.first_name} {vacation_request.employee.last_name}')
    event.add('dtstart', vacation_request.start_date)
    # Ende ist der nächste Tag, da der Endtag eingeschlossen ist
    end_date = vacation_request.end_date + timedelta(days=1)
    event.add('dtend', end_date)
    
    # Erstelle detaillierte Beschreibung
    description = [
        f'Mitarbeiter: {vacation_request.employee.first_name} {vacation_request.employee.last_name}',
        f'Abteilung: {vacation_request.employee.department}',
    ]
    
    if vacation_request.substitute:
        description.append(f'Vertretung: {vacation_request.substitute.first_name} {vacation_request.substitute.last_name}')
    
    if vacation_request.comment:
        description.append(f'Kommentar: {vacation_request.comment}')
    
    event.add('description', '\n'.join(description))
    
    # Füge eindeutige ID hinzu
    event['uid'] = f'vacation-{vacation_request.id}@{current_app.config["DOMAIN"]}'
    
    # Setze Status basierend auf Urlaubsantrag
    if vacation_request.status == 'approved':
        event.add('status', 'CONFIRMED')
    elif vacation_request.status == 'rejected':
        event.add('status', 'CANCELLED')
    else:
        event.add('status', 'TENTATIVE')
    
    # Füge Kategorien hinzu
    event.add('categories', ['Urlaub', vacation_request.employee.department])
    
    # Füge Link zum Urlaubsantrag hinzu
    event.add('url', url_for('main.vacation_request_details',
                            request_id=vacation_request.id,
                            _external=True))
    
    return event

def create_department_calendar(department):
    """Erstellt einen Kalender für eine Abteilung"""
    cal = Calendar()
    
    # Setze Kalender-Eigenschaften
    cal.add('prodid', f'-//Urlaubsplaner//Abteilung {department}//')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', f'Urlaub - {department}')
    cal.add('x-wr-caldesc', f'Urlaubskalender der Abteilung {department}')
    
    # Füge alle Urlaubsanträge der Abteilung hinzu
    employees = Employee.query.filter_by(department=department).all()
    for employee in employees:
        for request in employee.vacation_requests:
            if request.status == 'approved':  # Nur genehmigte Anträge
                cal.add_component(create_ical_event(request))
    
    return cal

def create_employee_calendar(employee):
    """Erstellt einen persönlichen Kalender für einen Mitarbeiter"""
    cal = Calendar()
    
    # Setze Kalender-Eigenschaften
    cal.add('prodid', f'-//Urlaubsplaner//Mitarbeiter {employee.id}//')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', f'Urlaub - {employee.first_name} {employee.last_name}')
    cal.add('x-wr-caldesc', f'Persönlicher Urlaubskalender von {employee.first_name} {employee.last_name}')
    
    # Füge alle Urlaubsanträge des Mitarbeiters hinzu
    for request in employee.vacation_requests:
        cal.add_component(create_ical_event(request))
    
    return cal

def sync_with_caldav(employee, calendar_url, username, password):
    """Synchronisiert Urlaubsanträge mit einem CalDAV-Server"""
    try:
        # Verbinde mit CalDAV-Server
        client = DAVClient(url=calendar_url,
                         username=username,
                         password=password)
        
        # Hole Principal und Calendar
        principal = client.principal()
        calendars = principal.calendars()
        
        # Suche oder erstelle Urlaubskalender
        vacation_calendar = None
        for cal in calendars:
            if cal.get_properties([dav.DisplayName])[dav.DisplayName] == 'Urlaub':
                vacation_calendar = cal
                break
        
        if not vacation_calendar:
            # Erstelle neuen Kalender
            vacation_calendar = principal.make_calendar(name='Urlaub')
        
        # Hole existierende Events
        events = vacation_calendar.events()
        existing_uids = {event.icalendar_component['uid'] for event in events}
        
        # Synchronisiere Urlaubsanträge
        for request in employee.vacation_requests:
            event = create_ical_event(request)
            uid = event['uid']
            
            if uid in existing_uids:
                # Update existierendes Event
                for existing_event in events:
                    if existing_event.icalendar_component['uid'] == uid:
                        existing_event.load()
                        if request.status == 'rejected':
                            existing_event.delete()
                        else:
                            existing_event.save(event.to_ical())
                        break
            else:
                # Erstelle neues Event
                if request.status != 'rejected':
                    vacation_calendar.save_event(event.to_ical())
        
        return True, "Kalender erfolgreich synchronisiert"
    except Exception as e:
        return False, f"Fehler bei der Kalendersynchronisation: {str(e)}"

def subscribe_to_calendar(calendar_type, identifier):
    """Erstellt eine Kalender-Abonnement-URL"""
    if calendar_type == 'department':
        department = identifier
        calendar = create_department_calendar(department)
    else:  # employee
        employee = Employee.query.get(identifier)
        if not employee:
            return None
        calendar = create_employee_calendar(employee)
    
    return calendar.to_ical()
