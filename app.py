from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from db import init_db
from login import render_login_gate

import profile as profile_tab
import symptom_checker
import medicine_reminder
import doctors

st.set_page_config(page_title="AI Health Assistant", page_icon="🏥", layout="centered")

init_db()

# Login gate
if not render_login_gate():
    st.stop()

st.title("🏥 AI Health Assistant")
st.caption(f"Logged in as **{st.session_state.username}**")
st.caption("Triage & guidance tool — not a diagnostic tool. Always see a real doctor for anything serious.")

tab1, tab2, tab3, tab4 = st.tabs([
    "🩺 Symptom Checker",
    "💊 Reminders",
    "🏥 Doctors",
    "👤 Profile"
])

with tab1:
    symptom_checker.render_tab()

with tab2:
    medicine_reminder.medicine_reminder_tab()

with tab3:
    doctors.render_tab()

with tab4:
    profile_tab.render_tab()