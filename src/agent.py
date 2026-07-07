import re
import time
import json
from groq import Groq
import os
from dotenv import load_dotenv
from src.config import GROQ_MODEL
from src.intent_router import classify_intent
from src.knowledge_base import retrieve_faq_context
from src.tools import get_order_status, book_appointment
from src.monitor import log_interaction

load_dotenv()

_llm_client = None

def _get_llm():
    global _llm_client
    if _llm_client is None:
        _llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _llm_client

FAQ_PROMPT = """You are a helpful customer service agent. Answer the question using ONLY the context below. If the context doesn't contain the answer, say you don't know.

Context:
{context}

Question: {question}
Answer:"""

DIRECT_PROMPT = """You are a helpful customer service agent. Answer the question conversationally.

Question: {question}
Answer:"""

def _ask_llm(prompt: str) -> str:
    client = _get_llm()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200,
        timeout=30,
    )
    return response.choices[0].message.content.strip()

def _handle_faq(user_text: str, use_rag: bool = True) -> str:
    if use_rag:
        context_chunks = retrieve_faq_context(user_text)
        context = "\n\n".join(context_chunks)
        prompt = FAQ_PROMPT.format(context=context, question=user_text)
    else:
        prompt = DIRECT_PROMPT.format(question=user_text)
    return _ask_llm(prompt)

def _handle_order_status(user_text: str) -> str:
    match = re.search(r"ORD-\d+", user_text)
    if not match:
        return "I'd be happy to check your order status. Could you please provide your order ID?"
    order_id = match.group()
    result = get_order_status(order_id)
    if not result["found"]:
        return f"I couldn't find order {order_id}. Please double-check the order ID."
    return f"Order {order_id} is currently '{result['status']}' and is expected to be delivered on {result['expected_delivery']}."

def _handle_schedule(user_text: str) -> str:
    extraction_prompt = f"""Extract a date and time from this request. Respond with ONLY JSON:
{{"date": "YYYY-MM-DD" or null, "time": "HH:MM" or null}}
If neither is mentioned, use null for both.

Request: {user_text}"""
    try:
        result = json.loads(_ask_llm(extraction_prompt))
    except (json.JSONDecodeError, KeyError):
        return "Could I get the date and time you'd like to book?"
    date, time = result.get("date"), result.get("time")
    if not date or not time:
        return "Could you please specify both the date and time for the appointment?"
    outcome = book_appointment(date, time)
    if outcome["success"]:
        return f"Your appointment on {date} at {time} has been booked successfully!"
    return f"Sorry, the slot on {date} at {time} is unavailable. Please choose another time."

def warmup():
    _get_llm()
    from src.intent_router import classify_intent
    classify_intent("Hello")

def handle_user_input(user_text: str, use_rag: bool = True) -> str:
    start = time.time()
    intent = classify_intent(user_text)
    if intent == "faq":
        response = _handle_faq(user_text, use_rag)
    elif intent == "order_status":
        response = _handle_order_status(user_text)
    elif intent == "schedule_appointment":
        response = _handle_schedule(user_text)
    else:
        response = "I'm having trouble with that — let me connect you to a human agent."
    latency = round((time.time() - start) * 1000, 2)
    log_interaction(user_text, intent, response, latency)
    return response
