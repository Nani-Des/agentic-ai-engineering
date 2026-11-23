"""
A chat UI for the agent API.

Run:  streamlit run ui_streamlit.py
Set API_URL (default http://localhost:8000) and APP_API_KEY (default dev-key) if they differ.
"""
import os
import uuid

import httpx
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("APP_API_KEY", "dev-key")

st.set_page_config(page_title="Bank Assistant", page_icon="💬")
st.title("Bank & Telco Assistant")
st.caption("Course demo. All data is fake.")

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:8]
    st.session_state.history = []

for role, text in st.session_state.history:
    st.chat_message(role).write(text)

if prompt := st.chat_input("Ask about balances, bundles, currency or FAQs"):
    st.chat_message("user").write(prompt)
    st.session_state.history.append(("user", prompt))
    try:
        r = httpx.post(f"{API_URL}/chat", json={"message": prompt, "session_id": st.session_state.session_id},
                       headers={"X-API-Key": API_KEY}, timeout=60)
        r.raise_for_status()
        data = r.json()
        reply = data["answer"]
        st.chat_message("assistant").write(reply)
        st.caption(f"tools: {', '.join(data['tools_used']) or 'none'} · {data['latency_ms']} ms · {data['tokens']} tokens")
    except httpx.HTTPStatusError as e:
        reply = f"Error {e.response.status_code}: {e.response.json().get('detail')}"
        st.error(reply)
    except Exception as e:
        reply = f"Could not reach the API at {API_URL}: {e}"
        st.error(reply)
    st.session_state.history.append(("assistant", reply))
