import streamlit as st
from lib.receipts import make_receipt_pdf

user = st.session_state.get("user")
if user is None:
    st.warning("Please log in on the main page first.")
    st.stop()

st.title("Receipts")

sample = {
    "receipt_no": "FG-000001",
    "created_at": "2026-11-24 12:00",
    "amount": 200,
    "driver_name": "Test Driver",
    "bus_number": "B12",
}

st.download_button(
    "Download sample receipt",
    data=make_receipt_pdf(sample),
    file_name="receipt.pdf",
    mime="application/pdf",
)