import streamlit as st

from lib.auth import require_login
from lib.style import page_header
from lib.db import query   

page_header("Insights", "See where your money goes.", "📊")
user = require_login()

import altair as alt
import pandas as pd

from lib.insights import weekly_spending, monthly_spending, weekly_income


def week_label(df):
    # Data arrives newest-first, so the oldest week gets "Week 1"
    n = len(df)
    return pd.Series([f"Week {n - i}" for i in range(n)], index=df.index)


def week_date(df):
    # 2026-11-23 -> "23 Nov 2026" (shown in the tooltip)
    return pd.to_datetime(df["week_start"]).dt.strftime("%d %b %Y")


def month_label(df):
    # "2026-11" -> "November 2026"
    return pd.to_datetime(df["month"] + "-01").dt.strftime("%B %Y")


def bar(df, label, value, title, extra=None):
    # Oldest on the left, newest on the right
    df = df.iloc[::-1]
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{label}:N", sort=None, title=None),
        y=alt.Y(f"{value}:Q", title=title),
        tooltip=[label, value, "rides"] + (extra or []),
    )
    st.altair_chart(chart)


user = st.session_state.get("user")
if user is None:
    st.warning("Log in on the Home page.")
    st.stop()

st.title("My insights")

if user["role"] == "student":
    weekly = pd.DataFrame(weekly_spending(user["id"]))
    monthly = pd.DataFrame(monthly_spending(user["id"]))
    if weekly.empty:
        st.info("No rides yet.")
    else:
        weekly["spent"] = weekly["spent"].astype(float)
        weekly["label"] = week_label(weekly)
        weekly["starts"] = week_date(weekly)
        monthly["spent"] = monthly["spent"].astype(float)
        monthly["label"] = month_label(monthly)
        st.subheader("Weekly transport spending (₦)")
        bar(weekly, "label", "spent", "Spent (₦)", extra=["starts"])
        st.subheader("Monthly transport spending (₦)")
        bar(monthly, "label", "spent", "Spent (₦)")
else:
    driver = query("SELECT id FROM drivers WHERE user_id = %s", (user["id"],))
    income = pd.DataFrame(weekly_income(driver[0]["id"])) if driver else pd.DataFrame()
    if income.empty:
        st.info("No payments received yet.")
    else:
        income["income"] = income["income"].astype(float)
        income["label"] = week_label(income)
        income["starts"] = week_date(income)
        st.subheader("Weekly income (₦)")
        bar(income, "label", "income", "Income (₦)", extra=["starts"])
