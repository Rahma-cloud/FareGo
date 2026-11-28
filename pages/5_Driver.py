"""Driver: live payment confirmation, earnings, QR sticker and history."""
import streamlit as st

from lib.auth import require_login, user_name
from lib.db import query
from lib.qr import driver_link, qr_png_bytes
from lib.style import page_header
from lib.wallet import get_balance, driver_summary, driver_history_table

user = require_login("driver")
driver_id = user["driver_id"]

page_header("Driver dashboard", "See payments arrive in real time.")

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
    d = driver_summary(driver_id)
    c1, c2, c3 = st.columns(3)
    c1.metric("Wallet balance", f"₦{get_balance(user['user_id']):,.0f}")
    c2.metric("Payments today", d["payments"])
    c3.metric("Earned today", f"₦{d['earned']:,.0f}")

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

    st.markdown("#### Recent payments")
    rows = driver_history_table(driver_id)
    if rows:
        st.dataframe(rows, hide_index=True)
    else:
        st.write("No payments yet.")


live_panel()

st.markdown("#### Your QR sticker")
bus = query("SELECT bus_number, qr_code FROM drivers WHERE id = %s", (driver_id,))[0]
link = driver_link(bus["qr_code"])
png = qr_png_bytes(link)

left, right = st.columns([1, 1.4])
with left:
    st.image(png, width=240)
    st.download_button(
        "Download QR sticker", data=png, file_name=f"driver_{driver_id}.png", mime="image/png"
    )
with right:
    st.write(f"**Bus {bus['bus_number']}**")
    st.write(
        "Print this code and stick it on your bus. Students scan it with their "
        "phone camera, confirm with their PIN, and the payment appears above."
    )
    st.caption(link)