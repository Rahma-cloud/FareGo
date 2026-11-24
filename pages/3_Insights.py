import pandas as pd
import streamlit as st

from lib.db import query
from lib.insights import weekly_spending, monthly_spending, weekly_income

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
        weekly["week"] = weekly["week"].astype(str)
        monthly["spent"] = monthly["spent"].astype(float)
        st.subheader("Weekly transport spending (₦)")
        st.bar_chart(weekly, x="week", y="spent")
        st.subheader("Monthly transport spending (₦)")
        st.bar_chart(monthly, x="month", y="spent")
else:
    driver = query("SELECT id FROM drivers WHERE user_id = %s", (user["id"],))
    income = pd.DataFrame(weekly_income(driver[0]["id"])) if driver else pd.DataFrame()
    if income.empty:
        st.info("No payments received yet.")
    else:
        income["income"] = income["income"].astype(float)
        income["week"] = income["week"].astype(str)
        st.subheader("Weekly income (₦)")
        st.bar_chart(income, x="week", y="income")
