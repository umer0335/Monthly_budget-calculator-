from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from tinydb import Query, TinyDB

DEFAULT_CATEGORIES = [
    {"name": "Housing", "color": "#6F4E37", "icon": "home"},
    {"name": "Food", "color": "#C68B59", "icon": "utensils"},
    {"name": "Transport", "color": "#355C7D", "icon": "car"},
    {"name": "Utilities", "color": "#4E6C50", "icon": "bolt"},
    {"name": "Health", "color": "#9A3B3B", "icon": "heart"},
    {"name": "Savings", "color": "#2E8B57", "icon": "piggy-bank"},
]

BUDGET_FIELD_KEYS = [
    "salary",
    "stock",
    "interest_income_dividends",
    "monthly_401k_contribution",
    "monthly_federal_taxes",
    "monthly_state_taxes",
    "monthly_city_taxes",
    "fun_random",
    "alcohol",
    "ubers",
    "other",
    "rent",
    "groceries",
    "utilities",
    "student_loans",
    "credit_card_debt",
    "robinhood",
    "laundry",
    "car",
    "public_transportation",
    "dog_care",
    "savings_401k",
    "savings_cash",
    "savings_roth_ira",
    "savings_stocks",
    "eating_out_restaurants",
    "travel",
    "gym_fitness",
    "bathhouse",
    "hair",
    "nails",
    "skincare",
    "clothes",
    "coffee",
]


def default_budget_values() -> dict[str, float]:
    return {field: 0.0 for field in BUDGET_FIELD_KEYS}


def parse_float(value: Any) -> float:
    if isinstance(value, (float, int)):
        return float(value)

    cleaned = str(value).replace(",", "").replace("$", "").strip()
    if cleaned == "":
        return 0.0

    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def normalize_budget_values(raw_values: dict[str, Any]) -> dict[str, float]:
    return {field: parse_float(raw_values.get(field, 0)) for field in BUDGET_FIELD_KEYS}


def calculate_budget_summary(values: dict[str, float]) -> dict[str, float]:
    annual_pre_tax_income = (
        values["salary"]
        + values["stock"]
        + values["interest_income_dividends"]
    )
    pre_tax_monthly_income = annual_pre_tax_income / 12
    monthly_taxable_income = pre_tax_monthly_income - values["monthly_401k_contribution"]

    monthly_tax_total = (
        values["monthly_federal_taxes"]
        + values["monthly_state_taxes"]
        + values["monthly_city_taxes"]
    )
    post_tax_monthly_take_home = monthly_taxable_income - monthly_tax_total
    total_annual_take_home = post_tax_monthly_take_home * 12

    total_irresponsible = (
        values["fun_random"]
        + values["alcohol"]
        + values["ubers"]
        + values["other"]
    )

    total_responsible = (
        values["rent"]
        + values["groceries"]
        + values["utilities"]
        + values["student_loans"]
        + values["credit_card_debt"]
        + values["robinhood"]
        + values["laundry"]
        + values["car"]
        + values["public_transportation"]
        + values["dog_care"]
    )

    total_savings = (
        values["savings_401k"]
        + values["savings_cash"]
        + values["savings_roth_ira"]
        + values["savings_stocks"]
    )

    total_bonus_spending = (
        values["eating_out_restaurants"]
        + values["travel"]
        + values["gym_fitness"]
        + values["bathhouse"]
        + values["hair"]
        + values["nails"]
        + values["skincare"]
        + values["clothes"]
        + values["coffee"]
    )

    total_monthly_spending = (
        total_responsible + total_bonus_spending + total_irresponsible + total_savings
    )
    total_expenses = total_responsible + total_bonus_spending + total_irresponsible

    return {
        "annual_pre_tax_income": annual_pre_tax_income,
        "pre_tax_monthly_income": pre_tax_monthly_income,
        "monthly_taxable_income": monthly_taxable_income,
        "monthly_tax_total": monthly_tax_total,
        "post_tax_monthly_take_home": post_tax_monthly_take_home,
        "total_annual_take_home": total_annual_take_home,
        "total_monthly_take_home": post_tax_monthly_take_home,
        "total_irresponsible": total_irresponsible,
        "total_responsible": total_responsible,
        "total_savings": total_savings,
        "total_bonus_spending": total_bonus_spending,
        "total_expenses": total_expenses,
        "total_monthly_spending": total_monthly_spending,
        "monthly_buffer": post_tax_monthly_take_home - total_monthly_spending,
    }


class BudgetDatabase:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._db = TinyDB(self.db_path)
        self.meta = self._db.table("meta")
        self.categories = self._db.table("categories")
        self.transactions = self._db.table("transactions")
        self.monthly_budgets = self._db.table("monthly_budgets")

        self._bootstrap()

    def _bootstrap(self) -> None:
        key = Query()
        if not self.meta.contains(key.key == "initialized"):
            self.categories.insert_multiple(DEFAULT_CATEGORIES)
            self.meta.insert({"key": "initialized", "value": True})

        self.ensure_year_has_months(date.today().year)

    def _default_month_budget(self, month_key: str) -> dict[str, Any]:
        now = datetime.utcnow().isoformat(timespec="seconds")
        return {
            "month": month_key,
            "values": default_budget_values(),
            "created_at": now,
            "updated_at": now,
        }

    def get_or_create_month_budget(self, month_key: str) -> dict[str, Any]:
        query = Query()
        record = self.monthly_budgets.get(query.month == month_key)
        if record:
            return record

        record = self._default_month_budget(month_key)
        self.monthly_budgets.insert(record)
        return record

    def ensure_year_has_months(self, year: int) -> None:
        for month in range(1, 13):
            month_key = f"{year:04d}-{month:02d}"
            self.get_or_create_month_budget(month_key)

    def save_month_budget(self, month_key: str, raw_values: dict[str, Any]) -> dict[str, Any]:
        query = Query()
        now = datetime.utcnow().isoformat(timespec="seconds")
        normalized_values = normalize_budget_values(raw_values)

        existing = self.monthly_budgets.get(query.month == month_key)
        if existing:
            self.monthly_budgets.update(
                {"values": normalized_values, "updated_at": now},
                query.month == month_key,
            )
        else:
            self.monthly_budgets.insert(
                {
                    "month": month_key,
                    "values": normalized_values,
                    "created_at": now,
                    "updated_at": now,
                }
            )

        return self.get_or_create_month_budget(month_key)

    def get_month_budget_view(self, month_key: str) -> dict[str, Any]:
        record = self.get_or_create_month_budget(month_key)
        values = normalize_budget_values(record.get("values", {}))
        summary = calculate_budget_summary(values)

        return {
            "month": month_key,
            "month_label": datetime.strptime(month_key, "%Y-%m").strftime("%B %Y"),
            "values": values,
            "summary": summary,
            "updated_at": record.get("updated_at"),
        }
