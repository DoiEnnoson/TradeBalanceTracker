# China Trade Monitor

Verfolgt wann neue Monatsdaten und Revisionen auf chinadata.live erscheinen.

## Setup

1. Repo auf GitHub anlegen
2. Drei Secrets setzen (Settings → Secrets → Actions):

| Secret | Wert |
|---|---|
| `EMAIL_TO` | deine@email.com |
| `EMAIL_FROM` | absender@gmail.com |
| `EMAIL_APP_PASSWORD` | xxxx xxxx xxxx xxxx |

Das App-Passwort: Google-Konto → Sicherheit → App-Passwörter (nur mit aktivem 2FA).

## Was passiert

- **Täglich 12:12 UTC**: `monitor.py` pingt die API, schreibt neue Datenpunkte und Revisionen in `state/releases.json`, committed zurück ins Repo.
- **25. Mai 12:12 UTC**: `report.py` liest den gesamten State und schickt einen Report per Mail.

## Struktur

```
.github/workflows/monitor.yml   Workflow-Definition
monitor.py                      Täglicher Ping
report.py                       Report-Generierung + Mailversand
state/releases.json             Akkumulierter State (committed)
```

## Manuell auslösen

Actions → China Trade Monitor → Run workflow.
