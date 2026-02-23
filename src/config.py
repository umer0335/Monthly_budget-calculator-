from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_DIR / "data" / "budget.json"
    SECRET_KEY = "replace-me-in-production"
