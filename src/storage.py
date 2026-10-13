"""
FinGuard AI - Persistent Storage Engine
Manages SQLite database for transaction evaluation logs, user behavioral
profiles, system metrics, and audit history.
"""

import sys
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

logger = logging.getLogger("FinGuard_Storage")


class DatabaseManager:
    """
    Manages local SQLite database operations for FinGuard AI.
    """

    def __init__(self, db_path: Path = config.DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    from contextlib import contextmanager

    @contextmanager
    def connection(self):
        """Context manager that auto-commits and guarantees connection close."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def get_connection(self):
        return self.connection()

    def init_db(self):
        """Creates required database tables and seeds demo profiles if empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Evaluated Transactions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluated_transactions (
                    transaction_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    merchant_category TEXT,
                    card_network TEXT,
                    ml_probability REAL,
                    ml_risk_score REAL,
                    behavioral_risk_score REAL,
                    contextual_risk_score REAL,
                    dynamic_risk_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    is_cold_start INTEGER DEFAULT 0,
                    factors_json TEXT,
                    raw_details_json TEXT
                )
            """)

            # 2. User Profiles Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    account_name TEXT,
                    total_txns INTEGER DEFAULT 0,
                    avg_amount REAL DEFAULT 0.0,
                    std_amount REAL DEFAULT 0.0,
                    max_amount REAL DEFAULT 0.0,
                    recent_failed_attempts INTEGER DEFAULT 0,
                    account_age_days INTEGER DEFAULT 30,
                    kyc_status TEXT DEFAULT 'fully_verified',
                    default_device TEXT DEFAULT 'trusted_device',
                    default_location TEXT DEFAULT 'home_location',
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            conn.commit()

        # Seed initial demo profiles if empty
        self._seed_demo_data()

    def _seed_demo_data(self):
        """Populates demo user profiles and baseline transactions for out-of-the-box demonstration."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_profiles")
            count = cursor.fetchone()[0]
            if count > 0:
                return  # Already seeded

            now_str = datetime.now().isoformat()

            demo_profiles = [
                (
                    "USER_101",
                    "Sarah Chen (Regular Retail Shopper)",
                    48,
                    45.50,
                    16.20,
                    160.0,
                    0,
                    320,
                    "fully_verified",
                    "trusted_device",
                    "home_location",
                    now_str,
                    now_str,
                ),
                (
                    "USER_202",
                    "Alex Mercer (Suspicious / High Velocity)",
                    22,
                    110.0,
                    42.0,
                    350.0,
                    3,
                    45,
                    "tier_1_verified",
                    "new_device",
                    "domestic_travel",
                    now_str,
                    now_str,
                ),
                (
                    "USER_303",
                    "Liam O'Connor (Brand New Cold Start)",
                    0,
                    0.0,
                    0.0,
                    0.0,
                    0,
                    2,
                    "unverified",
                    "new_device",
                    "home_location",
                    now_str,
                    now_str,
                ),
                (
                    "USER_404",
                    "David Kumar (Commercial Enterprise)",
                    120,
                    450.0,
                    125.0,
                    1800.0,
                    0,
                    540,
                    "fully_verified",
                    "trusted_device",
                    "home_location",
                    now_str,
                    now_str,
                ),
                (
                    "USER_505",
                    "Elena Rostova (Dormant Account)",
                    6,
                    28.0,
                    11.0,
                    65.0,
                    1,
                    210,
                    "fully_verified",
                    "trusted_device",
                    "home_location",
                    now_str,
                    now_str,
                ),
            ]

            cursor.executemany("""
                INSERT INTO user_profiles (
                    user_id, account_name, total_txns, avg_amount, std_amount, max_amount,
                    recent_failed_attempts, account_age_days, kyc_status, default_device,
                    default_location, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, demo_profiles)

            # Pre-seed initial evaluated transactions for dashboard
            base_txns = [
                ("TXN-1001", "2026-10-12 10:15:00", "USER_101", 38.50, "grocery", "visa", 0.04, 4.0, 10.0, 12.0, 8.1, "LOW RISK", "ALLOW", 0, '["Consistent routine grocery transaction", "Recognized device"]'),
                ("TXN-1002", "2026-10-12 11:20:00", "USER_101", 65.00, "retail", "mastercard", 0.08, 8.0, 15.0, 18.0, 13.0, "LOW RISK", "ALLOW", 0, '["Normal retail purchase"]'),
                ("TXN-1003", "2026-10-12 12:05:00", "USER_202", 480.00, "crypto", "visa", 0.74, 74.0, 85.0, 78.0, 78.8, "HIGH RISK", "BLOCK", 0, '["High-risk crypto purchase", "Severe spending surge", "3 failed authentication retries"]'),
                ("TXN-1004", "2026-10-12 13:40:00", "USER_303", 45.00, "retail", "visa", 0.12, 12.0, 35.0, 38.0, 25.4, "LOW RISK", "ALLOW", 1, '["Cold-start initial purchase within normal threshold", "Clean residential IP"]'),
                ("TXN-1005", "2026-10-12 14:10:00", "USER_101", 295.00, "electronics", "visa", 0.28, 28.0, 48.0, 35.0, 36.8, "MEDIUM RISK", "VERIFY", 0, '["Amount 6.4x above user average", "Step-up OTP challenge recommended"]'),
                ("TXN-1006", "2026-10-12 15:25:00", "USER_404", 520.00, "travel_airline", "mastercard", 0.15, 15.0, 18.0, 22.0, 17.8, "LOW RISK", "ALLOW", 0, '["Commercial travel booking within enterprise parameters"]'),
                ("TXN-1007", "2026-10-12 16:00:00", "USER_202", 950.00, "gambling", "visa", 0.88, 88.0, 95.0, 92.0, 91.5, "HIGH RISK", "BLOCK", 0, '["Known online casino gateway", "Impossible velocity", "Tor network detected"]'),
                ("TXN-1008", "2026-10-12 17:15:00", "USER_505", 140.00, "retail", "mastercard", 0.22, 22.0, 52.0, 30.0, 34.5, "MEDIUM RISK", "VERIFY", 0, '["Dormant account reactivation with higher spend", "SMS OTP verification requested"]'),
            ]

            cursor.executemany("""
                INSERT INTO evaluated_transactions (
                    transaction_id, timestamp, user_id, amount, merchant_category, card_network,
                    ml_probability, ml_risk_score, behavioral_risk_score, contextual_risk_score,
                    dynamic_risk_score, risk_level, decision, is_cold_start, factors_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, base_txns)

            conn.commit()
            logger.info("Database successfully initialized and seeded with demo profiles.")

    def save_transaction(self, record: Dict[str, Any]):
        """Persists evaluated transaction record to SQLite."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO evaluated_transactions (
                    transaction_id, timestamp, user_id, amount, merchant_category, card_network,
                    ml_probability, ml_risk_score, behavioral_risk_score, contextual_risk_score,
                    dynamic_risk_score, risk_level, decision, is_cold_start, factors_json, raw_details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record["transaction_id"],
                record["timestamp"],
                record["user_id"],
                record["amount"],
                record.get("merchant_category", "retail"),
                record.get("card_network", "visa"),
                record.get("ml_probability", 0.0),
                record.get("ml_risk_score", 0.0),
                record.get("behavioral_risk_score", 0.0),
                record.get("contextual_risk_score", 0.0),
                record["dynamic_risk_score"],
                record["risk_level"],
                record["decision"],
                1 if record.get("is_cold_start", False) else 0,
                json.dumps(record.get("explanation_factors", [])),
                json.dumps(record.get("raw_details", {})),
            ))
            conn.commit()

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetches user profile by user_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def list_user_profiles(self) -> List[Dict[str, Any]]:
        """Lists all user profiles."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles ORDER BY user_id ASC")
            return [dict(r) for r in cursor.fetchall()]

    def update_user_profile_after_txn(self, user_id: str, amount: float, decision: str):
        """Updates profile counters and stats after transaction approval."""
        if decision == config.DECISION_BLOCK:
            return  # Blocked transactions don't become legitimate spending history

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            now_str = datetime.now().isoformat()

            if row:
                total = row["total_txns"] + 1
                old_avg = row["avg_amount"]
                new_avg = old_avg + (amount - old_avg) / total
                max_amt = max(row["max_amount"], amount)
                cursor.execute("""
                    UPDATE user_profiles
                    SET total_txns = ?, avg_amount = ?, max_amount = ?, updated_at = ?
                    WHERE user_id = ?
                """, (total, round(new_avg, 2), round(max_amt, 2), now_str, user_id))
            else:
                cursor.execute("""
                    INSERT INTO user_profiles (user_id, account_name, total_txns, avg_amount, std_amount, max_amount, created_at, updated_at)
                    VALUES (?, ?, 1, ?, 10.0, ?, ?, ?)
                """, (user_id, f"Account {user_id}", amount, amount, now_str, now_str))

            conn.commit()

    def get_recent_transactions(self, limit: int = 100, risk_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves recently evaluated transactions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if risk_filter and risk_filter != "ALL":
                cursor.execute(
                    "SELECT * FROM evaluated_transactions WHERE risk_level = ? ORDER BY timestamp DESC LIMIT ?",
                    (risk_filter, limit),
                )
            else:
                cursor.execute(
                    "SELECT * FROM evaluated_transactions ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Calculates live KPI metrics for dashboard."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), AVG(dynamic_risk_score) FROM evaluated_transactions")
            total_txns, avg_score = cursor.fetchone()
            total_txns = total_txns or 0
            avg_score = round(avg_score or 0.0, 1)

            cursor.execute("SELECT COUNT(*) FROM evaluated_transactions WHERE decision = ?", (config.DECISION_BLOCK,))
            blocked_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM evaluated_transactions WHERE decision = ?", (config.DECISION_VERIFY,))
            verified_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM evaluated_transactions WHERE decision = ?", (config.DECISION_ALLOW,))
            allowed_count = cursor.fetchone()[0]

            cursor.execute("SELECT risk_level, COUNT(*) FROM evaluated_transactions GROUP BY risk_level")
            distribution = {r[0]: r[1] for r in cursor.fetchall()}

            return {
                "total_transactions": total_txns,
                "average_risk_score": avg_score,
                "blocked_transactions": blocked_count,
                "verified_transactions": verified_count,
                "allowed_transactions": allowed_count,
                "risk_distribution": distribution,
            }


# Singleton
_db_instance = None


def get_database_manager() -> DatabaseManager:
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


if __name__ == "__main__":
    db = get_database_manager()
    print("Database metrics:", db.get_dashboard_metrics())
    print("User profiles count:", len(db.list_user_profiles()))
