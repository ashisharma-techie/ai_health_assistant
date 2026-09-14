
import os
import requests
import json
import streamlit as st

# --- API key: moved out of the source code ---
# Reads from an environment variable first, then from Streamlit secrets
# (needed for when this gets deployed on Streamlit Community Cloud later).
# See the note at the bottom of this message for how to set this up —
# do this BEFORE pushing this file to GitHub.
def _get_api_key():
    key = os.environ.get("PRISM_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("PRISM_API_KEY", "")
    except Exception:
        return ""  # no secrets.toml file at all — fine, just means no key set that way


API_KEY = _get_api_key()

PROCESS_ID = "cmtzo3mdz000b3mmjuwkwdmms"
BASE_URL = "https://api.prismrun.ai/api/chat"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def start_run():
    """Step 1: Start a new session with the Symptom Checker process."""
    response = requests.post(
        f"{BASE_URL}/run-process",
        headers=HEADERS,
        json={"processId": PROCESS_ID, "model": "gpt-5.1 (non reasoning)", "resourceIds": []}
    )
    return response.json()["runId"]


def send_message(run_id, message):
    """Step 2: Send the user's symptom message."""
    requests.post(
        f"{BASE_URL}/send",
        headers=HEADERS,
        json={"runId": run_id, "message": message, "model": "gpt-5.1 (non reasoning)", "resourceIds": []}
    )


def get_ai_reply(run_id):
    """Step 3: Read the streaming response and extract the final AI reply."""
    url = f"{BASE_URL}/stream"
    params = {"runId": run_id}
    latest_message = ""
    with requests.get(url, headers=HEADERS, params=params, stream=True) as r:
        for line in r.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if decoded.startswith("data:"):
                decoded = decoded[len("data:"):].strip()
            try:
                data = json.loads(decoded)
            except json.JSONDecodeError:
                continue
            if data.get("type") == "messages-update":
                messages = data.get("messages", [])
                for msg in messages:
                    if msg.get("role") == "assistant":
                        latest_message = msg.get("content", latest_message)
            if data.get("type") == "status-update" and data.get("status") == "COMPLETED":
                break
    return latest_message


def get_symptom_advice(user_message):
    """Full flow: run all 3 steps and return the AI's advice."""
    run_id = start_run()
    send_message(run_id, user_message)
    return get_ai_reply(run_id)


# ---------- NEW: the Streamlit UI, this is what app.py calls ----------

def render_tab():
    st.header("🩺 Symptom Checker")
    st.caption(
        "Describe how you're feeling in plain language. This tool gives general "
        "guidance only — it does not diagnose. Always see a real doctor for anything serious."
    )

    if not API_KEY:
        st.error("PRISM_API_KEY not found. Set it as an environment variable or in Streamlit secrets.")
        return

    symptoms = st.text_area(
        "What symptoms are you experiencing?",
        placeholder="e.g. sore throat, mild fever since yesterday, headache",
        height=100,
    )

    if st.button("Check symptoms", type="primary", disabled=not symptoms.strip()):
        with st.spinner("Checking with AI..."):
            try:
                advice = get_symptom_advice(symptoms)
            except Exception as e:
                st.error(f"Something went wrong talking to Prism: {e}")
                return

        if not advice:
            st.warning("No response came back — try again in a moment.")
        else:
            st.markdown(advice)

        st.caption("⚠️ This is not a medical diagnosis. Please consult a doctor for anything serious.")