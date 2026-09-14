import streamlit as st

st.title("AI Health Assistant")

tab1, tab2, tab3 = st.tabs(["Symptom Checker", "Reminders", "Doctor Finder"])

with tab1:
    st.subheader("Describe your symptom")
    user_input = st.text_area("What's bothering you?")
    if st.button("Check Symptom"):
        st.write("This is where the AI response will appear.")

with tab2:
    st.subheader("Medicine Reminders")
    st.write("Coming soon")

with tab3:
    st.subheader("Find Nearby Doctors")
    st.write("Coming soon")