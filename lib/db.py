import mysql.connector
import streamlit as st

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
        import tomli as tomllib  # older Python (installed from requirements.txt)

def _cfg():
    try:
        return dict(st.secrets["mysql"])
    except Exception:
        # Lets scripts such as seed.py run outside Streamlit (run them from the repo root)
        with open(".streamlit/secrets.toml", "rb") as f:
            return tomllib.load(f)["mysql"]


def get_conn():
    c = _cfg()
    return mysql.connector.connect(
        host=c["host"], port=c["port"], user=c["user"],
        password=c["password"], database=c["database"],
    )


def query(sql, params=None):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        conn.close()


def execute(sql, params=None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_fare():
    rows = query("SELECT setting_value FROM settings WHERE setting_key = 'fare'")
    return float(rows[0]["setting_value"])


def create_payment(student_id, driver_id, amount, flagged_duplicate=False):
    """Moves money, saves the transaction and its receipt row.
    Returns the transaction id, or None if the wallet balance is too low."""
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT balance FROM wallets WHERE user_id = %s FOR UPDATE", (student_id,))
        row = cur.fetchone()
        if row is None or row["balance"] < amount:
            conn.rollback()
            return None
        cur.execute("UPDATE wallets SET balance = balance - %s WHERE user_id = %s", (amount, student_id))
        cur.execute(
            "UPDATE wallets w JOIN drivers d ON d.user_id = w.user_id "
            "SET w.balance = w.balance + %s WHERE d.id = %s",
            (amount, driver_id),
        )
        cur.execute(
            "INSERT INTO transactions (payer_user_id, payee_driver_id, amount, type, flagged_duplicate) "
            "VALUES (%s, %s, %s, 'fare', %s)",
            (student_id, driver_id, amount, 1 if flagged_duplicate else 0),
        )
        tx_id = cur.lastrowid
        cur.execute(
            "INSERT INTO receipts (transaction_id, receipt_no) VALUES (%s, %s)",
            (tx_id, f"FG-{tx_id:06d}"),
        )
        conn.commit()
        return tx_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
