# Monthly Budget Calculator

A web app for planning and tracking monthly finances with **Flask** + **TinyDB**.

## What this build includes

- Full monthly budget sheet matching your template sections
- Month selector (`YYYY-MM`) with automatic month record creation
- Persistent storage to `data/budget.json`
- Save/update budget values per month
- Auto-calculated totals for:
  - Pre-tax income
  - Post-tax take-home pay
  - Responsible spending
  - Bonus spending
  - Savings
  - Irresponsible spending
  - Monthly buffer

## Project layout

```text
.
├── app.py
├── data/
│   └── budget.json
├── requirements.txt
├── src/
│   ├── config.py
│   └── db.py
├── static/
│   ├── css/styles.css
│   └── js/main.js
└── templates/
    ├── base.html
    └── index.html
```

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Next step ideas

- Add charts/history trends by month
- Export monthly budget to CSV/PDF
- Add auth/login for multi-user support
