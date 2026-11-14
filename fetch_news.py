import feedparser
import json
import urllib.parse

QUERY = "RBI OR SEBI OR Sensex OR Nifty OR GST OR budget OR mutual fund OR income tax when:1d"

URL = (
    "https://news.google.com/rss/search?q="
    + urllib.parse.quote(QUERY)
    + "&hl=hi&gl=IN&ceid=IN:hi"
)


def fetch_news(limit=15):
    feed = feedparser.parse(URL)
    items = []
    for e in feed.entries[:limit]:
        items.append({
            "title": e.title,
            "link": e.link,
            "published": e.get("published", ""),
            "source": e.get("source", {}).get("title", ""),
        })
    return items


if __name__ == "__main__":
    news = fetch_news()
    with open("topics.json", "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    for n in news:
        print("-", n["title"])
