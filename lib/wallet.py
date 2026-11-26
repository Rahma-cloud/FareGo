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
    # Record it in the history. This needs 'topup' to be an allowed
    # transactions.type and payee_driver_id to allow NULL. If your schema
    # differs, adjust here (and tell Person C to ignore type='topup'
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