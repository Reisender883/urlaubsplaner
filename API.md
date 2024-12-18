# Urlaubsplaner API Dokumentation

## Authentifizierung

Die API verwendet Token-basierte Authentifizierung. Um einen Token zu erhalten, melden Sie sich über die Web-Oberfläche an.
Der Token muss bei allen API-Anfragen im Authorization-Header mitgesendet werden:

```
Authorization: Bearer <your-token>
```

## Endpunkte

### Mitarbeiter

#### GET /api/v1/employees
Listet alle Mitarbeiter auf (nur Admin).

**Response:**
```json
[
  {
    "id": 1,
    "username": "max.mustermann",
    "email": "max@example.com",
    "first_name": "Max",
    "last_name": "Mustermann",
    "department": "IT",
    "annual_leave_days": 30,
    "carried_over_days": 5,
    "is_admin": false,
    "vacation_requests": [...]
  }
]
```

#### GET /api/v1/employees/{id}
Ruft einen einzelnen Mitarbeiter ab.

**Response:**
```json
{
  "id": 1,
  "username": "max.mustermann",
  "email": "max@example.com",
  "first_name": "Max",
  "last_name": "Mustermann",
  "department": "IT",
  "annual_leave_days": 30,
  "carried_over_days": 5,
  "is_admin": false,
  "vacation_requests": [...]
}
```

### Urlaubsanträge

#### GET /api/v1/vacation-requests
Listet alle Urlaubsanträge auf (Admin sieht alle, Mitarbeiter nur eigene).

**Response:**
```json
[
  {
    "id": 1,
    "employee_id": 1,
    "substitute_id": 2,
    "start_date": "2024-07-01",
    "end_date": "2024-07-14",
    "status": "pending",
    "comment": "Sommerurlaub",
    "request_date": "2024-01-15T10:30:00",
    "approved_by": null,
    "employee": {...},
    "substitute": {...}
  }
]
```

#### POST /api/v1/vacation-requests
Erstellt einen neuen Urlaubsantrag.

**Request:**
```json
{
  "start_date": "2024-07-01",
  "end_date": "2024-07-14",
  "substitute_id": 2,
  "comment": "Sommerurlaub"
}
```

#### GET /api/v1/vacation-requests/{id}
Ruft einen einzelnen Urlaubsantrag ab.

**Response:**
```json
{
  "id": 1,
  "employee_id": 1,
  "substitute_id": 2,
  "start_date": "2024-07-01",
  "end_date": "2024-07-14",
  "status": "pending",
  "comment": "Sommerurlaub",
  "request_date": "2024-01-15T10:30:00",
  "approved_by": null,
  "employee": {...},
  "substitute": {...}
}
```

#### PUT /api/v1/vacation-requests/{id}
Aktualisiert einen Urlaubsantrag.

**Request (Admin):**
```json
{
  "status": "approved"
}
```

**Request (Mitarbeiter):**
```json
{
  "comment": "Neuer Kommentar"
}
```

### Abteilungen

#### GET /api/v1/departments/{department}/vacation-requests
Listet alle Urlaubsanträge einer Abteilung auf (nur Admin).

**Response:**
```json
[
  {
    "id": 1,
    "employee_id": 1,
    "substitute_id": 2,
    "start_date": "2024-07-01",
    "end_date": "2024-07-14",
    "status": "pending",
    "comment": "Sommerurlaub",
    "request_date": "2024-01-15T10:30:00",
    "approved_by": null,
    "employee": {...},
    "substitute": {...}
  }
]
```

## Fehlercodes

- 200: Erfolgreiche Anfrage
- 201: Ressource erfolgreich erstellt
- 400: Ungültige Anfrage
- 401: Nicht authentifiziert
- 403: Keine Berechtigung
- 404: Ressource nicht gefunden
- 500: Serverfehler

## Beispiele

### cURL

```bash
# Token abrufen (über Web-Interface)
TOKEN="your-token-here"

# Alle Urlaubsanträge abrufen
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/v1/vacation-requests

# Neuen Urlaubsantrag erstellen
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2024-07-01", "end_date": "2024-07-14", "substitute_id": 2, "comment": "Sommerurlaub"}' \
  http://localhost:5000/api/v1/vacation-requests

# Urlaubsantrag genehmigen (Admin)
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}' \
  http://localhost:5000/api/v1/vacation-requests/1
```
