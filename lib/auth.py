"""Login, PIN and session helpers (scan-to-pay, Person A).

Uses the existing users table from seed.py: email, password_hash, pin_hash
(both bcrypt) and role.
"""
import re
import secrets

import bcrypt
import streamlit as st

from lib.db import get_conn, query


# ---------- hashing (bcrypt, same as seed.py) ----------
def hash_secret(secret: str) -> str:
    return bcrypt.hashpw(secret.encode(), bcrypt.gensalt()).decode()


def verify_secret(secret: str, stored: str) -> bool:
    try:
        return bcrypt.checkpw(secret.encode(), stored.encode())
    except (ValueError, AttributeError, TypeError):
        return False


# ---------- users ----------
def display_name(row, fallback="User"):
    for key in ("full_name", "name", "username", "email"):
        if row.get(key):
            return str(row[key])
    return f"{fallback} {row.get('id', '')}".strip()


def user_name(user_id):
    rows = query("SELECT * FROM users WHERE id = %s", (user_id,))
    return display_name(rows[0]) if rows else "Unknown"


def _build_user(row):
    drv = query("SELECT id FROM drivers WHERE user_id = %s", (row["id"],))
    # Keep every column from the users table (id, full_name, email, role...)
    # so other pages can read them, but never keep the password or PIN hashes.
    user = {k: v for k, v in row.items() if k not in ("password_hash", "pin_hash")}
    user.update({
        "user_id": row["id"],
        "name": display_name(row),
        "role": row.get("role") or ("driver" if drv else "student"),
        "driver_id": drv[0]["id"] if drv else None,
    })
    return user


def authenticate(email, password):
    rows = query("SELECT * FROM users WHERE email = %s", (email,))
    if rows and verify_secret(password, rows[0]["password_hash"]):
        return _build_user(rows[0])
    return None


def verify_pin(user_id, pin):
    rows = query("SELECT pin_hash FROM users WHERE id = %s", (user_id,))
    return bool(rows) and verify_secret(pin, rows[0]["pin_hash"])


# ---------- sign up ----------
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def create_account(full_name, email, password, pin, role, bus_number=None):
    """Creates the user, their wallet (and a driver row for drivers) as one
    all-or-nothing step. Returns (user_id, None) or (None, error message)."""
    full_name = (full_name or "").strip()
    email = (email or "").strip().lower()
    if not full_name:
        return None, "Please enter your full name."
    if not _EMAIL_RE.match(email):
        return None, "Please enter a valid email address."
    if len(password or "") < 8:
        return None, "Password must be at least 8 characters."
    if not (len(pin or "") == 4 and pin.isdigit()):
        return None, "PIN must be exactly 4 digits."
    if role not in ("student", "driver"):
        return None, "Please choose student or driver."
    if role == "driver" and not (bus_number or "").strip():
        return None, "Please enter your bus number."
    # Keep within the column sizes in the database
    if len(full_name) > 100:
        return None, "Name is too long (100 characters at most)."
    if len(email) > 120:
        return None, "Email is too long (120 characters at most)."
    if role == "driver" and len(bus_number.strip()) > 20:
        return None, "Bus number is too long (20 characters at most)."

    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchall():
            return None, "An account with this email already exists. Please log in."
        cur.execute(
            "INSERT INTO users (full_name, email, password_hash, pin_hash, role) "
            "VALUES (%s, %s, %s, %s, %s)",
            (full_name, email, hash_secret(password), hash_secret(pin), role),
        )
        user_id = cur.lastrowid
        cur.execute("INSERT INTO wallets (user_id, balance) VALUES (%s, 0)", (user_id,))
        if role == "driver":
            while True:  # random QR code value that is not used yet
                code = f"DRV-{secrets.token_hex(3).upper()}"
                cur.execute("SELECT id FROM drivers WHERE qr_code = %s", (code,))
                if not cur.fetchall():
                    break
            cur.execute(
                "INSERT INTO drivers (user_id, bus_number, qr_code) VALUES (%s, %s, %s)",
                (user_id, bus_number.strip(), code),
            )
        conn.commit()
        return user_id, None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------- Streamlit helpers ----------
def signup_form():
    # The role choice sits outside the form so the bus-number box can appear
    # as soon as "Driver" is picked.
    role = st.radio("I am a...", ["Student", "Driver"], horizontal=True, key="su_role").lower()
    with st.form("signup_form"):
        full_name = st.text_input("Full name", key="su_name")
        email = st.text_input("Email", key="su_email")
        password = st.text_input("Password (at least 8 characters)", type="password", key="su_pw")
        confirm = st.text_input("Confirm password", type="password", key="su_pw2")
        pin = st.text_input(
            "4-digit PIN (used to confirm payments)", type="password", max_chars=4, key="su_pin"
        )
        bus = st.text_input("Bus number (for example BUS-09)", key="su_bus") if role == "driver" else None
        submitted = st.form_submit_button("Create account")
    st.caption("Free to join. Pay your shuttle from your phone, no cash needed.")
    if submitted:
        if password != confirm:
            st.error("The two passwords do not match.")
            return
        user_id, error = create_account(full_name, email, password, pin, role, bus)
        if error:
            st.error(error)
            return
        st.session_state["user"] = authenticate(email.strip().lower(), password)
        st.rerun()


def login_form():
    st.markdown("#### Log in or create an account")
    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pw")
            submitted = st.form_submit_button("Log in")
        if submitted:
            user = authenticate(email.strip().lower(), password)
            if user:
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("Wrong email or password.")
    with tab_signup:
        signup_form()


def _normalize(user):
    """The session may hold a user saved by another page (for example app.py)
    with only the users-table columns (id, full_name, role...). Rebuild it so
    it always has user_id, name, role and driver_id."""
    if all(k in user for k in ("user_id", "name", "role", "driver_id")):
        return user
    uid = user.get("user_id") or user.get("id")
    rows = query("SELECT * FROM users WHERE id = %s", (uid,)) if uid else []
    return _build_user(rows[0]) if rows else None


def require_login(role=None):
    """Call at the top of any page. Returns the logged-in user as a dict:
    {"user_id", "name", "role" ("student" or "driver"), "driver_id"}."""
    user = st.session_state.get("user")
    if user:
        user = _normalize(user)
        st.session_state["user"] = user  # None here means: show the login form
    if not user:
        login_form()
        st.stop()
    with st.sidebar:
        st.write(f"Signed in as **{user['name']}** ({user['role']})")
        if st.button("Log out"):
            st.session_state.pop("user", None)
            st.rerun()
    if role and user["role"] != role:
        st.error(f"This page is for {role}s. You are signed in as a {user['role']}.")
        st.stop()
    return user