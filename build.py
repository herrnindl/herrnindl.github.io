"""Builds photos.json from the chapter folders in photos/.

Runs automatically on GitHub every time something changes.
Optional captions/credits: put an info.txt in a chapter folder with lines like
    IMG_1234.jpg | Caption text | Photographer name
Use * for every photo, or a pattern like name* for some of them:
    * | | Daniel Breuer @alpindis
"""
import fnmatch
import json
import os

CHAPTERS = ["red", "ember", "ber", "vanilla-2", "vanilla", "grey",
            "navy-blue", "lavendel", "baby-blue", "white", "origin"]
EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")

DATES = {}
if os.path.exists(os.path.join("photos", "dates.json")):
    with open(os.path.join("photos", "dates.json")) as f:
        DATES = json.load(f)

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
    files = sorted(n for n in os.listdir(folder) if n.lower().endswith(EXT))
    patterns = [k for k in info if "*" in k]
    for name in files:
        meta = info.get(name.lower(), [])
        default = next((info[k] for k in patterns if fnmatch.fnmatch(name.lower(), k)), [])
        def pick(i):
            if len(meta) > i and meta[i]:
                return meta[i]
            return default[i] if len(default) > i else ""
        taken = ""
        try:
            from PIL import Image
            with Image.open(os.path.join(folder, name)) as im:
                ex = im.getexif()
                d = ex.get_ifd(0x8769).get(36867) or ex.get(306) or ""
                if d[:4].isdigit():
                    taken = f"{d[8:10]}.{d[5:7]}.{d[0:4]}"
        except Exception:
            pass
        out.append({
            "date": taken or DATES.get(f"photos/{ch}/{name}", ""),
            "src": f"photos/{ch}/{name}",
            "chapter": ch,
            "caption": pick(1),
            "credit": pick(2),
        })

SIZES = {}
if os.path.exists(os.path.join("thumbs", "sizes.json")):
    with open(os.path.join("thumbs", "sizes.json")) as f:
        SIZES = json.load(f)


def thumb(path):
    base = "thumbs/" + os.path.splitext(path)[0]
    if path in SIZES and os.path.exists(base + "-600.webp"):
        return {"thumb": base + "-600.webp", "thumb2": base + "-1200.webp", "w": SIZES[path][0], "h": SIZES[path][1]}
    return {"thumb": path}


for p in out:
    p.update(thumb(p["src"]))

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
# A file called cover.jpg (or .png/.webp) is the cover and the first image inside, otherwise the first image is the cover.
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
        "images": [url(n) for n in covers[:1] + rest],
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

# press/2024-08-platzhirsch/ etc.: scans or photos of an article, shown when its press entry is tapped
sets["press"] = {}
if os.path.isdir("press"):
    for name in sorted(os.listdir("press")):
        folder = os.path.join("press", name)
        if os.path.isdir(folder):
            imgs = sorted(n for n in os.listdir(folder) if n.lower().endswith(EXT))
            if imgs:
                sets["press"][name] = [f"press/{name}/{n}" for n in imgs]

# journal/2026-11-20-title/ : post.txt (first line = title, rest = text) plus photos
sets["journal"] = []
if os.path.isdir("journal"):
    for name in sorted(os.listdir("journal"), reverse=True):
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", name)
        folder = os.path.join("journal", name)
        if not m or not os.path.isdir(folder):
            continue
        text = ""
        for t in ("post.txt", "post.txt.txt", "post.md"):
            if os.path.exists(os.path.join(folder, t)):
                with open(os.path.join(folder, t), encoding="utf-8-sig") as f:
                    text = f.read().strip()
                break
        lines = text.splitlines()
        title = lines[0].strip() if lines else name[11:].replace("-", " ")
        body = "\n".join(lines[1:]).strip()
        imgs = sorted(n for n in os.listdir(folder) if n.lower().endswith(EXT))
        if not body and not imgs:
            continue
        day = datetime.date(int(m[1]), int(m[2]), int(m[3]))
        sets["journal"].append({
            "id": name, "chapter": chapter_for(day), "date": day.strftime("%d.%m.%y"),
            "title": title, "caption": body,
            "cover": f"journal/{name}/{imgs[0]}" if imgs else "",
            "images": [f"journal/{name}/{n}" for n in imgs],
            "credit": "", "big": "",
        })

# journal/journal.txt : all posts in one file.
#   20.11.2026 | title
#   text ...
#   ---
# Lines starting with # are ignored. Photos: optional folder journal/2026-11-20/
jfile = os.path.join("journal", "journal.txt")
for cand in (jfile, jfile + ".txt"):
    if os.path.exists(cand):
        with open(cand, encoding="utf-8-sig") as f:
            raw = "\n".join(l for l in f.read().splitlines() if not l.lstrip().startswith("#"))
        sets["journal"] = [j for j in sets["journal"] if not re.match(r"^\d{4}-\d{2}-\d{2}$", j["id"])]
        for block in re.split(r"^\s*-{3,}\s*$", raw, flags=re.M):
            lines = [l.rstrip() for l in block.strip().splitlines()]
            if not lines:
                continue
            m = re.match(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*\|?\s*(.*)$", lines[0])
            if not m:
                continue
            day = datetime.date(int(m[3]), int(m[2]), int(m[1]))
            folder = os.path.join("journal", day.isoformat())
            imgs = sorted(n for n in os.listdir(folder) if n.lower().endswith(EXT)) if os.path.isdir(folder) else []
            sets["journal"].append({
                "id": day.isoformat(), "chapter": chapter_for(day), "date": day.strftime("%d.%m.%y"),
                "title": m[4].strip() or "journal.", "caption": "\n".join(lines[1:]).strip(),
                "cover": f"journal/{day.isoformat()}/{imgs[0]}" if imgs else "",
                "images": [f"journal/{day.isoformat()}/{n}" for n in imgs],
                "credit": "", "big": "",
            })
        break
sets["journal"].sort(key=lambda j: j["id"][:10], reverse=True)

for group in ("recaps", "posts", "journal"):
    for item in sets[group]:
        if item.get("cover"):
            item.update(thumb(item["cover"]))

with open("sets.json", "w", encoding="utf-8") as f:
    json.dump(sets, f, ensure_ascii=False, indent=1)
print(f"{len(sets['recaps'])} recaps, {len(sets['posts'])} posts, {len(sets['journal'])} journal")
