from groq import Groq
import os
from dotenv import load_dotenv
from src.config import GROQ_MODEL

load_dotenv()

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

VALID_INTENTS = {"faq", "order_status", "schedule_appointment", "escalate"}

PROMPT_TEMPLATE = """You are an intent classifier for a customer service voice agent.
Classify the user's request into one of these intents:
- faq: general questions about business policies (e.g. "What are your business hours?")
- order_status: checking an existing order (e.g. "Where is my order ORD-1001?")
- schedule_appointment: booking a call or visit (e.g. "I want to book an appointment")
- escalate: anything else you cannot confidently classify

Respond with ONLY the intent name, nothing else.

User: {user_text}
Intent:"""

def classify_intent(user_text: str) -> str:
    client = _get_client()
    prompt = PROMPT_TEMPLATE.format(user_text=user_text)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=10,
    )
    intent = response.choices[0].message.content.strip().lower()
    if intent in VALID_INTENTS:
        return intent
    return "escalate"
