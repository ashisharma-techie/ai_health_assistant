"""
symptom_checker.py — powered by Google's Gemini API (free tier).

Has render_tab() with no arguments, so app.py doesn't need to change.

Setup:
1. Go to aistudio.google.com, sign in with Google, click "Get API key".
2. Add to your .env file:  GEMINI_API_KEY=your-key-here
3. Uses plain `requests` (already installed) — no extra pip install needed.
"""

import os
import json
import re
import requests
import streamlit as st

# If this model name ever 404s, check aistudio.google.com for the current one.
MODEL = "gemini-3.6-flash"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

SYSTEM_PROMPT = """You are a health triage assistant, not a doctor. The user will
describe a symptom or set of symptoms.

Your job:
1. List 2-4 possible general causes (phrased as possibilities, never certainties).
2. Classify urgency as exactly one of: "Mild", "Moderate", "Severe".
   Classify as Severe if there are signs of chest pain, difficulty breathing,
   severe bleeding, sudden confusion, or anything life-threatening.
3. Give advice appropriate to the urgency:
   - Severe: tell the user to seek emergency help immediately, no home remedies.
   - Moderate: general self-care advice + recommend seeing a doctor within 1-2 days.
   - Mild: general self-care tips + monitor for a few days.
4. Always include this exact disclaimer: "This is general guidance, not a medical
   diagnosis. Please consult a doctor for proper care."

Respond ONLY with valid JSON, no preamble, no markdown fences, in exactly this shape:
{
  "possible_causes": ["...", "..."],
  "urgency": "Mild" | "Moderate" | "Severe",
  "advice": "...",
  "disclaimer": "This is general guidance, not a medical diagnosis. Please consult a doctor for proper care."
}
"""


def _get_api_key():
    """Try .env first (local), then Streamlit secrets (cloud)."""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return ""


API_KEY = _get_api_key()


def _parse_response(raw_text: str) -> dict:
    """Strip markdown fences if the model added them, then parse JSON."""
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "possible_causes": ["Could not parse AI response."],
            "urgency": "Moderate",
            "advice": raw_text,
            "disclaimer": "This is general guidance, not a medical diagnosis. Please consult a doctor for proper care.",
        }


def get_symptom_advice(user_message: str) -> dict:
    """Send symptoms to Gemini, get back structured advice."""
    url = f"{BASE_URL}?key={API_KEY}"
    body = {
        "contents": [
            {"role": "user", "parts": [{"text": user_message}]}
        ],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 500,
        },
    }

    response = requests.post(url, json=body, timeout=30)
    if not response.ok:
        raise RuntimeError(f"Gemini API error ({response.status_code}): {response.text}")

    data = response.json()
    try:
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected Gemini response shape: {data}")

    return _parse_response(raw_text)


def render_tab():
    st.header("🩺 Symptom Checker")
    st.caption(
        "Describe how you're feeling in plain language. This tool gives general "
        "guidance only — it does not diagnose. Always see a real doctor for anything serious."
    )

    if not API_KEY:
        st.error("GEMINI_API_KEY not found. Add it to your .env file.")
        return

    symptoms = st.text_area(
        "What symptoms are you experiencing?",
        placeholder="e.g. sore throat, mild fever since yesterday, headache",
        height=100,
    )

    if st.button("Check symptoms", type="primary", disabled=not symptoms.strip()):
        with st.spinner("Checking with AI..."):
            try:
                result = get_symptom_advice(symptoms)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                return

        urgency = result.get("urgency", "Moderate")
        if urgency == "Severe":
            st.error("🚨 **Severe** — seek emergency help immediately.")
        elif urgency == "Moderate":
            st.warning("⚠️ **Moderate** — consider seeing a doctor within 1-2 days.")
        else:
            st.success("🙂 **Mild** — likely manageable at home, monitor for a few days.")

        st.subheader("Possible causes")
        for cause in result.get("possible_causes", []):
            st.markdown(f"- {cause}")

        st.subheader("Advice")
        st.write(result.get("advice", ""))

        st.caption(result.get("disclaimer", "This is general guidance, not a medical diagnosis."))
