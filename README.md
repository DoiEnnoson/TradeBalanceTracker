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
