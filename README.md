# LF9 – Todo-Listen-Verwaltung als REST-API

Dieses Projekt enthält eine REST-API zur Verwaltung von Todo-Listen und Todo-Einträgen. Die API wurde mit Python und Flask umgesetzt und mit einer OpenAPI-Spezifikation dokumentiert. Zusätzlich wird beschrieben, wie die Anwendung auf einer Linux-VM mit Docker bereitgestellt wird.

Repository: `https://github.com/JanHonerkamp/LF9.git`  
Kontakt in der OpenAPI-Spezifikation: `jan.honerkamp@gmx.net`

## Projektdateien

| Datei | Zweck |
|---|---|
| `openapi.yaml` | Beschreibung der REST-Schnittstelle nach OpenAPI |
| `app.py` | Python-Flask-Implementierung der REST-API |
| `Dockerfile` | Bauanleitung für den Docker-Container |
| `README.md` | Installations-, Konfigurations- und Testanleitung |

## Funktion der API

Die Anwendung verwaltet Todo-Listen und Todo-Einträge. Die Daten werden nur im Arbeitsspeicher gehalten. Nach einem Neustart der Anwendung sind neu angelegte Daten wieder zurückgesetzt. Eine Authentifizierung wurde nicht umgesetzt, da sie in der Aufgabenstellung zunächst nicht gefordert ist.

Jede Todo-Liste besitzt:

- eine UUID als ID
- einen Namen

Jeder Todo-Eintrag besitzt:

- eine UUID als ID
- einen Namen
- eine optionale Beschreibung
- die Zuordnung zu einer Todo-Liste über `list_id`

## REST-Endpunkte

| Methode | Endpunkt | Beschreibung | Erfolgsstatus |
|---|---|---|---|
| GET | `/todo-list` | Alle Todo-Listen abrufen | `200` |
| POST | `/todo-list` | Neue Todo-Liste erstellen | `201` |
| GET | `/todo-list/{list_id}` | Einträge einer Todo-Liste abrufen | `200` |
| POST | `/todo-list/{list_id}` | Eintrag zu einer Todo-Liste hinzufügen | `201` |
| DELETE | `/todo-list/{list_id}` | Todo-Liste mit Einträgen löschen | `204` |
| PATCH | `/todo-list/entry/{entry_id}` | Todo-Eintrag ändern | `200` |
| DELETE | `/todo-list/entry/{entry_id}` | Todo-Eintrag löschen | `204` |

Bei falschen IDs gibt die API `404` zurück. Bei ungültigem JSON-Body gibt die API `400` zurück.

## OpenAPI prüfen

Die Datei `openapi.yaml` kann im Swagger Editor geprüft werden:

```text
https://editor.swagger.io/
```

Die Datei wurde erfolgreich importiert und die Endpunkte wurden in der Swagger UI angezeigt.

## Lokaler Start ohne Docker

Flask installieren:

```bash
python -m pip install flask
```

Server starten:

```bash
python app.py
```

Die API läuft lokal unter:

```text
http://127.0.0.1:5000
```

## VM- und Server-Konfiguration

Die VM wurde in VirtualBox im Modus `Netzwerkbrücke` betrieben. Dadurch befindet sich die VM im gleichen lokalen Netzwerk wie der Host-Rechner.

Verwendete Netzwerkdaten:

| Einstellung | Wert |
|---|---|
| Betriebssystem | Ubuntu Server 26.04 LTS |
| Interface | `enp0s3` |
| statische IP | `192.168.52.108/24` |
| Gateway | `192.168.52.1` |
| DNS | `192.168.52.1` |
| Netplan-Datei | `/etc/netplan/00-installer-config.yaml` |

### Statische IP setzen

Vor der Änderung wurde eine Sicherung erstellt:

```bash
sudo cp /etc/netplan/00-installer-config.yaml /etc/netplan/00-installer-config.yaml.bak
```

Die Netplan-Datei wurde bearbeitet:

```bash
sudo nano /etc/netplan/00-installer-config.yaml
```

Inhalt der Datei:

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      match:
        macaddress: 08:00:27:85:da:d6
      set-name: enp0s3
      dhcp4: false
      dhcp6: true
      addresses: [192.168.52.108/24]
      routes:
        - to: default
          via: 192.168.52.1
      nameservers:
        addresses: [192.168.52.1]
```

Die Konfiguration wurde getestet und übernommen:

```bash
sudo netplan try
```

Prüfung der Netzwerkkonfiguration:

```bash
ip -br a
ip route
ping -c 4 192.168.52.1
ping -c 4 github.com
```

## Benutzer einrichten

Es wurden zwei lokale Benutzer eingerichtet beziehungsweise korrigiert.

| Benutzer | Aufgabe | Rechte |
|---|---|---|
| `willi` | normaler lokaler Benutzer | keine sudo-Rechte |
| `fernzugriff` | SSH- und Administrationsbenutzer | sudo-Rechte |

Benutzer `fernzugriff` anlegen und sudo-Rechte vergeben:

```bash
sudo adduser fernzugriff
sudo usermod -aG sudo fernzugriff
groups fernzugriff
```

Benutzer `willi` als normalen Benutzer korrigieren:

```bash
sudo deluser willi sudo
sudo deluser willi adm
sudo deluser willi lxd
id -nG willi
```

Ergebnis der Prüfung:

```text
willi cdrom dip plugdev users
```

Passwörter werden aus Sicherheitsgründen nicht im Repository dokumentiert.

## SSH einrichten

OpenSSH wurde installiert beziehungsweise geprüft und aktiviert:

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh --no-pager
```

Zur Einschränkung des SSH-Zugriffs wurde eine eigene Konfigurationsdatei erstellt:

```bash
sudo tee /etc/ssh/sshd_config.d/99-lf9.conf > /dev/null <<'EOF'
PermitRootLogin no
PasswordAuthentication yes
AllowUsers fernzugriff
EOF
```

Konfiguration prüfen und SSH neu starten:

```bash
sudo sshd -t
sudo systemctl restart ssh
sudo systemctl status ssh --no-pager
```

SSH-Test vom Host-Rechner:

```bash
ssh fernzugriff@192.168.52.108
```

Der Login mit `fernzugriff` war erfolgreich.

## Docker einrichten

Docker war auf der VM installiert und aktiv. Der Status wurde geprüft:

```bash
docker --version
sudo systemctl status docker --no-pager
```

Damit `fernzugriff` Docker ohne `sudo` verwenden kann, wurde der Benutzer der Docker-Gruppe hinzugefügt:

```bash
sudo usermod -aG docker fernzugriff
newgrp docker
docker ps
```

`docker ps` konnte ohne Berechtigungsfehler ausgeführt werden.

## Deployment der Web-App mit Docker

Repository klonen:

```bash
git clone https://github.com/JanHonerkamp/LF9.git
cd LF9
```

Docker-Image bauen:

```bash
docker build -t todo-api .
```

Container starten:

```bash
docker run -d -p 5000:5000 --restart always --name todo-api todo-api
```

Die Option `--restart always` sorgt dafür, dass der Container nach einem Neustart der VM automatisch wieder gestartet wird.

Laufenden Container prüfen:

```bash
docker ps
```

Die Anwendung ist über die VM-IP erreichbar:

```text
http://192.168.52.108:5000
```

## API testen

Alle Todo-Listen abrufen:

```bash
curl -i http://127.0.0.1:5000/todo-list
```

Neue Todo-Liste erstellen:

```bash
curl -i -X POST http://127.0.0.1:5000/todo-list \
  -H "Content-Type: application/json" \
  -d '{"name":"Schule"}'
```

Einträge einer Todo-Liste abrufen:

```bash
curl -i http://127.0.0.1:5000/todo-list/1318d3d1-d979-47e1-a225-dab1751dbe75
```

Eintrag hinzufügen:

```bash
curl -i -X POST http://127.0.0.1:5000/todo-list/DEINE_LIST_ID \
  -H "Content-Type: application/json" \
  -d '{"name":"Projekt testen","description":"API vor der Abgabe pruefen"}'
```

Eintrag ändern:

```bash
curl -i -X PATCH http://127.0.0.1:5000/todo-list/entry/DEINE_ENTRY_ID \
  -H "Content-Type: application/json" \
  -d '{"description":"Test erfolgreich"}'
```

Eintrag löschen:

```bash
curl -i -X DELETE http://127.0.0.1:5000/todo-list/entry/DEINE_ENTRY_ID
```

Todo-Liste löschen:

```bash
curl -i -X DELETE http://127.0.0.1:5000/todo-list/DEINE_LIST_ID
```

Fehlerfall testen:

```bash
curl -i http://127.0.0.1:5000/todo-list/falsche-id
```

## Testprotokoll

| Test | Erwartung | Ergebnis |
|---|---|---|
| OpenAPI im Swagger Editor importieren | Datei wird ohne rote Fehler geladen | OK |
| Server lokal mit Python starten | Server läuft auf Port 5000 | OK |
| `GET /todo-list` | Statuscode `200` | OK |
| `POST /todo-list` | Statuscode `201` | OK |
| `GET /todo-list/{list_id}` | Statuscode `200` | OK |
| `POST /todo-list/{list_id}` | Statuscode `201` | OK |
| `PATCH /todo-list/entry/{entry_id}` | Statuscode `200` | OK |
| `DELETE /todo-list/entry/{entry_id}` | Statuscode `204` | OK |
| `DELETE /todo-list/{list_id}` | Statuscode `204` | OK |
| falsche ID | Statuscode `404` | OK |
| statische IP | VM verwendet `192.168.52.108/24` | OK |
| SSH | Login mit `fernzugriff` funktioniert | OK |
| Docker | Docker-Dienst läuft | OK |

## Abgabe

Für die Abgabe muss das GitHub-Repository die folgenden Dateien enthalten:

```text
openapi.yaml
app.py
Dockerfile
README.md
```

Die Repository-URL für die Abgabe lautet:

```text
https://github.com/JanHonerkamp/LF9.git
```

## Quellen

- OpenAPI Initiative: https://www.openapis.org/
- OpenAPI Specification: https://swagger.io/specification/
- Swagger Editor: https://editor.swagger.io/
- Flask Dokumentation: https://flask.palletsprojects.com/
- Dockerfile Reference: https://docs.docker.com/reference/dockerfile/
