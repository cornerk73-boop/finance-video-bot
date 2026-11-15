import glob
import json
import subprocess

FPS = 25


def run(cmd):
    subprocess.run(cmd, check=True)


dur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "csv=p=0", "voice.mp3"]))
imgs = sorted(glob.glob("images/*.jpg"))
if not imgs:
    raise SystemExit("No images found")
seg = dur / len(imgs)
frames = int(seg * FPS) + FPS // 2

with open("list.txt", "w") as lst:
    for i, img in enumerate(imgs):
        out = f"clip_{i}.mp4"
        vf = ("scale=2400:1350:force_original_aspect_ratio=increase,"
              "crop=2400:1350,"
              "zoompan=z='min(zoom+0.0005,1.12)':x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps={FPS},"
              "format=yuv420p")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", img, "-vf", vf,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", out])
        lst.write(f"file '{out}'\n")

style = ("FontName=Noto Sans Devanagari,FontSize=14,"
         "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
         "BorderStyle=1,Outline=2,Shadow=0,MarginV=35,Alignment=2")
run(["ffmpeg", "-y", "-loglevel", "error",
     "-f", "concat", "-safe", "0", "-i", "list.txt", "-i", "voice.mp3",
     "-vf", f"subtitles=subs.srt:force_style='{style}'",
     "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
     "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
     "-t", str(dur), "final.mp4"])

d = json.load(open("script.json", encoding="utf-8"))
credits = json.load(open("credits.json", encoding="utf-8"))
with open("description.txt", "w", encoding="utf-8") as f:
    f.write(d["title"] + "\n\n" + d["description"] + "\n\n")
    f.write("Source headline: " + d.get("source_headline", "") + "\n")
    f.write("Voice: AI-generated narration. Images: Pixabay (free license).\n\n")
    f.write("\n".join(credits) + "\n\n")
    f.write("Tags: " + ", ".join(d["tags"]) + "\n")
print("Video done:", round(dur), "seconds")
