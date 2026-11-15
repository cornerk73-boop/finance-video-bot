import json
import re
import subprocess


def fmt(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


dur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "csv=p=0", "voice.mp3"]))
marks = json.load(open("timings.json", encoding="utf-8"))

if not marks:
    text = json.load(open("script.json", encoding="utf-8"))["script"]
    text = text.replace("[VERIFY]", "")
    sents = [s.strip() for s in re.split(r"(?<=[।.!?])\s+", text) if s.strip()]
    total = sum(len(s) for s in sents)
    t, marks = 0, []
    for s in sents:
        d = dur * len(s) / total
        marks.append({"text": s, "start": t, "end": t + d})
        t += d

merged, cur = [], None
for m in marks:
    if cur is None:
        cur = dict(m)
    else:
        cur["text"] += " " + m["text"]
        cur["end"] = m["end"]
    if len(cur["text"].split()) >= 6:
        merged.append(cur)
        cur = None
if cur:
    merged.append(cur)

cues = []
for m in merged:
    words = m["text"].replace("[VERIFY]", "").split()
    if not words:
        continue
    chunks = [words[i:i + 8] for i in range(0, len(words), 8)]
    total = sum(len(" ".join(c)) for c in chunks)
    t, span = m["start"], m["end"] - m["start"]
    for c in chunks:
        line = " ".join(c)
        d = span * len(line) / total
        half = (len(c) + 1) // 2
        txt = (" ".join(c[:half]) + "\n" + " ".join(c[half:])) if len(c) > 4 else line
        cues.append((t, t + d, txt))
        t += d

with open("subs.srt", "w", encoding="utf-8") as f:
    for i, (a, b, txt) in enumerate(cues, 1):
        f.write(f"{i}\n{fmt(a)} --> {fmt(b)}\n{txt}\n\n")
print("Subtitle cues:", len(cues))
