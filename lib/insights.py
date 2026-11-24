from lib.db import query


def weekly_spending(student_id):
    return query(
        "SELECT YEARWEEK(created_at, 1) AS week, COUNT(*) AS rides, SUM(amount) AS spent "
        "FROM transactions WHERE payer_user_id = %s AND type = 'fare' "
        "GROUP BY YEARWEEK(created_at, 1) ORDER BY week DESC LIMIT 8",
        (student_id,),
    )


def monthly_spending(student_id):
    return query(
        "SELECT CONCAT(YEAR(created_at), '-', LPAD(MONTH(created_at), 2, '0')) AS month, COUNT(*) AS rides, SUM(amount) AS spent "
        "FROM transactions WHERE payer_user_id = %s AND type = 'fare' "
        "GROUP BY CONCAT(YEAR(created_at), '-', LPAD(MONTH(created_at), 2, '0')) ORDER BY month DESC LIMIT 6",
        (student_id,),
    )


def weekly_income(driver_id):
    return query(
        "SELECT YEARWEEK(created_at, 1) AS week, COUNT(*) AS rides, SUM(amount) AS income "
        "FROM transactions WHERE payee_driver_id = %s AND type = 'fare' "
        "GROUP BY YEARWEEK(created_at, 1) ORDER BY week DESC LIMIT 8",
        (driver_id,),
    )
