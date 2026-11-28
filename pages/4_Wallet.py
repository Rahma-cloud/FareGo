"""Student: wallet balance, simulated top-up and transaction history."""
import streamlit as st

from lib.auth import require_login
from lib.style import page_header
from lib.wallet import get_balance, top_up, student_history_table

user = require_login("student")

page_header("My wallet", "Top up and track every ride.")


def _do_topup(amount):
    top_up(user["user_id"], amount)
    st.session_state["wallet_msg"] = f"₦{amount:,.0f} added to your wallet (demo mode)."


def _do_custom_topup():
    _do_topup(st.session_state["topup_amount"])


msg = st.session_state.pop("wallet_msg", None)
if msg:
    st.success(msg)

st.metric("Balance", f"₦{get_balance(user['user_id']):,.0f}")

st.markdown("#### Quick top-up")
q1, q2, q3 = st.columns(3)
q1.button("Add ₦500", on_click=_do_topup, args=(500,), use_container_width=True)
q2.button("Add ₦1,000", on_click=_do_topup, args=(1000,), use_container_width=True)
q3.button("Add ₦2,000", on_click=_do_topup, args=(2000,), use_container_width=True)

st.number_input(
    "Or choose your own amount (₦)", min_value=100, max_value=50000, value=1000, step=100,
    key="topup_amount",
)
st.button("Add this amount", type="primary", on_click=_do_custom_topup)

st.markdown("#### My transactions")
rows = student_history_table(user["user_id"])
if rows:
    st.dataframe(rows, hide_index=True)
else:
    st.info("No transactions yet. Top up, then scan a driver's QR code to pay.")