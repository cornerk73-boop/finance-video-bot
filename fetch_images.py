import json
import os
import urllib.parse
import urllib.request

KEY = os.environ["PIXABAY_API_KEY"]
FALLBACK = ["indian rupee notes", "stock market chart", "bank building",
            "calculator money", "smartphone payment", "gold coins",
            "mumbai skyline", "office desk", "credit card", "piggy bank"]
BAD_KW = ["logo", "brand", "flag", "celebrity", "news", "newspaper",
          "person", "people", "face", "man", "woman", "girl", "boy"]
BAD_TAGS = ["fashion", "model", "girl", "woman", "man", "people", "portrait",
            "baby", "child", "sport", "baseball", "beauty", "bikini",
            "party", "wedding", "politician", "logo", "newspaper", "news"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60)


def good(hit, kw):
    tags = [t.strip().lower() for t in hit.get("tags", "").split(",")]
    tagtext = " ".join(tags)
    if any(b in tagtext.split() or b in tags for b in BAD_TAGS):
        return False
    words = [w for w in kw.lower().split() if len(w) > 3]
    return any(w in tagtext for w in words)


def main():
    data = json.load(open("script.json", encoding="utf-8"))
    kws = [k.strip() for k in data.get("image_keywords", [])
           if not any(b in k.lower().split() for b in BAD_KW)]
    kws = kws + FALLBACK
    os.makedirs("images", exist_ok=True)
    used, credits, n = set(), [], 0
    for kw in kws:
        if n >= 8:
            break
        url = ("https://pixabay.com/api/?key=" + KEY
               + "&q=" + urllib.parse.quote(kw)
               + "&image_type=photo&orientation=horizontal"
               + "&safesearch=true&per_page=30&min_width=1280")
        try:
            res = json.load(get(url))
        except Exception as e:
            print("Search failed:", kw, e)
            continue
        for p in res.get("hits", []):
            if p["id"] in used or not good(p, kw):
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
            print(f"Saved {n} | {kw} | tags: {p['tags']}")
            break
        else:
            print("No good match for:", kw)
    json.dump(credits, open("credits.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    if n < 4:
        raise SystemExit("Too few relevant images found")


main()
