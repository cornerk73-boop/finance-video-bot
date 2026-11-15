import asyncio
import json
import edge_tts

VOICE = "hi-IN-SwaraNeural"  # female;

async def main():
    data = json.load(open("script.json", encoding="utf-8"))
    text = data["script"].replace("[VERIFY]", "")
    comm = edge_tts.Communicate(text, VOICE, rate="+5%")
    marks = []
    with open("voice.mp3", "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                marks.append({
                    "text": chunk["text"],
                    "start": chunk["offset"] / 10_000_000,
                    "end": (chunk["offset"] + chunk["duration"]) / 10_000_000,
                })
    json.dump(marks, open("timings.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("Voice saved. Timing marks:", len(marks))


asyncio.run(main())
