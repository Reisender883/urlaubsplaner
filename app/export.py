import os
from datetime import datetime
import xlsxwriter
from flask import current_app

def create_vacation_export(year, department=None):
    """Erstellt eine Excel-Datei mit der Urlaubsübersicht"""
    filename = f'urlaubsplan_{year}_{department or "alle"}.xlsx'
    filepath = os.path.join(current_app.config['EXPORT_FOLDER'], filename)
    
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet('Urlaubsübersicht')
    
    # Formate
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd.mm.yyyy',
        'align': 'center'
    })
    
    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    # Spaltenbreiten
    worksheet.set_column('A:A', 20)  # Name
    worksheet.set_column('B:B', 20)  # Abteilung
    worksheet.set_column('C:C', 15)  # Jahresurlaub
    worksheet.set_column('D:D', 15)  # Resturlaub
    worksheet.set_column('E:E', 15)  # Genommen
    worksheet.set_column('F:F', 15)  # Verbleibend
    worksheet.set_column('G:H', 12)  # Zeiträume
    
    # Überschriften
    headers = [
        'Mitarbeiter',
        'Abteilung',
        'Jahresurlaub',
        'Resturlaub',
        'Genommen',
        'Verbleibend',
        'Von',
        'Bis'
    ]
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    return filepath

def create_department_export(department, start_date, end_date):
    """Erstellt eine Excel-Datei mit der Abteilungsübersicht"""
    filename = f'abteilung_{department}_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.xlsx'
    filepath = os.path.join(current_app.config['EXPORT_FOLDER'], filename)
    
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet('Abteilungsübersicht')
    
    # Formate
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd.mm.yyyy',
        'align': 'center'
    })
    
    # Spaltenbreiten
    worksheet.set_column('A:A', 25)  # Name
    worksheet.set_column('B:B', 15)  # Urlaubstage gesamt
    worksheet.set_column('C:C', 15)  # Genommen
    worksheet.set_column('D:D', 15)  # Verbleibend
    
    # Überschriften
    headers = [
        'Mitarbeiter',
        'Urlaubstage gesamt',
        'Genommen',
        'Verbleibend'
    ]
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    return filepath

def create_personal_export(employee, year):
    """Erstellt eine Excel-Datei mit der persönlichen Urlaubsübersicht"""
    filename = f'urlaub_{employee.username}_{year}.xlsx'
    filepath = os.path.join(current_app.config['EXPORT_FOLDER'], filename)
    
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet('Urlaubsübersicht')
    
    # Formate
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd.mm.yyyy',
        'align': 'center'
    })
    
    # Spaltenbreiten
    worksheet.set_column('A:A', 15)  # Von
    worksheet.set_column('B:B', 15)  # Bis
    worksheet.set_column('C:C', 10)  # Tage
    worksheet.set_column('D:D', 15)  # Status
    worksheet.set_column('E:E', 20)  # Vertretung
    worksheet.set_column('F:F', 30)  # Kommentar
    
    # Überschriften
    headers = [
        'Von',
        'Bis',
        'Tage',
        'Status',
        'Vertretung',
        'Kommentar'
    ]
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    return filepath
