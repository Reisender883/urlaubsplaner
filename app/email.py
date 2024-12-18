from flask import current_app, render_template
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_vacation_request_notification(request, approvers):
    """Benachrichtigt Administratoren über einen neuen Urlaubsantrag"""
    send_email(
        subject='Neuer Urlaubsantrag',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[admin.email for admin in approvers],
        text_body=render_template('email/vacation_request.txt',
                                request=request),
        html_body=render_template('email/vacation_request.html',
                                request=request)
    )

def send_vacation_status_notification(request):
    """Benachrichtigt den Mitarbeiter über den Status seines Urlaubsantrags"""
    send_email(
        subject='Status Ihres Urlaubsantrags',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[request.employee.email],
        text_body=render_template('email/vacation_status.txt',
                                request=request),
        html_body=render_template('email/vacation_status.html',
                                request=request)
    )

def send_substitute_notification(request):
    """Benachrichtigt die Vertretung über einen neuen Urlaubsantrag"""
    if request.substitute:
        send_email(
            subject='Vertretungsanfrage',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[request.substitute.email],
            text_body=render_template('email/substitute_request.txt',
                                    request=request),
            html_body=render_template('email/substitute_request.html',
                                    request=request)
        )

def send_resource_assignment_notification(assignment):
    """Benachrichtigt einen Mitarbeiter über eine neue Ressourcenzuordnung"""
    subject = f'Neue Ressourcenzuordnung: {assignment.resource.name}'
    
    send_email(
        subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[assignment.employee.email],
        text_body=render_template('email/resource_assignment.txt',
                                assignment=assignment),
        html_body=render_template('email/resource_assignment.html',
                                assignment=assignment)
    )

def send_resource_status_notification(resource):
    """Benachrichtigt Verantwortliche über kritische Ressourcenzustände"""
    current_staff = resource.assignments.filter_by(end_date=None).count()
    
    if current_staff < resource.min_staff_required:
        subject = f'Kritische Besetzung: {resource.name}'
        
        # Finde alle Hauptverantwortlichen
        primary_staff = resource.assignments.filter_by(
            is_primary=True,
            end_date=None
        ).all()
        
        # Wenn keine Hauptverantwortlichen, sende an alle Administratoren
        if not primary_staff:
            recipients = [emp.email for emp in Employee.query.filter_by(is_admin=True)]
        else:
            recipients = [assignment.employee.email for assignment in primary_staff]
        
        if recipients:
            send_email(
                subject,
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=recipients,
                text_body=render_template('email/resource_status.txt',
                                        resource=resource,
                                        current_staff=current_staff),
                html_body=render_template('email/resource_status.html',
                                        resource=resource,
                                        current_staff=current_staff)
            )

def send_resource_conflict_notification(resource, start_date, end_date, affected_employees):
    """Benachrichtigt über Ressourcenkonflikte bei Urlaubsanträgen"""
    subject = f'Ressourcenkonflikt: {resource.name}'
    
    # Benachrichtige Hauptverantwortliche und Administratoren
    primary_staff = resource.assignments.filter_by(
        is_primary=True,
        end_date=None
    ).all()
    
    recipients = set()
    
    # Hauptverantwortliche
    for assignment in primary_staff:
        recipients.add(assignment.employee.email)
    
    # Administratoren
    for admin in Employee.query.filter_by(is_admin=True):
        recipients.add(admin.email)
    
    if recipients:
        send_email(
            subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=list(recipients),
            text_body=render_template('email/resource_conflict.txt',
                                    resource=resource,
                                    start_date=start_date,
                                    end_date=end_date,
                                    affected_employees=affected_employees),
            html_body=render_template('email/resource_conflict.html',
                                    resource=resource,
                                    start_date=start_date,
                                    end_date=end_date,
                                    affected_employees=affected_employees)
        )

def send_resource_reminder(assignment):
    """Sendet Erinnerungen für wichtige Ressourcen"""
    if assignment.resource.priority >= 4:  # Nur für hohe Prioritäten
        subject = f'Erinnerung: Verantwortlichkeit für {assignment.resource.name}'
        
        send_email(
            subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[assignment.employee.email],
            text_body=render_template('email/resource_reminder.txt',
                                    assignment=assignment),
            html_body=render_template('email/resource_reminder.html',
                                    assignment=assignment)
        )
