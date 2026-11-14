import feedparser
import json
import urllib.parse

QUERIES = [
    "RBI OR SEBI OR Sensex OR Nifty when:1d",
    "GST OR budget OR income tax OR mutual fund OR bank when:1d",
    "share market OR gold price OR petrol price OR rupee when:1d",
    "IPO OR आईपीओ OR IPO GMP OR IPO listing when:1d",
    "IPO subscription OR IPO allotment OR SME IPO when:1d",
]
IPO_WORDS = ["ipo", "आईपीओ", "gmp", "लिस्टिंग", "allotment", "अलॉटमेंट"]
TRENDS_URL = "https://trends.google.com/trending/rss?geo=IN"


def rss_url(q):
    return ("https://news.google.com/rss/search?q="
            + urllib.parse.quote(q) + "&hl=hi&gl=IN&ceid=IN:hi")


def clean(title):
    return title.rsplit(" - ", 1)[0].strip()


def words(text):
    return set(w.strip(",.:;'\"|-?!()") for w in text.lower().split())


def similar(a, b):
    if not a or not b:
        return False
    return len(a & b) / len(a | b) >= 0.3


def get_trends():
    try:
        feed = feedparser.parse(TRENDS_URL)
        return [e.title.lower() for e in feed.entries]
    except Exception:
        return []


def fetch_news(top=10):
    items = []
    seen = set()
    for q in QUERIES:
        for e in feedparser.parse(rss_url(q)).entries:
            if e.link in seen:
                continue
            seen.add(e.link)
            items.append({
                "title": clean(e.title),
                "link": e.link,
                "published": e.get("published", ""),
                "source": e.get("source", {}).get("title", ""),
            })

    clusters = []
    for it in items:
        w = words(it["title"])
        for c in clusters:
            if similar(w, c["words"]):
                c["items"].append(it)
                break
        else:
            clusters.append({"words": w, "items": [it]})

    trends = get_trends()
    results = []
    for c in clusters:
        first = c["items"][0]
        sources = {i["source"] for i in c["items"] if i["source"]}
        trend_hit = any(t in first["title"].lower() for t in trends)
        score = len(sources) + (2 if trend_hit else 0)
        results.append({
            "title": first["title"],
            "link": first["link"],
            "published": first["published"],
            "publishers": len(sources),
            "trending": trend_hit,
            "score": score,
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top]


if __name__ == "__main__":
    news = fetch_news()
    with open("topics.json", "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    for n in news:
        flag = " [TRENDING]" if n["trending"] else ""
            for n in news:
        flag = " [TRENDING]" if n["trending"] else ""
        ipo = " [IPO]" if any(k in n["title"].lower() for k in IPO_WORDS) else ""
        print(f"{n['score']} | {n['publishers']} publishers{flag}{ipo} | {n['title']}")
