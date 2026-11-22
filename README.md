# Mental Wellness Journal Companion (Problem 57)

**Sarthak Chakurkar – Roll No 57 – GenAI (LLM) Mini Project**

A Streamlit journaling app that replies supportively to a student's journal entry using an LLM (Groq, Llama 3.1), always shows helpline numbers when an entry shows distress, and saves entries locally.

## Features
- Journal entry box + mood slider
- Supportive reply from an LLM with a reflection question
- Two-layer distress check (keyword list + LLM flag) → helplines always shown (Tele-MANAS 14416)
- Entries saved locally in `journal_entries.json`, past entries listed
- Works in offline mode (template replies) if no API key is set

## Setup
```bash
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env   # free key from console.groq.com
streamlit run app.py
```
Test with 5 sample inputs: `python test_samples.py`

## Files
- `app.py` – Streamlit UI and local storage
- `companion.py` – system prompt, distress detection, LLM call
- `test_samples.py` – runs 5 sample entries

> Not a substitute for professional help. In an emergency call 112.
