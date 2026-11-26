"""Driver: live payment confirmation, wallet balance, QR sticker, history."""
import streamlit as st

from lib.auth import require_login, user_name
from lib.db import query
from lib.qr import driver_link, qr_png_bytes
from lib.wallet import get_balance, driver_history

user = require_login("driver")
driver_id = user["driver_id"]

st.title("Driver dashboard")

# Only payments that arrive AFTER this page opens trigger the green banner
if "baseline_tx" not in st.session_state:
    last = query(
        "SELECT COALESCE(MAX(id), 0) AS last_id FROM transactions "
        "WHERE payee_driver_id = %s",
        (driver_id,),
    )
    st.session_state["baseline_tx"] = last[0]["last_id"]


@st.fragment(run_every=3)
def live_panel():
    st.metric("Wallet balance", f"₦{get_balance(user['user_id']):,.0f}")

    newest = query(
        "SELECT * FROM transactions WHERE payee_driver_id = %s AND id > %s "
        "ORDER BY id DESC LIMIT 1",
        (driver_id, st.session_state["baseline_tx"]),
    )
    if newest:
        t = newest[0]
        st.success(
            f"PAYMENT RECEIVED: ₦{float(t['amount']):,.0f} "
            f"from {user_name(t['payer_user_id'])}"
        )
    else:
        st.info("Waiting for payments...")

    st.subheader("Recent payments")
    rows = driver_history(driver_id)
    if rows:
        st.dataframe(rows)
    else:
        st.write("No payments yet.")


live_panel()

st.subheader("Your QR sticker")
code_row = query("SELECT qr_code FROM drivers WHERE id = %s", (driver_id,))
link = driver_link(code_row[0]["qr_code"])
png = qr_png_bytes(link)
st.image(png, width=260)
st.caption(link)
st.download_button(
    "Download QR sticker", data=png, file_name=f"driver_{driver_id}.png", mime="image/png"
)