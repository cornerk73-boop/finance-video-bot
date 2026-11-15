import json
import os
import urllib.parse
import urllib.request

KEY = os.environ["PIXABAY_API_KEY"]
FALLBACK = ["indian rupee", "stock market", "mumbai city",
            "calculator money", "business meeting", "bank building",
            "mobile payment", "newspaper"]
BAD = ["logo", "brand", "flag", "celebrity"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60)


def main():
    data = json.load(open("script.json", encoding="utf-8"))
    kws = [k for k in data.get("image_keywords", [])
           if not any(b in k.lower() for b in BAD)]
    kws = (kws + FALLBACK)[:12]
    os.makedirs("images", exist_ok=True)
    used, credits, n = set(), [], 0
    for kw in kws:
        if n >= 8:
            break
        url = ("https://pixabay.com/api/?key=" + KEY
               + "&q=" + urllib.parse.quote(kw)
               + "&image_type=photo&orientation=horizontal"
               + "&safesearch=true&per_page=10&min_width=1280")
        try:
            res = json.load(get(url))
        except Exception as e:
            print("Search failed:", kw, e)
            continue
        for p in res.get("hits", []):
            if p["id"] in used:
                continue
            used.add(p["id"])
            try:
                img = get(p["largeImageURL"]).read()
            except Exception as e:
                print("Download failed:", e)
                continue
            n += 1
            open(f"images/img_{n:02d}.jpg", "wb").write(img)
            credits.append(f"Image by {p['user']} on Pixabay: {p['pageURL']}")
            print("Saved", n, kw)
            break
    json.dump(credits, open("credits.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    if n < 3:
        raise SystemExit("Too few images downloaded")


main()
