# Urlaubsplaner

Ein webbasiertes System zur Verwaltung von Urlaubsanträgen und Mitarbeiterinformationen.

## Features

- Mitarbeiterverwaltung
- Urlaubsantragstellung und -genehmigung
- Jahresübersicht der Urlaubstage
- Verwaltung von Urlaubskonten
- Vertretungsregelung
- Übersichtlicher Jahreskalender

## Installation

1. Virtuelle Umgebung erstellen:
```bash
python -m venv venv
```

2. Virtuelle Umgebung aktivieren:
```bash
# Windows
venv\Scripts\activate
```

3. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

4. Datenbank initialisieren:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Anwendung starten:
```bash
flask run
```

## Technologien

- Flask (Backend)
- SQLAlchemy (Datenbank)
- Flask-Login (Authentifizierung)
- Bootstrap 4 (Frontend)
