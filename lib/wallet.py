"""Wallet balance, simulated top-up and transaction history (scan-to-pay)."""
from lib.db import query, execute


def get_balance(user_id):
    rows = query("SELECT balance FROM wallets WHERE user_id = %s", (user_id,))
    return float(rows[0]["balance"]) if rows else 0.0


def top_up(user_id, amount):
    """Simulated top-up (demo mode, no real money)."""
    execute(
        "UPDATE wallets SET balance = balance + %s WHERE user_id = %s",
        (amount, user_id),
    )
    # Record it in the history. Check schema.sql: this needs 'topup' to be an
    # allowed transactions.type and payee_driver_id to allow NULL. If your
    # schema differs, adjust here (and tell Person C to ignore type='topup'
    # in the insights).
    try:
        execute(
            "INSERT INTO transactions "
            "(payer_user_id, payee_driver_id, amount, type, flagged_duplicate) "
            "VALUES (%s, NULL, %s, 'topup', 0)",
            (user_id, amount),
        )
    except Exception:
        pass


def student_history(user_id, limit=50):
    return query(
        "SELECT * FROM transactions WHERE payer_user_id = %s ORDER BY id DESC LIMIT %s",
        (user_id, limit),
    )


def driver_history(driver_id, limit=20):
    return query(
        "SELECT * FROM transactions WHERE payee_driver_id = %s ORDER BY id DESC LIMIT %s",
        (driver_id, limit),
    )


# ---------- summaries and nicer tables for the home, wallet and driver pages ----------
def student_summary(user_id):
    """Rides and money spent in the last 7 days."""
    rows = query(
        "SELECT COUNT(*) AS rides, COALESCE(SUM(amount), 0) AS spent FROM transactions "
        "WHERE payer_user_id = %s AND type = 'fare' AND created_at >= NOW() - INTERVAL 7 DAY",
        (user_id,),
    )
    r = rows[0] if rows else {}
    return {"rides": int(r.get("rides") or 0), "spent": float(r.get("spent") or 0)}


def driver_summary(driver_id):
    """Payments received and money earned today."""
    rows = query(
        "SELECT COUNT(*) AS payments, COALESCE(SUM(amount), 0) AS earned FROM transactions "
        "WHERE payee_driver_id = %s AND type = 'fare' AND DATE(created_at) = CURDATE()",
        (driver_id,),
    )
    r = rows[0] if rows else {}
    return {"payments": int(r.get("payments") or 0), "earned": float(r.get("earned") or 0)}


def student_history_table(user_id, limit=50):
    return [
        {
            "Date": r.get("created_at"),
            "Type": "Top-up" if r.get("type") == "topup" else "Ride payment",
            "Amount (NGN)": float(r["amount"]),
            "Note": "Possible duplicate" if r.get("flagged_duplicate") else "",
        }
        for r in student_history(user_id, limit)
    ]


def driver_history_table(driver_id, limit=20):
    rows = query(
        "SELECT t.created_at, t.amount, t.flagged_duplicate, u.full_name "
        "FROM transactions t JOIN users u ON u.id = t.payer_user_id "
        "WHERE t.payee_driver_id = %s ORDER BY t.id DESC LIMIT %s",
        (driver_id, limit),
    )
    return [
        {
            "Date": r.get("created_at"),
            "Student": r.get("full_name"),
            "Amount (NGN)": float(r["amount"]),
            "Note": "Possible duplicate" if r.get("flagged_duplicate") else "",
        }
        for r in rows
    ]