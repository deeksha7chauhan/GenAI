import sqlite3
import os
from datetime import datetime
from typing import List, Tuple

from agentic_shop.config import DB_PATH

def _ensure_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                product_id TEXT,
                retailer   TEXT,
                price      REAL,
                seen_at    TEXT
            )
        """)
        conn.commit()

def track_price(product_id: str, retailer: str, price: float):
    _ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO price_history (product_id, retailer, price, seen_at) VALUES (?, ?, ?, ?)",
            (product_id, retailer, price, datetime.utcnow().isoformat())
        )
        conn.commit()

def get_price_history(product_id: str) -> List[Tuple[str, float, str]]:
    _ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        rows = c.execute(
            "SELECT retailer, price, seen_at FROM price_history WHERE product_id = ? ORDER BY seen_at DESC",
            (product_id,)
        ).fetchall()
        return rows
