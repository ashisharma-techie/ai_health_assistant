import requests
import json

API_KEY = "prism_live_jOhiuyUGipCcHCnnRHPpaEiCbc_9YRhGU_awGI4Lujk"
PROCESS_ID = "cmtzo3mdz000b3mmjuwkwdmms"
BASE_URL = "https://api.prismrun.ai/api/chat"
HEADERS = {"Authorization": f"Bearer {prism_live_jOhiuyUGipCcHCnnRHPpaEiCbc_9YRhGU_awGI4Lujk}", "Content-Type": "application/json"}

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