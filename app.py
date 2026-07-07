import streamlit as st
import tempfile
import os
import time
import sqlite3
from src.stt import transcribe, warmup as warmup_stt
from src.tts import speak, warmup as warmup_tts
from src.agent import handle_user_input, warmup as warmup_agent
from src.knowledge_base import warmup as warmup_kb
from src.monitor import get_recent_logs

st.set_page_config(page_title="Voice Agent", layout="wide")

if "warmed_up" not in st.session_state:
    st.title("Starting up...")
    bar = st.progress(0, text="Loading speech-to-text model...")
    warmup_stt()
    bar.progress(25, text="Loading text-to-speech engine...")
    warmup_tts()
    bar.progress(50, text="Connecting to language model...")
    warmup_agent()
    bar.progress(75, text="Loading knowledge base...")
    warmup_kb()
    bar.progress(100, text="Ready!")
    time.sleep(0.3)
    st.session_state.warmed_up = True
    st.rerun()

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
                st.text(f"{i+1}. {log['intent']} ({round(log['latency_ms'])}ms)")
                st.caption(f"Q: {log['transcript'][:50]}...")
                st.caption(f"A: {log['response'][:50]}...")
                if i < len(logs) - 1:
                    st.divider()
        else:
            st.caption("No interactions yet.")

    with st.expander("Available Slots"):
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
    uploaded_file = st.file_uploader("Or upload .wav", type=["wav"], label_visibility="collapsed")

input_source = audio_data or uploaded_file
if input_source and st.button("Process", type="primary", use_container_width=True):
    status = st.status("Processing...", expanded=True)
    status.write("Saving audio...")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(input_source.getvalue() if hasattr(input_source, "getvalue") else input_source.read())
        tmp_path = tmp.name

    status.write("Transcribing speech...")
    transcript = transcribe(tmp_path)

    with st.chat_message("user"):
        st.write(f"🎤 {transcript}")
    st.session_state.messages.append({"role": "user", "content": f"🎤 {transcript}"})

    status.write("Getting response...")
    response = handle_user_input(transcript, use_rag=use_rag)

    status.write("Generating speech...")
    audio_path = speak(response)

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    with st.chat_message("assistant"):
        st.write(response)
        st.audio(audio_bytes)
    st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

    os.unlink(tmp_path)
    os.unlink(audio_path)
    status.update(label="Done!", state="complete", expanded=False)
