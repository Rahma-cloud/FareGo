"""Login, PIN and session helpers (scan-to-pay, Person A).

Uses the existing users table from seed.py: email, password_hash, pin_hash
(both bcrypt) and role.
"""
import bcrypt
import streamlit as st

from lib.db import query


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


# ---------- Streamlit helpers ----------
def login_form():
    st.title("FareGo")
    st.subheader("Log in")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
    if submitted:
        user = authenticate(email.strip().lower(), password)
        if user:
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("Wrong email or password.")


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