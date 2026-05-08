"""
report.py — wird am 25. Mai ausgeführt.
Liest state/releases.json und schickt einen Report per Mail.
"""

import json
import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

STATE_FILE = "state/releases.json"


def load_state() -> dict:
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)


def build_report(state: dict) -> tuple[str, str]:
    """Gibt (subject, body) zurück."""
    checked  = state.get("last_checked", "?")
    points   = state.get("data_points", {})
    today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        f"CHINA TRADE MONITOR — REPORT",
        f"Erstellt: {today} | Letzter Ping: {checked}",
        "=" * 72,
        "",
        f"Beobachtungszeitraum: {min(points)} bis {max(points)}",
        f"Erfasste Monate: {len(points)}",
        "",
        "─" * 72,
        "RELEASE-ZEITPUNKTE (wann tauchten Daten erstmals in der API auf?)",
        "─" * 72,
        "",
    ]

    total_revisions = 0
    for date in sorted(points):
        dp  = points[date]
        fs  = dp["first_seen"]
        rev = dp["revisions"]
        total_revisions += len(rev) - 1

        lines.append(f"  {date}")
        lines.append(f"    Erstmals gesehen : {fs}")

        # Lag berechnen: Wie viele Tage nach Monatsende?
        try:
            year, month     = map(int, date.split("-"))
            month_end       = datetime(year, month, 28, tzinfo=timezone.utc)  # konservativ
            first_seen_dt   = datetime.strptime(fs, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            lag_days        = (first_seen_dt - month_end).days
            lines.append(f"    Lag ab Monatsende: {lag_days} Tage")
        except Exception:
            lines.append(f"    Lag: nicht berechenbar")

        lines.append(f"    Revisionen       : {len(rev) - 1}")

        for i, r in enumerate(rev):
            label = "Preliminary" if i == 0 else f"Revision {i}"
            lines.append(
                f"      [{label}]  {r['seen_at']}"
                f"  export={r['export']:>12,.2f}"
                f"  import={r['import']:>12,.2f}"
                f"  balance={r['balance']:>12,.2f}"
            )
        lines.append("")

    lines += [
        "─" * 72,
        "ZUSAMMENFASSUNG",
        "─" * 72,
        "",
        f"  Monate mit mindestens einer Revision : {total_revisions}",
    ]

    # Letzte verfügbare Monatsdaten
    last_date = sorted(points)[-1]
    last_rev  = points[last_date]["revisions"][-1]
    lines += [
        f"  Neuester Datenpunkt  : {last_date}",
        f"  Exports (USD Mio.)   : {last_rev['export']:>12,.2f}",
        f"  Imports (USD Mio.)   : {last_rev['import']:>12,.2f}",
        f"  Balance (USD Mio.)   : {last_rev['balance']:>12,.2f}",
        "",
        "Datenquelle: chinadata.live / GACC",
        "Repository : github.com — china-trade-monitor",
    ]

    subject = f"China Trade Monitor — Report {today}"
    body    = "\n".join(lines)
    return subject, body


def send_email(subject: str, body: str) -> None:
    to_addr   = os.environ["EMAIL_TO"]
    from_addr = os.environ["EMAIL_FROM"]
    password  = os.environ["EMAIL_APP_PASSWORD"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = from_addr
    msg["To"]      = to_addr
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_addr, password)
        smtp.sendmail(from_addr, to_addr, msg.as_string())

    print(f"Report gesendet an {to_addr}")


def main() -> None:
    state          = load_state()
    subject, body  = build_report(state)
    print(body)
    send_email(subject, body)


if __name__ == "__main__":
    main()
