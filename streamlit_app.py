import json
import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(page_title="MyTeacher AI", page_icon="🤖", layout="wide")

st.markdown(
    """
<style>
.main { background: linear-gradient(180deg, #0b1020 0%, #121a33 100%); color: #f4f7ff; }
h1, h2, h3, p, label { color: #f4f7ff !important; }
[data-testid="stChatMessage"] { border: 1px solid rgba(255,255,255,0.2); border-radius: 14px; padding: 10px; }
.status-badge { display: inline-block; padding: 6px 10px; border-radius: 999px; margin: 4px 6px 4px 0; background: #243b73; color: #d9e6ff; font-size: 12px; }
.code-card { background: #0e1630; border-radius: 12px; padding: 12px; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🤖 MyTeacher AI Tutor")
st.caption("Chat-style interface with guided workflow signals: thinking, transcribing, extracting, analyzing, creating subgoals.")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.subheader("Input Type")
    input_type = st.selectbox("Choose source", ["text", "voice", "image"])
    session_id = st.text_input("Session ID", value="student-001")
    voice_url = st.text_input("Voice URL", value="") if input_type == "voice" else ""
    image_url = st.text_input("Image URL", value="") if input_type == "image" else ""

query = st.chat_input("Ask your question...")

if query:
    st.session_state.history.append({"role": "user", "content": query})

    payload = {
        "sessionId": session_id,
        "inputType": input_type,
        "text": query if input_type == "text" else "",
        "audioUrl": voice_url,
        "imageUrl": image_url,
    }

    with st.spinner("Running workflow..."):
        response = requests.post(f"{API_BASE_URL}/workflow/", json=payload, timeout=60)

    if response.ok:
        result = response.json()

        statuses = "".join(
            f'<span class="status-badge">{item["keyword"]}</span>' for item in result.get("statusTrail", [])
        )
        st.markdown(statuses, unsafe_allow_html=True)

        assistant_text = "\n".join(
            [
                "### Normalized Query",
                json.dumps(result.get("normalizedQuery", {}), indent=2),
                "\n### Subgoals",
                json.dumps(result.get("decomposed", {}), indent=2),
            ]
        )
        st.session_state.history.append({"role": "assistant", "content": assistant_text})
    else:
        st.session_state.history.append(
            {
                "role": "assistant",
                "content": f"Request failed ({response.status_code}): {response.text}",
            }
        )

for entry in st.session_state.history:
    with st.chat_message(entry["role"]):
        if entry["role"] == "assistant" and entry["content"].startswith("###"):
            st.markdown('<div class="code-card">', unsafe_allow_html=True)
            st.markdown(entry["content"])
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(entry["content"])
