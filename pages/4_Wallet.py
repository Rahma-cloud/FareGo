"""Student: wallet balance, simulated top-up and transaction history."""
import streamlit as st

from lib.auth import require_login
from lib.wallet import get_balance, top_up, student_history

user = require_login("student")

st.title("My wallet")


def _do_topup():
    amount = st.session_state["topup_amount"]
    top_up(user["user_id"], amount)
    st.session_state["wallet_msg"] = f"₦{amount:,.0f} added to your wallet (demo mode)."


st.number_input(
    "Amount to add (₦)", min_value=100, max_value=50000, value=1000, step=100,
    key="topup_amount",
)
st.button("Add money", type="primary", on_click=_do_topup)

msg = st.session_state.pop("wallet_msg", None)
if msg:
    st.success(msg)

st.metric("Balance", f"₦{get_balance(user['user_id']):,.0f}")

st.subheader("My transactions")
rows = student_history(user["user_id"])
if rows:
    st.dataframe(rows)
else:
    st.info("No transactions yet.")