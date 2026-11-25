import streamlit as st
from lib.receipts import get_receipts_for_student, make_receipt_pdf

user = st.session_state.get("user")
if user is None:
    st.warning("Please log in on the main page first.")
    st.stop()

st.title("Receipts")

receipts = get_receipts_for_student(user["id"])

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