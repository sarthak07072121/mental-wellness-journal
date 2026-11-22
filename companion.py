"""
Core logic: system prompt, distress detection and LLM call.
Uses Groq's free API (OpenAI-compatible). Put GROQ_API_KEY in a .env file.
If no key is set, a safe offline reply is returned so the app still demos.
"""

import json
import os
import re

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

HELPLINES = [
    ("Tele-MANAS (24x7, free, Govt. of India)", "14416 or 1-800-891-4416"),
    ("iCall (TISS)", "9152987821"),
    ("Emergency", "112"),
]

# Rule-based safety net: works even if the LLM misses distress.
DISTRESS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "end it all",
    "want to die", "wanna die", "don't want to live", "dont want to live",
    "no reason to live", "self harm", "self-harm", "hurt myself", "cut myself",
    "hopeless", "worthless", "can't go on", "cant go on", "give up on life",
    "better off without me", "no way out", "panic attack", "can't breathe",
]

SYSTEM_PROMPT = """You are a warm, supportive journaling companion for college students.
The user shares a journal entry and their mood. Your job:
1. Acknowledge and validate their feelings in a kind, non-judgemental way.
2. Reflect back one or two key things they said, so they feel heard.
3. Offer 1-2 small, practical coping ideas (breathing, a short walk, talking to a friend,
   breaking tasks into steps, sleep). Keep it simple.
4. End with ONE gentle reflection question to help them think further.

Rules:
- Never diagnose, never give medical or medication advice.
- Do not lecture. Keep the reply under 150 words, plain friendly language.
- If the entry shows hopelessness, self-harm, suicidal thoughts or a crisis,
  set distress to true, gently encourage them to contact a helpline or a trusted person now.

Respond ONLY with valid JSON in this exact format:
{"reply": "<supportive message>", "prompt": "<one reflection question>", "distress": true/false}"""


def check_distress(text: str) -> bool:
    """Return True if the entry contains any distress keyword."""
    t = text.lower()
    return any(k in t for k in DISTRESS_KEYWORDS)


def _offline_reply(entry: str) -> dict:
    distress = check_distress(entry)
    if distress:
        reply = ("Thank you for trusting me with something this heavy. What you're feeling "
                 "matters, and you deserve support right now. Please reach out to Tele-MANAS "
                 "(14416) or someone you trust today. You don't have to carry this alone.")
    else:
        reply = ("Thank you for writing this down — putting feelings into words is a real step. "
                 "It sounds like a lot is on your mind. Try taking one slow breath and picking "
                 "just one small thing to do next.")
    return {"reply": reply + "\n\n(Offline mode: add GROQ_API_KEY for AI replies.)",
            "prompt": "What is one thing that would make tomorrow a little easier?",
            "distress": distress}


def _parse_json(content: str) -> dict:
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            return {
                "reply": str(data.get("reply", "")).strip() or content,
                "prompt": str(data.get("prompt", "")).strip(),
                "distress": bool(data.get("distress", False)),
            }
        except json.JSONDecodeError:
            pass
    return {"reply": content.strip(), "prompt": "", "distress": False}


def get_supportive_reply(entry: str, mood: str = "Okay") -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:  # Streamlit Cloud secrets
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            api_key = None
    if not api_key:
        return _offline_reply(entry)

    payload = {
        "model": MODEL,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Mood: {mood}\nJournal entry: {entry}"},
        ],
    }
    try:
        r = requests.post(GROQ_URL, json=payload, timeout=30,
                          headers={"Authorization": f"Bearer {api_key}"})
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        return _parse_json(content)
    except Exception as e:  # network / API errors -> safe fallback
        result = _offline_reply(entry)
        result["reply"] += f"\n\n(API error: {e})"
        return result
