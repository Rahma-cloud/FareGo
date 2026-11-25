from lib.db import query


def weekly_spending(student_id):
    """One row per week (Monday start date), newest first."""
    return query(
        "SELECT DATE_SUB(DATE(created_at), INTERVAL WEEKDAY(created_at) DAY) AS week_start, "
        "COUNT(*) AS rides, SUM(amount) AS spent "
        "FROM transactions WHERE payer_user_id = %s AND type = 'fare' "
        "GROUP BY DATE_SUB(DATE(created_at), INTERVAL WEEKDAY(created_at) DAY) "
        "ORDER BY week_start DESC LIMIT 8",
        (student_id,),
    )


def monthly_spending(student_id):
    """One row per month, labelled like 2026-11, newest first."""
    return query(
        "SELECT CONCAT(YEAR(created_at), '-', LPAD(MONTH(created_at), 2, '0')) AS month, COUNT(*) AS rides, SUM(amount) AS spent "
        "FROM transactions WHERE payer_user_id = %s AND type = 'fare' "
        "GROUP BY CONCAT(YEAR(created_at), '-', LPAD(MONTH(created_at), 2, '0')) ORDER BY month DESC LIMIT 6",
        (student_id,),
    )


def weekly_income(driver_id):
    """One row per week (Monday start date), newest first."""
    return query(
        "SELECT DATE_SUB(DATE(created_at), INTERVAL WEEKDAY(created_at) DAY) AS week_start, "
        "COUNT(*) AS rides, SUM(amount) AS income "
        "FROM transactions WHERE payee_driver_id = %s AND type = 'fare' "
        "GROUP BY DATE_SUB(DATE(created_at), INTERVAL WEEKDAY(created_at) DAY) "
        "ORDER BY week_start DESC LIMIT 8",
        (driver_id,),
    )
