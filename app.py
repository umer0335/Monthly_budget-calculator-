from datetime import date, datetime

from flask import Flask, redirect, render_template, request, url_for

from src.config import Config
from src.db import BUDGET_FIELD_KEYS, BudgetDatabase


def normalize_month_key(raw_month: str | None) -> str:
    fallback = date.today().strftime("%Y-%m")
    if not raw_month:
        return fallback

    try:
        return datetime.strptime(raw_month, "%Y-%m").strftime("%Y-%m")
    except ValueError:
        return fallback


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    budget_db = BudgetDatabase(app.config["DB_PATH"])
    app.extensions["budget_db"] = budget_db

    @app.get("/")
    def dashboard() -> str:
        month_key = normalize_month_key(request.args.get("month"))
        budget_db.ensure_year_has_months(int(month_key[:4]))
        budget = budget_db.get_month_budget_view(month_key)
        summary = budget["summary"]

        income_amount = max(float(summary["total_monthly_take_home"]), 0.0)
        expense_amount = max(float(summary["total_expenses"]), 0.0)
        savings_amount = max(float(summary["total_savings"]), 0.0)
        chart_total = income_amount + expense_amount + savings_amount

        if chart_total > 0:
            income_pct = (income_amount / chart_total) * 100
            expense_pct = (expense_amount / chart_total) * 100
            savings_pct = (savings_amount / chart_total) * 100
        else:
            income_pct = expense_pct = savings_pct = 0.0

        pie_chart = {
            "income_amount": income_amount,
            "expense_amount": expense_amount,
            "savings_amount": savings_amount,
            "income_pct": income_pct,
            "expense_pct": expense_pct,
            "savings_pct": savings_pct,
            "expense_end": income_pct + expense_pct,
            "has_data": chart_total > 0,
        }

        return render_template(
            "index.html",
            budget=budget,
            pie_chart=pie_chart,
            saved=request.args.get("saved") == "1",
        )

    @app.post("/budget")
    def save_budget():
        month_key = normalize_month_key(request.form.get("month"))
        budget_db.ensure_year_has_months(int(month_key[:4]))

        payload = {key: request.form.get(key, "0") for key in BUDGET_FIELD_KEYS}
        budget_db.save_month_budget(month_key, payload)

        return redirect(url_for("dashboard", month=month_key, saved=1))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "app": "monthly-budget-calculator"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
