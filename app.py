import streamlit as st
import tempfile
import os
from src.stt import transcribe
from src.tts import speak
from src.agent import handle_user_input
from src.monitor import get_recent_logs

st.set_page_config(page_title="Voice Agent", layout="wide")
st.title("Voice Agent Prototype")
st.caption("Speak or upload audio — the agent will transcribe, understand, and respond.")

with st.sidebar:
    st.header("Settings")
    use_rag = st.toggle("Use RAG (FAQ Knowledge Base)", value=True,
                        help="ON: answers from FAQ docs. OFF: answers from LLM knowledge only.")

    with st.expander("Recent Logs", expanded=False):
        logs = get_recent_logs(20)
        if logs:
            for i, log in enumerate(logs):
                st.text(f"{i+1}. {log['intent']} ({log['latency_ms']}ms)")
                st.caption(f"Q: {log['transcript'][:60]}...")
                st.caption(f"A: {log['response'][:60]}...")
                if i < len(logs) - 1:
                    st.divider()
        else:
            st.caption("No interactions yet.")

    with st.expander("Available Slots"):
        import sqlite3
        db_path = os.path.join("data", "business.db")
        conn = sqlite3.connect(db_path)
        slots = conn.execute("SELECT date, time, is_booked FROM appointments ORDER BY date, time").fetchall()
        conn.close()
        for s in slots:
            status = "Booked" if s[2] else "Available"
            st.text(f"{s[0]} {s[1]} - {status}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"])

col1, col2 = st.columns([3, 1])
with col1:
    audio_data = st.audio_input("Record your message")
with col2:
    uploaded_file = st.file_uploader("Or upload a .wav file", type=["wav"], label_visibility="collapsed")

input_source = audio_data or uploaded_file
if input_source and st.button("Process", type="primary", use_container_width=True):
    with st.spinner("Processing..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(input_source.getvalue() if hasattr(input_source, "getvalue") else input_source.read())
            tmp_path = tmp.name

        transcript = transcribe(tmp_path)
        st.session_state.messages.append({"role": "user", "content": f"🎤 {transcript}"})
        with st.chat_message("user"):
            st.write(f"🎤 {transcript}")

        response = handle_user_input(transcript, use_rag=use_rag)
        audio_path = speak(response)

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})
        with st.chat_message("assistant"):
            st.write(response)
            st.audio(audio_bytes)

        os.unlink(tmp_path)
        os.unlink(audio_path)

        st.rerun()
