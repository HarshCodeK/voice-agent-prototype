# Voice Agent Prototype

A local browser-based voice agent that simulates a customer service call. You speak (or upload audio), it transcribes your speech, figures out what you want, answers using a small knowledge base or mock business data, and speaks the answer back.

## Why simulate calls in the browser?

Real telephony (Twilio, LiveKit) requires paid phone numbers, carrier registration, and PSTN infrastructure. This prototype proves the AI pipeline works end-to-end first — speech-to-text, intent classification, tool calling, and text-to-speech — before adding telephony plumbing on top. Telephony is just the transport layer; the intelligence is all here.

## Architecture

```
Audio In --> STT (faster-whisper) --> Intent Router (Groq LLM)
                                          |
                    +---------------------+---------------------+
                    |                     |                     |
                    v                     v                     v
              FAQ (RAG)           Order Status           Appointment
           (ChromaDB +        (SQLite lookup)         (SQLite booking)
         sentence-transformers)
                    |                     |                     |
                    +---------------------+---------------------+
                                          |
                                          v
                                  LLM Response (Groq)
                                          |
                                          v
                                  TTS (pyttsx3)
                                          |
                                          v
                                    Audio Out
```

## How to run

1. **Setup** — Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. **Environment** — Copy `.env.example` to `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
   Get a free key at https://console.groq.com

3. **Seed business data** — Creates the mock orders and appointments database:
   ```
   python scripts/seed_data.py
   ```

4. **Build knowledge base** — Embeds FAQ docs into ChromaDB:
   ```
   python -c "from src.knowledge_base import build_knowledge_base; build_knowledge_base()"
   ```

5. **Launch the app**:
   ```
   streamlit run app.py
   ```
   Open http://localhost:8501 in your browser. Record or upload a .wav file to start a conversation.

## Worked example

1. User clicks record and says: "What are your business hours?"
2. Audio is transcribed by faster-whisper → "What are your business hours?"
3. Intent router classifies it as "faq"
4. FAQ knowledge base (ChromaDB + sentence-transformers) retrieves relevant chunks
5. LLM generates: "Our customer service team is available Monday through Friday from 8:00 AM to 8:00 PM EST, and Saturday from 9:00 AM to 5:00 PM EST."
6. pyttsx3 converts the answer to speech and plays it back in the browser

## What I'd add next

- **Real telephony** via Twilio — replace browser mic with an actual phone number
- **Streaming STT/TTS** — faster-whisper with streaming + pyttsx3 streaming for lower latency
- **Interruption handling (barge-in)** — let the user speak over the agent mid-response
- **Multi-turn memory** — use LLM conversation history for follow-up questions
- **Deeper tool integration** — real order database API, calendar sync for appointments
