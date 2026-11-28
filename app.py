import streamlit as st

from lib.auth import require_login
from lib.style import page_header, steps
from lib.wallet import get_balance, student_summary, driver_summary

st.set_page_config(page_title="FareGo", page_icon="🚌")

# Shows the shared Log in / Sign up screen until the user is logged in.
user = require_login()

page_header("FareGo", "Pay your shuttle in seconds.")
st.subheader(f"Welcome, {user['name']}")

if user["role"] == "student":
    st.caption("Student account")
    s = student_summary(user["user_id"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Wallet balance", f"₦{get_balance(user['user_id']):,.0f}")
    c2.metric("Rides this week", s["rides"])
    c3.metric("Spent this week", f"₦{s['spent']:,.0f}")

    st.markdown("#### How it works")
    steps([
        ("Top up", "Add money to your wallet"),
        ("Scan", "Scan the QR code on the shuttle"),
        ("Pay", "Confirm with your 4-digit PIN"),
        ("Done", "Your receipt is created for you"),
    ])
    st.page_link("pages/4_Wallet.py", label="Top up my wallet", icon="💳")
    st.page_link("pages/2_Receipts.py", label="My receipts", icon="🧾")
    st.page_link("pages/3_Insights.py", label="My spending insights", icon="📊")
else:
    st.caption("Driver account")
    d = driver_summary(user["driver_id"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Wallet balance", f"₦{get_balance(user['user_id']):,.0f}")
    c2.metric("Payments today", d["payments"])
    c3.metric("Earned today", f"₦{d['earned']:,.0f}")

    st.markdown("#### How it works")
    steps([
        ("Show your QR", "Stick it on your bus"),
        ("Student scans", "They pay with their PIN"),
        ("You see it", "Payment shows on your dashboard"),
    ])
    st.page_link("pages/5_Driver.py", label="Open my driver dashboard", icon="🚌")
    st.page_link("pages/3_Insights.py", label="My income insights", icon="📊")
    