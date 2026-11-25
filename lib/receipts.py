from fpdf import FPDF

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

def make_receipt_pdf(receipt):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "FareGo Receipt", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)
    pdf.set_font("Helvetica", size=12)
    lines = [
        ("Receipt no:", receipt["receipt_no"]),
        ("Date:", receipt["created_at"]),
        ("Amount:", f"NGN {receipt['amount']}"),
        ("Driver:", receipt["driver_name"]),
        ("Bus number:", receipt["bus_number"]),
    ]
    for label, value in lines:
        pdf.cell(50, 10, label)
        pdf.cell(0, 10, str(value), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())

def monthly_summary(payments, year, month):
    month_rows = [
        p for p in payments
        if p["created_at"].year == year and p["created_at"].month == month
    ]
    total = sum(float(p["amount"]) for p in month_rows)
    return {"rides": len(month_rows), "total": total}