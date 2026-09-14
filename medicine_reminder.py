import streamlit as st
import sqlite3
from datetime import datetime

# ---------- DATABASE SETUP ----------

def get_connection():
    conn = sqlite3.connect("health_assistant.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# ---------- DATABASE OPERATIONS ----------

def add_reminder(medicine_name, dosage, reminder_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reminders (medicine_name, dosage, reminder_time, created_at) VALUES (?, ?, ?, ?)",
        (medicine_name, dosage, reminder_time, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_all_reminders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, medicine_name, dosage, reminder_time FROM reminders ORDER BY reminder_time")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_reminder(reminder_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()

# ---------- STREAMLIT UI ----------

def medicine_reminder_tab():
    st.header("💊 Medicine Reminders")
    init_db()

    with st.form("add_reminder_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            medicine_name = st.text_input("Medicine Name")
            dosage = st.text_input("Dosage (e.g., 500mg, 1 tablet)")
        with col2:
            reminder_time = st.time_input("Reminder Time")

        submitted = st.form_submit_button("Add Reminder")
        if submitted:
            if medicine_name.strip() == "" or dosage.strip() == "":
                st.warning("Please fill in both medicine name and dosage.")
            else:
                add_reminder(medicine_name, dosage, reminder_time.strftime("%H:%M"))
                st.success(f"Reminder added for {medicine_name} at {reminder_time.strftime('%H:%M')}")

    st.divider()

    st.subheader("Your Reminders")
    reminders = get_all_reminders()

    if not reminders:
        st.info("No reminders yet. Add one above!")
    else:
        for reminder_id, name, dosage, time in reminders:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.write(f"**{name}**")
            col2.write(dosage)
            col3.write(f"⏰ {time}")
            if col4.button("🗑️", key=f"delete_{reminder_id}"):
                delete_reminder(reminder_id)
                st.rerun()


if __name__ == "__main__":
    medicine_reminder_tab()