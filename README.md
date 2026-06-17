# Todo-Listen-Verwaltung REST-API

Dieses Projekt ist eine einfache REST-API zur Verwaltung von Todo-Listen und Todo-Einträgen.
Die API wurde mit Python und Flask umgesetzt und mit einer OpenAPI-Spezifikation dokumentiert.

## Inhalt des Repositorys

| Datei | Zweck |
|---|---|
| `openapi.yaml` | Beschreibung der REST-API nach OpenAPI |
| `app.py` | Flask-Server mit allen Endpunkten |
| `Dockerfile` | Start der Anwendung in einem Docker-Container |
| `README.md` | Erklärung, Startanleitung und Testablauf |

## Was die API kann

- Alle Todo-Listen abrufen
- Neue Todo-Liste erstellen
- Alle Einträge einer bestimmten Todo-Liste abrufen
- Neue Einträge zu einer Todo-Liste hinzufügen
- Bestehende Einträge aktualisieren
- Einzelne Einträge löschen
- Ganze Todo-Listen löschen

Die Daten werden nur während der Laufzeit gespeichert. Nach einem Neustart des Servers werden wieder nur die Beispiel-Daten geladen.

## Voraussetzungen ohne Docker

- Python 3
- Flask

Flask installieren:

```bash
python -m pip install flask
```

Server starten:

```bash
python app.py
```

Danach läuft der Server unter:

```text
http://127.0.0.1:5000
```

## Start mit Docker

Docker-Image bauen:

```bash
docker build -t todo-api .
```

Container starten:

```bash
docker run -p 5000:5000 todo-api
```

Danach läuft der Server ebenfalls unter:

```text
http://127.0.0.1:5000
```

## Endpunkte

| Methode | Endpunkt | Bedeutung |
|---|---|---|
| GET | `/todo-list` | Alle Todo-Listen abrufen |
| POST | `/todo-list` | Neue Todo-Liste erstellen |
| GET | `/todo-list/{list_id}` | Alle Einträge einer Todo-Liste abrufen |
| POST | `/todo-list/{list_id}` | Neuen Eintrag zu einer Todo-Liste hinzufügen |
| DELETE | `/todo-list/{list_id}` | Todo-Liste mit Einträgen löschen |
| PATCH | `/todo-list/entry/{entry_id}` | Einzelnen Eintrag aktualisieren |
| DELETE | `/todo-list/entry/{entry_id}` | Einzelnen Eintrag löschen |

## Testablauf für die Abgabe

### 1. Server starten

```bash
python app.py
```

### 2. Alle Listen abrufen

```bash
curl http://127.0.0.1:5000/todo-list
```

Erwartung: Es kommt eine JSON-Liste mit Beispiel-Listen zurück.

### 3. Neue Liste erstellen

```bash
curl -X POST http://127.0.0.1:5000/todo-list \
  -H "Content-Type: application/json" \
  -d '{"name":"Schule"}'
```

Erwartung: Statuscode `201` und eine neue Liste mit UUID.
Kopiere dir die zurückgegebene `id`. Diese ID brauchst du im nächsten Schritt als `list_id`.

### 4. Einträge einer Liste abrufen

```bash
curl http://127.0.0.1:5000/todo-list/DEINE_LIST_ID
```

Ersetze `DEINE_LIST_ID` durch die ID aus Schritt 3.

Erwartung: Eine JSON-Liste mit den Einträgen dieser Liste. Bei einer neuen Liste ist sie zuerst leer.

### 5. Eintrag zu einer Liste hinzufügen

```bash
curl -X POST http://127.0.0.1:5000/todo-list/DEINE_LIST_ID \
  -H "Content-Type: application/json" \
  -d '{"name":"README prüfen","description":"Vor der Abgabe testen"}'
```

Erwartung: Statuscode `201` und ein neuer Eintrag mit UUID.
Kopiere dir die zurückgegebene `id`. Diese ID brauchst du im nächsten Schritt als `entry_id`.

### 6. Eintrag aktualisieren

```bash
curl -X PATCH http://127.0.0.1:5000/todo-list/entry/DEINE_ENTRY_ID \
  -H "Content-Type: application/json" \
  -d '{"description":"Erfolgreich getestet"}'
```

Erwartung: Statuscode `200` und der aktualisierte Eintrag.

### 7. Eintrag löschen

```bash
curl -X DELETE http://127.0.0.1:5000/todo-list/entry/DEINE_ENTRY_ID
```

Erwartung: Statuscode `204`. Es wird kein Inhalt zurückgegeben.

### 8. Todo-Liste löschen

```bash
curl -X DELETE http://127.0.0.1:5000/todo-list/DEINE_LIST_ID
```

Erwartung: Statuscode `204`. Die Liste und ihre Einträge wurden gelöscht.

### 9. Fehlerfall testen

```bash
curl http://127.0.0.1:5000/todo-list/falsche-id
```

Erwartung: Statuscode `404` mit einer Fehlermeldung als JSON.

## OpenAPI testen

Die Datei `openapi.yaml` kann im Swagger Editor geöffnet werden.
Dort kann geprüft werden, ob die API-Dokumentation korrekt geladen wird.

## Noch einzutragende persönliche Daten

Bitte vor der Abgabe prüfen:

- In `openapi.yaml`: `DEINE_EMAIL_HIER_EINTRAGEN@example.com` durch deine E-Mail-Adresse ersetzen.
- In GitHub: Repository öffentlich sichtbar machen.
- Abgabe: GitHub-Link an die Lehrkraft senden.

Beispiel für den Repository-Link:

```text
https://github.com/DEIN_USERNAME/DEIN_REPO
```
