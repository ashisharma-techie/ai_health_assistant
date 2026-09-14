<<<<<<< HEAD
import medicine_reminder
=======
from dotenv import load_dotenv
load_dotenv()  # must run before symptom_checker.py reads PRISM_API_KEY

>>>>>>> 5a17f3880c727c82561fe548c20a5151d1b61959
import streamlit as st
from db import init_db
from login import render_login_gate

import profile as profile_tab
import symptom_checker
# import reminders
# import doctors

st.set_page_config(page_title="AI Health Assistant", page_icon="🏥", layout="centered")

init_db()

# ---- LOGIN GATE: nothing past this point runs until logged in ----
if not render_login_gate():
    st.stop()
# --------------------------------------------------------------

st.title("🏥 AI Health Assistant")
st.caption(f"Logged in as **{st.session_state.username}**")
st.caption("Triage & guidance tool — not a diagnostic tool. Always see a real doctor for anything serious.")

tab1, tab2, tab3, tab4 = st.tabs(["🩺 Symptom Checker", "💊 Reminders", "🏥 Doctors", "👤 Profile"])

with tab1:
    symptom_checker.render_tab()

with tab2:
<<<<<<< HEAD
    medicine_reminder.medicine_reminder_tab()
=======
    st.info("Reminders go here — teammate to call reminders.render_tab()")
    # reminders.render_tab()
>>>>>>> 5a17f3880c727c82561fe548c20a5151d1b61959

with tab3:
    st.info("Doctor finder goes here — teammate to call doctors.render_tab()")
    # doctors.render_tab()

with tab4:
    profile_tab.render_tab()
 