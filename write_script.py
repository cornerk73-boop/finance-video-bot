import json
import os
import time
import urllib.request
import urllib.error

API_KEY = os.environ["GEMINI_API_KEY"]
BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
MODELS = [
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
]
MIN_WORDS = 330   # change these two numbers for a different length
MAX_WORDS = 420

RESEARCH = """Use Google Search to research this Indian finance news:
{title}

Write a factual brief in English, 300-400 words, covering: what happened,
key numbers and dates, who is involved, background, what it means for common
Indian people, and the official source (RBI, SEBI, NSE, BSE, PIB) if any.
Only include facts you actually found. If something is unconfirmed, say so.
Do not copy sentences from articles."""

PROMPT = """You are a scriptwriter for an Indian finance news YouTube channel.
Headline: {title}

Fact brief (use only this):
{facts}

Write in simple, spoken Hindi (Devanagari) for a common Indian investor.
Rules:
- {mn} to {mx} words. This is important.
- Structure: strong hook, background, key facts with numbers, what it means
  for common people, what to watch next, short closing.
- Use ONLY facts in the brief. Do NOT invent numbers, dates or names.
  If a number is unknown, write [VERIFY].
- No buy, sell, apply or avoid advice. Educational only.
- Last line: "यह सिर्फ़ जानकारी है, निवेश सलाह नहीं।"

Return ONLY JSON with these keys:
"title": YouTube title in Hindi, under 70 characters,
"script": the full Hindi narration,
"description": Hindi description, 3 lines, with disclaimer,
"tags": list of 10 tags (Hindi and English),
"image_keywords": list of 8 English search words for stock photos
"""


def call(model, prompt, search, as_json):
    url = BASE + model + ":generateContent?key=" + API_KEY
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    if search:
        body["tools"] = [{"google_search": {}}]
    if as_json:
        body["generationConfig"] = {"responseMimeType": "application/json"}
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)


def ask(prompt, search=False, as_json=False):
    for model in MODELS:
        for attempt in range(1, 4):
            try:
                print(f"Trying {model} (attempt {attempt})")
                return call(model, prompt, search, as_json)
            except urllib.error.HTTPError as e:
                print("HTTP", e.code, e.read().decode("utf-8")[:200])
                if e.code in (429, 500, 503):
                    time.sleep(10 * attempt)
                    continue
                break
            except Exception as e:
                print("Error:", e)
                time.sleep(5)
    return None


def parse(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    return json.loads(text)


if __name__ == "__main__":
    topics = json.load(open("topics.json", encoding="utf-8"))
    top = topics[0]
    title = top["title"]
    print("Topic:", title)

    facts = ask(RESEARCH.format(title=title), search=True)
    if not facts:
        print("Research failed, using headline only")
        facts = "Only the headline is known: " + title
    print("\nFACTS:\n", facts[:600])

    result = None
    extra = ""
    for _ in range(2):
        out = ask(PROMPT.format(title=title, facts=facts,
                                mn=MIN_WORDS, mx=MAX_WORDS) + extra,
                  as_json=True)
        if not out:
            break
        result = parse(out)
        words = len(result["script"].split())
        print("Word count:", words)
        if words >= MIN_WORDS * 0.8:
            break
        extra = f"\nYour last script was too short. Write at least {MIN_WORDS} words."

    if not result:
        raise SystemExit("Could not write script. Re-run in a few minutes.")

    result["source_headline"] = title
    result["facts"] = facts
    with open("script.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    words = len(result["script"].split())
    print("\nTITLE:", result["title"])
    print(f"WORDS: {words}  (about {words / 145:.1f} minutes)")
    print("\nSCRIPT:\n", result["script"])
    print("\nTAGS:", result["tags"])
    print("IMAGES:", result["image_keywords"])
