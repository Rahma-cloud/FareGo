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


def make_monthly_report_pdf(student_name, year, month, payments, summary_text=None):
    rows = [
        p for p in payments
        if p["created_at"].year == year and p["created_at"].month == month
    ]
    totals = monthly_summary(payments, year, month)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "FareGo Monthly Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 8, f"Student: {student_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Month: {month:02d}/{year}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Total rides: {totals['rides']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Total spent: NGN {totals['total']:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 8, summary_text or "AI summary coming soon.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Rides", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    for p in rows:
        line = f"{p['receipt_no']}   {p['created_at'].strftime('%Y-%m-%d')}   NGN {p['amount']}   {p['driver_name']}"
        pdf.cell(0, 7, line, new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())