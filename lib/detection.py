from lib.db import query


def check_duplicate(student_id, driver_id, amount, window_seconds=60):
    """True if this student already paid this driver this amount in the last N seconds."""
    rows = query(
        "SELECT COUNT(*) AS n FROM transactions "
        "WHERE payer_user_id = %s AND payee_driver_id = %s AND amount = %s "
        "AND type = 'fare' AND created_at >= NOW() - INTERVAL %s SECOND",
        (student_id, driver_id, amount, window_seconds),
    )
    return rows[0]["n"] > 0
