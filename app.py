import bcrypt
import streamlit as st

from lib.db import query

st.set_page_config(page_title="FareGo", page_icon="🚌")
st.title("FareGo")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        rows = query("SELECT * FROM users WHERE email = %s", (email,))
        if rows and bcrypt.checkpw(password.encode(), rows[0]["password_hash"].encode()):
            st.session_state.user = rows[0]
            st.rerun()
        else:
            st.error("Wrong email or password")
else:
    u = st.session_state.user
    st.success(f"Welcome, {u['full_name']} ({u['role']})")
    bal = query("SELECT balance FROM wallets WHERE user_id = %s", (u["id"],))[0]["balance"]
    st.metric("Wallet balance", f"₦{bal:,.2f}")
    if st.button("Log out"):
        st.session_state.user = None
        st.rerun()
