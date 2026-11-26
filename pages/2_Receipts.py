from datetime import date

import streamlit as st
from lib.receipts import (
    get_receipts_for_student,
    make_monthly_report_pdf,
    make_receipt_pdf,
    monthly_summary,
)

user = st.session_state.get("user")
if user is None:
    st.warning("Please log in on the main page first.")
    st.stop()

st.title("Receipts")

receipts = get_receipts_for_student(user["id"])
st.subheader("Monthly report")
today = date.today()
month = st.selectbox("Month", list(range(1, 13)), index=today.month - 1)
year = int(st.number_input("Year", min_value=2024, max_value=2100, value=today.year, step=1))
totals = monthly_summary(receipts, year, month)
st.write(f"Rides: {totals['rides']} | Total: NGN {totals['total']:.2f}")
st.download_button(
    "Download monthly report (PDF)",
    data=make_monthly_report_pdf(user["full_name"], year, month, receipts),
    file_name=f"farego_report_{year}_{month:02d}.pdf",
    mime="application/pdf",
)
st.divider()

if not receipts:
    st.info("No receipts yet. They appear after you pay a fare.")

for r in receipts:
    st.write(f"{r['receipt_no']} | NGN {r['amount']} | {r['driver_name']} | {r['created_at']}")
    st.download_button(
        "Download PDF",
        data=make_receipt_pdf(r),
        file_name=f"{r['receipt_no']}.pdf",
        mime="application/pdf",
        key=r["receipt_no"],
    )