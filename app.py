import streamlit as st

from lib.auth import require_login
from lib.style import page_header
from lib.wallet import get_balance

st.set_page_config(page_title="FareGo", page_icon="🚌")

# Shows the shared sign-in form (lib/auth.py) until the user is logged in.
user = require_login()

page_header("FareGo", "Pay your shuttle in seconds.", "🚌")
st.success(f"Welcome, {user['name']} ({user['role']})")
st.metric("Wallet balance", f"₦{get_balance(user['user_id']):,.2f}")

if user["role"] == "student":
    st.page_link("pages/4_Wallet.py", label="Top up my wallet and see my transactions")
    st.info("To pay, scan the QR code on the shuttle with your phone camera.")
else:
    st.page_link("pages/5_Driver.py", label="Open my driver dashboard")