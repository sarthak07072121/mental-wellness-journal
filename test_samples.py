"""Run 5 sample journal entries through the companion and print results.
Usage: python test_samples.py
"""
from companion import check_distress, get_supportive_reply

SAMPLES = [
    ("🙁 Low", "Exams start next week and I haven't studied enough. I keep scrolling my phone instead."),
    ("😄 Great", "Our team won the hackathon today! I finally feel my hard work paid off."),
    ("😐 Okay", "I had an argument with my roommate and now it feels awkward in the room."),
    ("😞 Very low", "I feel hopeless. Nothing I do matters and I don't want to live like this anymore."),
    ("🙁 Low", "I miss home. Everyone here seems to have friends except me."),
]

for i, (mood, text) in enumerate(SAMPLES, 1):
    res = get_supportive_reply(text, mood)
    distress = check_distress(text) or res["distress"]
    print(f"--- Sample {i} | mood: {mood} | distress: {distress}")
    print("Entry :", text)
    print("Reply :", res["reply"])
    print("Prompt:", res["prompt"])
    if distress:
        print(">> Helplines shown: Tele-MANAS 14416, iCall 9152987821, Emergency 112")
    print()
