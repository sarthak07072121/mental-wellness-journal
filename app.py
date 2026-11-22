"""
Mental Wellness Journal Companion  (GenAI Mini Project - Problem 57)

Flow: Journal entry box -> supportive-reply system prompt -> LLM reply.
If the entry shows distress, helpline numbers are ALWAYS shown.
All entries are saved locally in journal_entries.json.

Run:  streamlit run app.py
"""

import json
import os
from datetime import datetime

import streamlit as st

from companion import (
    HELPLINES,
    check_distress,
    get_supportive_reply,
)

JOURNAL_FILE = "journal_entries.json"


# ---------- local storage ----------
def load_entries():
    if not os.path.exists(JOURNAL_FILE):
        return []
    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_entry(entry_text, reply, distress, mood):
    entries = load_entries()
    entries.append(
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mood": mood,
            "entry": entry_text,
            "reply": reply,
            "distress": distress,
        }
    )
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def show_helplines():
    lines = "\n".join(f"- **{name}:** {num}" for name, num in HELPLINES)
    st.error(
        "💙 **You don't have to go through this alone. Please reach out now:**\n\n"
        + lines
        + "\n\nIf you are in immediate danger, call **112** or go to the nearest hospital."
    )


# ---------- UI ----------
st.set_page_config(page_title="Journal Companion", page_icon="📔", layout="centered")
st.title("📔 Mental Wellness Journal Companion")
st.caption(
    "Write about your day. You'll get a kind, supportive reflection. "
    "This is not a substitute for professional help."
)

mood = st.select_slider(
    "How are you feeling overall?",
    options=["😞 Very low", "🙁 Low", "😐 Okay", "🙂 Good", "😄 Great"],
    value="😐 Okay",
)
entry = st.text_area("Today's journal entry", height=180,
                     placeholder="e.g. Exams are next week and I can't focus...")

if st.button("Reflect with me", type="primary"):
    if not entry.strip():
        st.warning("Please write something first.")
    else:
        with st.spinner("Reading your entry..."):
            result = get_supportive_reply(entry, mood)
        # Safety: keyword check OR LLM flag -> always show helplines
        distress = check_distress(entry) or result["distress"]

        if distress:
            show_helplines()
        st.subheader("Your companion says")
        st.write(result["reply"])
        if result.get("prompt"):
            st.info(f"✍️ Reflection prompt: {result['prompt']}")

        save_entry(entry, result["reply"], distress, mood)
        st.success("Entry saved to your local journal.")

# ---------- history ----------
st.divider()
st.subheader("Past entries")
entries = load_entries()
if not entries:
    st.write("No entries yet.")
for e in reversed(entries[-10:]):
    flag = " ⚠️" if e["distress"] else ""
    with st.expander(f"{e['time']}  ·  {e['mood']}{flag}"):
        st.markdown(f"**You wrote:** {e['entry']}")
        st.markdown(f"**Companion:** {e['reply']}")

with st.sidebar:
    st.header("Helplines (India)")
    for name, num in HELPLINES:
        st.markdown(f"**{name}**  \n{num}")
    st.caption("Emergency: 112")
    if st.button("Clear journal"):
        if os.path.exists(JOURNAL_FILE):
            os.remove(JOURNAL_FILE)
        st.rerun()
