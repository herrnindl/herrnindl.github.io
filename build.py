"""Builds photos.json from the chapter folders in photos/.

Runs automatically on GitHub every time something changes.
Optional captions/credits: put an info.txt in a chapter folder with lines like
    IMG_1234.jpg | Caption text | Photographer name
Use * for every photo, or a pattern like name* for some of them:
    * | | Daniel Breuer @alpindis
Videos (.mp4) in a chapter folder show as silent looping clips between the photos.
photos/digitals/   plain, unedited photos (front, side, waist-up, headshot) -> digitals page
photos/selected.txt  one photo per line (e.g. white/photo.jpg); the first is the big photo on the start page
"""
import re
import fnmatch
import json
import os

CHAPTERS = ["ember", "ber", "vanilla-2", "vanilla", "grey",
            "navy-blue", "lavendel", "baby-blue", "white", "origin", "digitals"]
VIDEO = (".mp4", ".webm")
EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif") + VIDEO

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
        if name.lower().endswith(VIDEO):
            pass
        else:
          try:
            from PIL import Image
            with Image.open(os.path.join(folder, name)) as im:
                ex = im.getexif()
                d = ex.get_ifd(0x8769).get(36867) or ex.get(306) or ""
                if d[:4].isdigit():
                    taken = f"{d[8:10]}.{d[5:7]}.{d[0:4]}"
          except Exception:
            pass
        if not taken:
            m = re.match(r"(20\d\d)-(\d\d)-(\d\d)", name)
            if m:
                taken = f"{m.group(3)}.{m.group(2)}.{m.group(1)}"
        entry = {
            "date": taken or DATES.get(f"photos/{ch}/{name}", ""),
            "src": f"photos/{ch}/{name}",
            "chapter": ch,
            "caption": pick(1),
            "credit": pick(2),
        }
        if name.lower().endswith(VIDEO):
            entry["video"] = True
        out.append(entry)

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
    if not p.get("video"):
        p.update(thumb(p["src"]))

# colour match from make_thumbs.py: how much of the photo is in its chapter's colour
COLOUR = {}
if os.path.exists(os.path.join("thumbs", "colour.json")):
    with open(os.path.join("thumbs", "colour.json")) as f:
        COLOUR = json.load(f)
for p in out:
    if p["src"] in COLOUR:
        p["cm"] = COLOUR[p["src"]]

# photos/faces.json: where the face is in each photo -> "f": [x, y, size] (0-1), so crops never cut the face off.
# "nf": true = no clear face (back view, landscape, detail): fine in the galleries, left out of the games.
FACES = {}
if os.path.exists(os.path.join("photos", "faces.json")):
    with open(os.path.join("photos", "faces.json")) as f:
        FACES = json.load(f)
for p in out:
    fc = FACES.get(p["src"])
    if fc:
        if fc[2]:
            p["f"] = fc[:3]
        if not fc[3]:
            p["nf"] = True

# selected.txt: the photos that open the start page, in this order
sel_path = os.path.join("photos", "selected.txt")
if os.path.exists(sel_path):
    with open(sel_path, encoding="utf-8") as f:
        wanted = [l.strip().lstrip("/").lower() for l in f if l.strip() and not l.startswith("#")]
    by = {p["src"].lower()[len("photos/"):]: p for p in out}
    for i, w in enumerate(wanted):
        if w in by:
            by[w]["sel"] = i + 1

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
          ("ember", "2026-11-01")]


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
# journal/journal.lock.json : the journal, encrypted with the journal password (see journal/lock.py).
# When it exists, a plain journal.txt is never read, and only dates and entry numbers go public.
jlock = os.path.join("journal", "journal.lock.json")
if os.path.exists(jlock):
    with open(jlock, encoding="utf-8") as f:
        _lock = json.load(f)
    sets["journal"] = [j for j in sets["journal"] if not re.match(r"^\d{4}-\d{2}-\d{2}$", j["id"])]
    for e in _lock.get("entries", []):
        day = datetime.date.fromisoformat(e["id"][:10])
        folder = os.path.join("journal", day.isoformat())
        imgs = sorted(n for n in os.listdir(folder) if n.lower().endswith(EXT)) if os.path.isdir(folder) else []
        sets["journal"].append({
            "id": e["id"], "n": e["n"], "chapter": chapter_for(day),
            "cover": f"journal/{day.isoformat()}/{imgs[0]}" if imgs else "",
            "images": [f"journal/{day.isoformat()}/{n}" for n in imgs],
        })
    sets["journal_lock"] = {k: _lock[k] for k in ("iter", "salt", "iv", "data")}
for cand in (() if os.path.exists(jlock) else (jfile, jfile + ".txt")):
    if os.path.exists(cand):
        with open(cand, encoding="utf-8-sig") as f:
            raw = "\n".join(l for l in f.read().splitlines() if not l.lstrip().startswith("#"))
        sets["journal"] = [j for j in sets["journal"] if not re.match(r"^\d{4}-\d{2}-\d{2}$", j["id"])]
        # hidden entries (header line starts with "# ") still count for the entry numbers
        hidden_days = []
        with open(cand, encoding="utf-8-sig") as f:
            flag = False   # only the entry right after a "# HIDDEN" line counts
            for l in f.read().splitlines():
                if "HIDDEN" in l:
                    flag = True; continue
                h = re.match(r"^\s*#\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*\|", l)
                if h and flag:
                    hidden_days.append(datetime.date(int(h[3]), int(h[2]), int(h[1])).isoformat()); flag = False
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
# entry number: counted over all entries, hidden ones included (so hiding 02 keeps 03 as 03)
try:
    _all = sorted([j["id"][:10] for j in sets["journal"]] + hidden_days)
    for j in sets["journal"]:
        j["n"] = _all.index(j["id"][:10]) + 1
except NameError:
    pass

# Teasers: photos/<chapter>/teasers/ (sorted by file name), shown on the chapter page
sets["teasers"] = {}
for ch in CHAPTERS:
    folder = os.path.join("photos", ch, "teasers")
    if os.path.isdir(folder):
        names = sorted(n for n in os.listdir(folder) if n.lower().endswith(EXT))
        if names:
            sets["teasers"][ch] = []
            for n in names:
                word = re.sub(r"^\d+[-_ ]*", "", os.path.splitext(n)[0]).replace("-", " ").strip(". ")
                item = {"src": f"photos/{ch}/teasers/{n}", "word": word}
                item.update(thumb(item["src"]))
                sets["teasers"][ch].append(item)

# trips/2026-04-16-france/   one folder per trip, named after the day it started.
#   The photos (the ones that were posted, in the order they were posted) sit in the folder,
#   the highlight stories in stories/ (photos and .mp4 clips, in the order they were posted).
#   info.txt: title: france. · dates: 16.–19.04.26 · place: paris · caption: the story
#   The trip shows on its chapter's timeline; chapter: only if the date picks the wrong one.
sets["trips"] = []
if os.path.isdir("trips"):
    for name in sorted(os.listdir("trips"), reverse=True):
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", name)
        folder = os.path.join("trips", name)
        if not m or not os.path.isdir(folder):
            continue
        day = datetime.date(int(m[1]), int(m[2]), int(m[3]))
        s = read_set("trips", name, day)
        info = read_info(folder)
        if not s:   # a trip with stories only (nothing posted): the first story photo is the cover
            sf = os.path.join(folder, "stories")
            first = sorted(n for n in os.listdir(sf) if n.lower().endswith(EXT) and not n.lower().endswith(VIDEO)) if os.path.isdir(sf) else []
            if not first:
                continue
            s = {"id": name, "chapter": info.get("chapter") or chapter_for(day), "cover": f"trips/{name}/stories/{first[0]}",
                 "images": [], "title": info.get("title", ""), "big": "", "caption": info.get("caption", ""), "credit": info.get("credit", "")}
        s["date"] = day.strftime("%d.%m.%y")
        s["day"] = day.isoformat()
        s["dates"] = info.get("dates", s["date"])
        s["place"] = info.get("place", "")
        def clip(src):
            poster = "thumbs/" + os.path.splitext(src)[0] + "-poster.webp"
            return {"src": src, "video": True, "poster": poster if os.path.exists(poster) else ""}
        s["photos"] = [clip(p) if p.lower().endswith(VIDEO) else dict({"src": p}, **thumb(p)) for p in s["images"]]
        s["stories"] = []
        sfolder = os.path.join(folder, "stories")
        if os.path.isdir(sfolder):
            for n in sorted(x for x in os.listdir(sfolder) if x.lower().endswith(EXT)):
                src = f"trips/{name}/stories/{n}"
                if n.lower().endswith(VIDEO):
                    poster = "thumbs/" + os.path.splitext(src)[0] + "-poster.webp"
                    s["stories"].append({"src": src, "video": True, "poster": poster if os.path.exists(poster) else ""})
                else:
                    s["stories"].append(dict({"src": src}, **thumb(src)))
        sets["trips"].append(s)

for group in ("recaps", "posts", "journal", "trips"):
    for item in sets[group]:
        if item.get("cover"):
            item.update(thumb(item["cover"]))

with open("sets.json", "w", encoding="utf-8") as f:
    json.dump(sets, f, ensure_ascii=False, indent=1)
print(f"{len(sets['recaps'])} recaps, {len(sets['posts'])} posts, {len(sets['journal'])} journal")


# ---- launch day: from 01.12.2026 Google may list the site ----
# The pages carry <meta name="robots" content="noindex"> until then. From launch on, the build
# removes it from the public pages (only in what gets published, the files in the repo stay as they are)
# and writes robots.txt + sitemap.xml. The Lebenslauf and the 404 page stay hidden from Google.
import datetime, glob
LAUNCH = datetime.datetime(2026, 12, 1, tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
HIDDEN = {"lebenslauf.html", "404.html"}
# only on GitHub: run locally, this part would rewrite the page files in the repo itself
if os.environ.get("GITHUB_ACTIONS") == "true" and datetime.datetime.now(datetime.timezone.utc) >= LAUNCH:
    # the CV stays on the site but out of Google: its text moves to cv.html (blocked in robots.txt)
    # and the Lebenslauf tab loads it when someone opens it
    with open("index.html", encoding="utf-8") as f:
        idx = f.read()
    tag = '<section class="cv panel" id="lebenslauf" lang="de" hidden>'
    if tag in idx:
        a = idx.index(tag) + len(tag); z = idx.index("</section>", a)
        with open("cv.html", "w", encoding="utf-8") as f:
            f.write(idx[a:z])
        idx = idx[:a - len(tag)] + tag.replace(" hidden>", ' hidden data-src="cv.html">') + "\n  " + idx[z:]
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(idx)
    public = []
    for page in sorted(glob.glob("*.html")):
        if page == "cv.html":
            continue
        if page in HIDDEN:
            continue
        with open(page, encoding="utf-8") as f:
            html = f.read()
        html = html.replace('<meta name="robots" content="noindex">\n', "").replace('<meta name="robots" content="noindex">', "")
        # link preview (image + description) only from launch day; before that the old preview stays
        html = re.sub(r"<!--LAUNCH-PREVIEW[^\n]*\n", "", html).replace("\nLAUNCH-PREVIEW-->", "")
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)
        public.append("https://herrnindl.com/" + ("" if page == "index.html" else page))
    with open("robots.txt", "w") as f:
        # also kept out of Google: the journal text (sets.json holds it too), the build scripts and the worker code
        f.write("User-agent: *\nDisallow: /lebenslauf.html\nDisallow: /cv.html\nDisallow: /journal/\nDisallow: /sets.json\n"
                "Disallow: /README.md\nDisallow: /build.py\nDisallow: /make_thumbs.py\nDisallow: /cloudflare/\n\nSitemap: https://herrnindl.com/sitemap.xml\n")
    with open("sitemap.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "".join("  <url><loc>%s</loc></url>\n" % u for u in public) + "</urlset>\n")
    print("launch: %d pages open for Google" % len(public))

