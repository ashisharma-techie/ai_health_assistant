import streamlit as st
from db import save_profile, get_profile
 
 
def render_tab():
    st.header("👤 Your Profile")
 
    # Shows who's logged in — this is the "display it on my profile dashboard" part
    st.markdown(f"**Logged in as:** {st.session_state.get('username', 'Unknown')}")
    st.divider()
 
    st.caption("This info helps personalize advice from the symptom checker.")
 
    existing = get_profile()
 
    with st.form("profile_form"):
        name = st.text_input(
            "Name",
            value=existing["name"] if existing else ""
        )
        age = st.number_input(
            "Age",
            min_value=0, max_value=120,
            value=existing["age"] if existing else 25
        )
        allergies = st.text_input(
            "Allergies (comma-separated)",
            value=existing["allergies"] if existing else "",
            placeholder="e.g. penicillin, peanuts"
        )
        conditions = st.text_input(
            "Existing conditions (comma-separated)",
            value=existing["conditions"] if existing else "",
            placeholder="e.g. diabetes, asthma"
        )
 
        submitted = st.form_submit_button("Save profile")
 
        if submitted:
            save_profile(name, age, allergies, conditions)
            st.success("Profile saved!")
            st.rerun()
 
    if existing:
        st.divider()
        st.caption(f"Currently saved: {existing['name']}, age {existing['age']}")