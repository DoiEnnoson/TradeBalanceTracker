"""
monitor.py — täglicher Ping gegen china-trade-monthly.
Schreibt neu aufgetauchte Datenpunkte und Revisionen in state/releases.json.
"""

import json
import os
import requests
from datetime import datetime, timezone

API_URL    = "https://chinadata.live/api/v2/data/china-trade-monthly"
STATE_FILE = "state/releases.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_state() -> dict:
    os.makedirs("state", exist_ok=True)
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"last_checked": None, "data_points": {}}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def fetch() -> list[dict]:
    r = requests.get(API_URL, timeout=20)
    r.raise_for_status()
    return r.json()["data"]["data"]


def fingerprint(point: dict) -> str:
    """Eindeutiger String für einen Datenpunkt — erkennt Revisionen."""
    return f"{point['export']}|{point['import']}|{point['balance']}"


def main() -> None:
    state   = load_state()
    points  = fetch()
    checked = now_iso()
    log     = []

    known: dict = state.get("data_points", {})

    for point in points:
        date = point["date"]
        fp   = fingerprint(point)

        if date not in known:
            # Neuer Monat — erstmals gesehen
            known[date] = {
                "first_seen": checked,
                "revisions": [
                    {
                        "seen_at":  checked,
                        "export":   point["export"],
                        "import":   point["import"],
                        "balance":  point["balance"],
                        "total":    point["total"],
                        "fingerprint": fp,
                    }
                ],
            }
            log.append(f"NEU       {date}  balance={float(point["balance"]):>12,.2f}  (first seen {checked})")

        else:
            # Bekannter Monat — Revision?
            seen_fps = {r["fingerprint"] for r in known[date]["revisions"]}
            if fp not in seen_fps:
                known[date]["revisions"].append(
                    {
                        "seen_at":  checked,
                        "export":   point["export"],
                        "import":   point["import"],
                        "balance":  point["balance"],
                        "total":    point["total"],
                        "fingerprint": fp,
                    }
                )
                log.append(f"REVISION  {date}  balance={float(point["balance"]):>12,.2f}  (revision #{len(known[date]['revisions'])})")

    state["last_checked"] = checked
    state["data_points"]  = known
    save_state(state)

    if log:
        print("Änderungen erkannt:")
        for line in log:
            print(f"  {line}")
    else:
        print(f"Keine neuen Daten. Geprüft: {checked}")

    print(f"Gesamt bekannte Monate: {len(known)}")


if __name__ == "__main__":
    main()
