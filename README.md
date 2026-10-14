# China Trade Tracker

Monthly dashboard for China's customs data, sourced from the General Administration of Customs China (GACC). Charts load directly from CSV files in this repository — no backend, no API key.

**Live dashboard:** [doiennoson.github.io/TradeBalanceTracker](https://doiennoson.github.io/TradeBalanceTracker)

---

## What it shows

| Section | Description |
|---|---|
| YTD Performance | Year-to-date export and import totals vs. prior year |
| Trade Flows | Monthly exports, imports and trade balance in USD |
| Year-on-Year Growth | Export and import growth rates by month |
| Value per Unit | Export value per metric ton (proxy for product mix) |
| Semiconductors | Integrated circuit exports and imports |
| Trading Partners | Absolute trade volumes by bloc (EU, USA, ASEAN, Russia, BRICS-4) |
| Share by Bloc | Bloc share of total exports and imports, latest month |
| Partner YoY Growth | Year-on-year growth by bloc, latest available month |
| Energy Imports | Crude oil, LNG and coal import volumes |

---

## Data files

All data lives in `data/`. Updated manually after each GACC monthly release (around the 10th of the following month).

### `china_trade_monthly.csv`
Overall trade figures. Coverage: January 2023 onwards.

| Column | Unit |
|---|---|
| date | YYYY-MM |
| export_mln_usd | million USD |
| import_mln_usd | million USD |
| balance_mln_usd | million USD |
| total_mln_usd | million USD |

### `china_trade_monthly_manual.csv`
GACC fallback for the overall trade figures. Same columns as `china_trade_monthly.csv`. Holds only the months the chinadata.live API has not published yet, taken from the GACC monthly release via the `/handelsbilanz` workflow. See [Fallback layer](#fallback-layer).

### `china_trade_partners.csv`
Trade by partner bloc. One row per month, wide format. Coverage: May 2026 onwards.

Partners: EU, USA, ASEAN, Russia, BRICS-4

Column pattern per partner (example: EU):

| Column | Unit |
|---|---|
| eu_export_mln_usd | million USD |
| eu_import_mln_usd | million USD |
| eu_export_share_pct | percent of total exports |
| eu_import_share_pct | percent of total imports |
| eu_export_yoy_pct | year-on-year growth, percent |
| eu_import_yoy_pct | year-on-year growth, percent |

YoY columns are left blank when GACC does not publish the figure explicitly.

### `china_trade_commodities.csv`
Key goods. Coverage: May 2026 onwards.

| Column | Unit |
|---|---|
| date | YYYY-MM |
| ic_export_mln_usd | integrated circuits, million USD |
| ic_import_mln_usd | integrated circuits, million USD |
| crude_oil_import_mln_t | million metric tons |
| crude_oil_import_mln_usd | million USD |
| nev_export_units | units |
| nev_export_mln_usd | million USD |
| hightech_export_mln_usd | million USD |

### `china_trade_freight.csv`
Physical trade volume (weight). Coverage: May 2026 onwards.

| Column | Unit |
|---|---|
| date | YYYY-MM |
| export_mln_t | million metric tons |
| import_mln_t | million metric tons |
| total_mln_t | million metric tons |

---

## Fallback layer

The dashboard draws on two data layers with different update cadences:

1. **API layer** — `china_trade_monthly.csv`, written by `monitor.py` from the chinadata.live API. Feeds the top-line charts (YTD, Trade Flows, Year-on-Year, Value per Unit, bloc-share totals).
2. **Manual GACC layer** — written after each GACC release by the `/handelsbilanz` workflow: `china_trade_partners.csv`, `china_trade_commodities.csv`, `china_trade_freight.csv`, plus the fallback files `china_trade_monthly_manual.csv` (this repo) and `gacc_imports_manual.csv` (in the `china-energy-monitor` repo).

The chinadata.live API usually lags the official GACC release by several days. Without a fallback, every chart bound to `china_trade_monthly.csv` sat a month behind the manual layer the moment the GACC figures were entered, and the bloc-share donuts rendered empty: they look up the latest partner month in the API file and found nothing.

**Resolution (`docs/index.html`):** `mergeMonthly(api, manual)` builds the monthly series as *API primary, manual fallback* — manual rows fill only the months the API does not yet contain, and an existing API month is never overwritten. Once chinadata.live catches up, the API value automatically shadows the manual one. The same pattern feeds the energy charts via `gacc_imports_manual.csv` pulled from the `china-energy-monitor` repo. If neither layer has a given month, the chart renders nothing instead of erroring.

This keeps the dashboard on the freshest GACC data without hardcoding numbers into the page and without manual edits to the API-managed `china_trade_monthly.csv`, which `monitor.py` would overwrite on its next run.

---

## Release monitor

`monitor.py` pings the chinadata.live API daily (12:12 UTC) and writes new release events to `state/releases.json`. `report.py` sends a monthly summary by email.

**GitHub Actions secrets required:**

| Secret | Value |
|---|---|
| `EMAIL_TO` | recipient address |
| `EMAIL_FROM` | sender Gmail address |
| `EMAIL_APP_PASSWORD` | Gmail app password (16 chars, requires 2FA) |

Trigger manually: Actions → China Trade Monitor → Run workflow.

---

## Source

Data: [General Administration of Customs China (GACC)](http://www.customs.gov.cn) — monthly press release, Table 4 (partners), Table 5/6 (commodities).

Dashboard by [Dói Ennoson](https://chinabusinessspotlight.substack.com) · China Business Spotlight
