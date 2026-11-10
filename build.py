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


# ---- recaps/ and posts/ -> sets.json -------------------------------------
# recaps/2026-10/      one folder per month, images in the order they should show
# posts/2026-10-27/    one folder per Instagram post (add -2 etc. for two posts a day)
# Optional info.txt in each folder, one "key: value" per line:
#   title: ber.          (recaps: shown on the cover)
#   big: 01              (recaps: the big number on the cover)
#   caption: text        (the post or recap text; use \n for a new line)
#   credit: Daniel Breuer @alpindis
#   chapter: ber         (only if the automatic chapter by date is wrong)
# A file called cover.jpg (or .png/.webp) is used as the cover, otherwise the first image.
import datetime
import re

STARTS = [("origin", "2024-08-26"), ("white", "2025-03-03"), ("baby-blue", "2025-05-23"),
          ("lavendel", "2025-07-07"), ("navy-blue", "2025-10-21"), ("grey", "2026-01-01"),
          ("vanilla", "2026-04-01"), ("vanilla-2", "2026-06-23"), ("ber", "2026-09-01"),
          ("ember", "2026-11-01"), ("red", "2027-01-01")]


def chapter_for(day):
    found = None
    for ch, start in STARTS:
        if day >= datetime.date.fromisoformat(start):
            found = ch
    return found or "origin"


def read_info(folder):
    info = {}
    for name in ("info.txt", "info.txt.txt"):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8-sig") as f:
                for line in f:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        info[k.strip().lower()] = v.strip().replace("\\n", "\n")
            break
    return info


def read_set(base, name, day):
    folder = os.path.join(base, name)
    imgs = sorted(n for n in os.listdir(folder) if n.lower().endswith(EXT))
    if not imgs:
        return None
    covers = [n for n in imgs if os.path.splitext(n)[0].lower() == "cover"]
    rest = [n for n in imgs if n not in covers]
    info = read_info(folder)
    url = lambda n: f"{base}/{name}/{n}"
    return {
        "id": name,
        "chapter": info.get("chapter") or chapter_for(day),
        "cover": url(covers[0] if covers else rest[0]),
        "images": [url(n) for n in (rest or covers)],
        "title": info.get("title", ""),
        "big": info.get("big", ""),
        "caption": info.get("caption", ""),
        "credit": info.get("credit", ""),
    }


sets = {"recaps": [], "posts": []}
if os.path.isdir("recaps"):
    for name in sorted(os.listdir("recaps"), reverse=True):
        m = re.match(r"^(\d{4})-(\d{2})", name)
        if not m or not os.path.isdir(os.path.join("recaps", name)):
            continue
        s = read_set("recaps", name, datetime.date(int(m[1]), int(m[2]), 15))
        if s:
            s["number"] = f"{m[2]}/{m[1][2:]}"
            sets["recaps"].append(s)
if os.path.isdir("posts"):
    for name in sorted(os.listdir("posts"), reverse=True):
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", name)
        if not m or not os.path.isdir(os.path.join("posts", name)):
            continue
        day = datetime.date(int(m[1]), int(m[2]), int(m[3]))
        s = read_set("posts", name, day)
        if s:
            s["date"] = day.strftime("%d.%m.%y")
            sets["posts"].append(s)

with open("sets.json", "w", encoding="utf-8") as f:
    json.dump(sets, f, ensure_ascii=False, indent=1)
print(f"{len(sets['recaps'])} recaps, {len(sets['posts'])} posts")
