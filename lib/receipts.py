from lib.db import query


def get_receipts_for_student(student_id):
    return query(
        "SELECT r.receipt_no, r.created_at, t.amount, "
        "u.full_name AS driver_name, d.bus_number "
        "FROM receipts r "
        "JOIN transactions t ON t.id = r.transaction_id "
        "JOIN drivers d ON d.id = t.payee_driver_id "
        "JOIN users u ON u.id = d.user_id "
        "WHERE t.payer_user_id = %s "
        "ORDER BY r.created_at DESC",
        (student_id,),
    )