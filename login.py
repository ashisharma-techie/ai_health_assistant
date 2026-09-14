import streamlit as st
from db import create_account, verify_login, has_any_account
 
 
def render_login_gate():
    """
    Call this at the very top of app.py, before anything else.
    Returns True once logged in, False while still showing the login screen.
    """
    if st.session_state.get("logged_in"):
        return True
 
    st.title("🏥 AI Health Assistant")
 
    if not has_any_account():
        st.subheader("Create your login")
        st.caption("This is a one-time setup — you'll use these to log in every time you open the app.")
 
        with st.form("create_account_form"):
            username = st.text_input("Choose a username")
            password = st.text_input("Choose a password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account")
 
            if submitted:
                if not username.strip() or not password:
                    st.warning("Please fill in both fields.")
                elif password != confirm:
                    st.warning("Passwords don't match.")
                else:
                    success = create_account(username.strip(), password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username.strip()
                        st.rerun()
                    else:
                        st.error("That username is already taken.")
 
    else:
        st.subheader("Log in")
 
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")
 
            if submitted:
                if verify_login(username.strip(), password):
                    st.session_state.logged_in = True
                    st.session_state.username = username.strip()
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
 
    return False
 