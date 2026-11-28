"""Student: pay the shuttle driver whose QR code was scanned."""
import streamlit as st

from lib.auth import require_login, verify_pin, user_name
from lib.db import query, get_fare, create_payment
from lib.style import page_header
from lib.wallet import get_balance

# Person C's duplicate check. Open lib/detection.py and make sure the function
# name and the arguments below match it. Until then it never flags anything.
try:
    from lib.detection import check_duplicate
except ImportError:
    def check_duplicate(student_id, driver_id, amount):
        return False

page_header("Pay your shuttle driver", "Scan, confirm with your PIN and ride.", "🚌")

# 1. Remember which driver's QR code was scanned (so it survives the login step)
scanned = st.query_params.get("driver")
if scanned:
    st.session_state["driver_code"] = str(scanned)

# 2. Must be logged in as a student
user = require_login("student")

# 3. Which driver?
driver_code = st.session_state.get("driver_code")
if not driver_code:
    st.info("Scan the QR code on the shuttle to start.")
    st.stop()

driver_rows = query("SELECT * FROM drivers WHERE qr_code = %s", (driver_code,))
if not driver_rows:
    st.error("This QR code is not linked to a driver.")
    st.stop()
driver_id = driver_rows[0]["id"]
driver_name = user_name(driver_rows[0]["user_id"])
if driver_rows[0].get("bus_number"):
    driver_name = f"{driver_name} ({driver_rows[0]['bus_number']})"

fare = get_fare()
balance = get_balance(user["user_id"])

st.subheader(f"Driver: {driver_name}")
col1, col2 = st.columns(2)
col1.metric("Fare", f"₦{fare:,.0f}")
col2.metric("Your balance", f"₦{balance:,.0f}")

# Result of the last payment (shown after the page reloads)
result = st.session_state.pop("pay_result", None)
if result:
    st.success(result)

if balance < fare:
    st.warning("Your balance is too low for this ride.")
    st.page_link("pages/4_Wallet.py", label="Top up your wallet")
    st.stop()


def finish_payment(flagged):
    tx_id = create_payment(user["user_id"], driver_id, fare, flagged_duplicate=flagged)
    st.session_state["dup_pending"] = False
    if tx_id is None:
        st.session_state["pay_result"] = "Payment failed: balance too low."
    else:
        st.session_state["pay_result"] = (
            f"Paid ₦{fare:,.0f} to {driver_name}. Receipt FG-{tx_id:06d}"
        )
    st.rerun()


with st.form("pay_form", clear_on_submit=True):
    pin = st.text_input("Enter your 4-digit PIN", type="password", max_chars=4)
    submitted = st.form_submit_button(f"Pay ₦{fare:,.0f}", type="primary")

if submitted:
    st.session_state["dup_pending"] = False
    if not verify_pin(user["user_id"], pin):
        st.error("Wrong PIN. Try again.")
    elif check_duplicate(user["user_id"], driver_id, fare):
        st.session_state["dup_pending"] = True
    else:
        finish_payment(False)

# Duplicate rule from the PRD: warn only, the student can still continue
if st.session_state.get("dup_pending"):
    st.warning(
        "You just paid this driver the same amount. "
        "Pay again, for example if you are paying for a friend?"
    )
    yes_col, no_col = st.columns(2)
    if yes_col.button("Yes, pay again"):
        finish_payment(True)
    if no_col.button("Cancel"):
        st.session_state["dup_pending"] = False
        st.rerun()