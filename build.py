"""Builds photos.json from the chapter folders in photos/.

Runs automatically on GitHub every time something changes.
Optional captions/credits: put an info.txt in a chapter folder with lines like
    IMG_1234.jpg | Caption text | Photographer name
Use * instead of a file name to set a credit for every photo in the chapter:
    * | | Daniel Breuer @alpindis
"""
import json
import os

CHAPTERS = ["red", "ember", "ber", "vanilla-2", "vanilla", "grey",
            "navy-blue", "lavendel", "baby-blue", "white", "origin"]
EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")

out = []
for ch in CHAPTERS:
    folder = os.path.join("photos", ch)
    if not os.path.isdir(folder):
        continue
    info = {}
    info_path = os.path.join(folder, "info.txt")
    if os.path.exists(info_path):
        with open(info_path, encoding="utf-8") as f:
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if parts and parts[0]:
                    info[parts[0].lower()] = parts
    files = sorted((n for n in os.listdir(folder) if n.lower().endswith(EXT)), reverse=True)
    for name in files:
        meta = info.get(name.lower(), [])
        default = info.get("*", [])
        def pick(i):
            if len(meta) > i and meta[i]:
                return meta[i]
            return default[i] if len(default) > i else ""
        out.append({
            "src": f"photos/{ch}/{name}",
            "chapter": ch,
            "caption": pick(1),
            "credit": pick(2),
        })

with open("photos.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"{len(out)} photos")
