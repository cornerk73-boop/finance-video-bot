import json
import os
import time
import urllib.request
import urllib.error

API_KEY = os.environ["GEMINI_API_KEY"]
MODELS = [
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
]
BASE = "https://generativelanguage.googleapis.com/v1beta/models/"

PROMPT = """You are a scriptwriter for an Indian finance news YouTube Shorts channel.
Topic headline: {title}

Write in simple, spoken Hindi (Devanagari) for a common Indian investor.
Rules:
- 150 to 190 words, about 60-75 seconds when spoken.
- Start with a strong hook line, then 3-4 short facts, then what it means in simple words.
- Use ONLY facts present in the headline. Do NOT invent numbers, dates or names.
  If a number is needed but unknown, write [VERIFY] there.
- No buy, sell, apply or avoid advice. Educational only.
- Last line: "यह सिर्फ़ जानकारी है, निवेश सलाह नहीं।"

Return ONLY JSON with these keys:
"title": YouTube title in Hindi, under 70 characters,
"script": the full Hindi narration,
"description": Hindi description, 3 lines, with disclaimer,
"tags": list of 8 tags (Hindi and English),
"image_keywords": list of 5 English search words for stock photos
"""


def call(model, title):
    url = BASE + model + ":generateContent?key=" + API_KEY
    body = {
        "contents": [{"parts": [{"text": PROMPT.format(title=title)}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.load(r)
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)


def ask(title):
    for model in MODELS:
        for attempt in range(1, 4):
            try:
                print(f"Trying {model} (attempt {attempt})")
                return call(model, title)
            except urllib.error.HTTPError as e:
                msg = e.read().decode("utf-8")[:200]
                print("HTTP", e.code, msg)
                if e.code in (429, 500, 503):
                    time.sleep(10 * attempt)
                    continue
                break  # other errors: try next model
            except Exception as e:
                print("Error:", e)
                time.sleep(5)
    raise SystemExit("All models busy. Please re-run in a few minutes.")


if __name__ == "__main__":
    topics = json.load(open("topics.json", encoding="utf-8"))
    top = topics[0]
    print("Topic:", top["title"])
    result = ask(top["title"])
    result["source_headline"] = top["title"]
    with open("script.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\nTITLE:", result["title"])
    print("\nSCRIPT:\n", result["script"])
    print("\nTAGS:", result["tags"])
    print("IMAGES:", result["image_keywords"])
