import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from io import BytesIO
import os
from flask import current_app
from app.models import Employee, VacationRequest

def generate_vacation_analysis(year):
    """Generiert eine detaillierte Urlaubsanalyse"""
    # Hole alle Urlaubsanträge für das Jahr
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()
    
    vacation_requests = VacationRequest.query.filter(
        VacationRequest.start_date >= start_date,
        VacationRequest.end_date <= end_date,
        VacationRequest.status == 'approved'
    ).all()
    
    # Erstelle DataFrame für die Analyse
    data = []
    for request in vacation_requests:
        data.append({
            'employee_id': request.employee_id,
            'employee_name': f"{request.employee.first_name} {request.employee.last_name}",
            'department': request.employee.department,
            'start_date': request.start_date,
            'end_date': request.end_date,
            'days': (request.end_date - request.start_date).days + 1,
            'month': request.start_date.month
        })
    
    df = pd.DataFrame(data)
    
    # Verschiedene Analysen
    analyses = {
        'monthly_distribution': analyze_monthly_distribution(df),
        'department_summary': analyze_department_distribution(df),
        'peak_periods': analyze_peak_periods(df),
        'employee_summary': analyze_employee_distribution(df)
    }
    
    return analyses

def analyze_monthly_distribution(df):
    """Analysiert die monatliche Verteilung der Urlaubstage"""
    if df.empty:
        return None
    
    monthly_data = df.groupby('month')['days'].sum().reindex(range(1, 13), fill_value=0)
    
    fig = px.bar(monthly_data,
                 labels={'month': 'Monat', 'value': 'Urlaubstage'},
                 title='Urlaubstage pro Monat')
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def analyze_department_distribution(df):
    """Analysiert die Urlaubsverteilung nach Abteilungen"""
    if df.empty:
        return None
    
    dept_data = df.groupby('department')['days'].agg(['sum', 'count']).reset_index()
    dept_data.columns = ['Abteilung', 'Gesamttage', 'Anzahl Anträge']
    
    fig = go.Figure(data=[
        go.Bar(name='Gesamttage', x=dept_data['Abteilung'], y=dept_data['Gesamttage']),
        go.Bar(name='Anzahl Anträge', x=dept_data['Abteilung'], y=dept_data['Anzahl Anträge'])
    ])
    
    fig.update_layout(barmode='group',
                     title='Urlaubsverteilung nach Abteilungen')
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def analyze_peak_periods(df):
    """Identifiziert Spitzenzeiten im Urlaubskalender"""
    if df.empty:
        return None
    
    # Erstelle Zeitreihe mit täglichen Urlaubsnehmern
    date_range = pd.date_range(start=df['start_date'].min(),
                             end=df['end_date'].max())
    daily_counts = pd.Series(0, index=date_range)
    
    for _, row in df.iterrows():
        dates = pd.date_range(start=row['start_date'],
                            end=row['end_date'])
        daily_counts[dates] += 1
    
    fig = px.line(daily_counts,
                  labels={'index': 'Datum', 'value': 'Anzahl Urlauber'},
                  title='Tägliche Urlauber im Jahresverlauf')
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def analyze_employee_distribution(df):
    """Analysiert die Urlaubsverteilung pro Mitarbeiter"""
    if df.empty:
        return None
    
    emp_data = df.groupby(['employee_name', 'department'])['days'].sum().reset_index()
    
    fig = px.bar(emp_data,
                 x='employee_name',
                 y='days',
                 color='department',
                 labels={'employee_name': 'Mitarbeiter',
                        'days': 'Urlaubstage',
                        'department': 'Abteilung'},
                 title='Urlaubstage pro Mitarbeiter')
    
    fig.update_layout(xaxis_tickangle=-45)
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def generate_pdf_report(year, analyses):
    """Generiert einen PDF-Bericht mit allen Analysen"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    # Definiere Stile
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Erstelle Story (Inhalt)
    story = []
    
    # Titel
    story.append(Paragraph(f'Urlaubsbericht {year}', title_style))
    story.append(Spacer(1, 12))
    
    # Allgemeine Statistiken
    employees = Employee.query.all()
    total_employees = len(employees)
    total_vacation_days = sum(emp.annual_leave_days for emp in employees)
    
    stats_data = [
        ['Statistik', 'Wert'],
        ['Anzahl Mitarbeiter', str(total_employees)],
        ['Gesamte Urlaubstage', str(total_vacation_days)],
    ]
    
    story.append(Paragraph('Allgemeine Statistiken', heading_style))
    story.append(Spacer(1, 12))
    
    stats_table = Table(stats_data)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Füge Analysen hinzu
    for title, html in analyses.items():
        if html:
            story.append(Paragraph(title.replace('_', ' ').title(), heading_style))
            story.append(Spacer(1, 12))
            
            # Konvertiere Plotly HTML zu Bild
            img_path = os.path.join(current_app.config['EXPORT_FOLDER'],
                                  f'{title}_{year}.png')
            
            # Füge Bild hinzu wenn es existiert
            if os.path.exists(img_path):
                img = Image(img_path)
                img.drawHeight = 4*inch
                img.drawWidth = 6*inch
                story.append(img)
                story.append(Spacer(1, 12))
    
    # Generiere PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_department_report(department, year):
    """Generiert einen detaillierten Abteilungsbericht"""
    # Hole alle Mitarbeiter der Abteilung
    employees = Employee.query.filter_by(department=department).all()
    
    # Hole alle Urlaubsanträge der Abteilung
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()
    
    data = []
    for employee in employees:
        vacation_days = 0
        approved_requests = []
        
        for request in employee.vacation_requests:
            if (request.start_date.year == year and
                request.status == 'approved'):
                days = (request.end_date - request.start_date).days + 1
                vacation_days += days
                approved_requests.append(request)
        
        data.append({
            'employee': employee,
            'total_days': employee.annual_leave_days + employee.carried_over_days,
            'used_days': vacation_days,
            'remaining_days': (employee.annual_leave_days +
                             employee.carried_over_days - vacation_days),
            'requests': approved_requests
        })
    
    return data

def generate_employee_report(employee, year):
    """Generiert einen detaillierten Mitarbeiterbericht"""
    start_date = datetime(year, 1, 1).date()
    end_date = datetime(year, 12, 31).date()
    
    # Sammle alle Urlaubsanträge
    requests = VacationRequest.query.filter(
        VacationRequest.employee_id == employee.id,
        VacationRequest.start_date >= start_date,
        VacationRequest.end_date <= end_date
    ).order_by(VacationRequest.start_date).all()
    
    # Analysiere Urlaubstage
    total_days = employee.annual_leave_days + employee.carried_over_days
    used_days = sum((req.end_date - req.start_date).days + 1
                   for req in requests if req.status == 'approved')
    remaining_days = total_days - used_days
    
    # Analysiere Verteilung nach Monaten
    monthly_distribution = {i: 0 for i in range(1, 13)}
    for request in requests:
        if request.status == 'approved':
            current_date = request.start_date
            while current_date <= request.end_date:
                monthly_distribution[current_date.month] += 1
                current_date += timedelta(days=1)
    
    return {
        'employee': employee,
        'total_days': total_days,
        'used_days': used_days,
        'remaining_days': remaining_days,
        'requests': requests,
        'monthly_distribution': monthly_distribution
    }
