"""
monitor.py — täglicher Ping gegen china-trade-monthly.
Schreibt neu aufgetauchte Datenpunkte und Revisionen in state/releases.json.
Nach jedem Lauf wird data/china_trade_monthly.csv mit dem aktuellsten Stand aktualisiert.
"""

import csv
import json
import os
import requests
from datetime import datetime, timezone

API_URL    = "https://chinadata.live/api/v2/data/china-trade-monthly"
STATE_FILE = "state/releases.json"
CSV_FILE   = "data/china_trade_monthly.csv"


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


def export_csv(known: dict) -> None:
    os.makedirs("data", exist_ok=True)
    rows = []
    for date in sorted(known.keys()):
        latest = known[date]["revisions"][-1]
        rows.append({
            "date":             date,
            "export_mln_usd":   latest["export"],
            "import_mln_usd":   latest["import"],
            "balance_mln_usd":  latest["balance"],
            "total_mln_usd":    latest["total"],
        })
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "export_mln_usd", "import_mln_usd", "balance_mln_usd", "total_mln_usd"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV aktualisiert: {CSV_FILE} ({len(rows)} Monate)")


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
            log.append(f"NEU       {date}  balance={float(point['balance']):>12,.2f}  (first seen {checked})")

        else:
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
                log.append(f"REVISION  {date}  balance={float(point['balance']):>12,.2f}  (revision #{len(known[date]['revisions'])})")

    state["last_checked"] = checked
    state["data_points"]  = known
    save_state(state)
    export_csv(known)

    if log:
        print("Änderungen erkannt:")
        for line in log:
            print(f"  {line}")
    else:
        print(f"Keine neuen Daten. Geprüft: {checked}")

    print(f"Gesamt bekannte Monate: {len(known)}")


if __name__ == "__main__":
    main()
