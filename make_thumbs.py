"""Creates small WebP previews in thumbs/ (two sizes) for the grids; the full photo opens in the viewer.
Run after adding photos: python3 make_thumbs.py"""
import json
import os
from PIL import Image, ImageOps

EXT = (".jpg", ".jpeg", ".png", ".webp")
SIZES = (600, 1200)
made = 0
dims = {}
for top in ("photos", "recaps", "posts", "journal", "press"):
    for root, _, files in os.walk(top):
        for n in files:
            if not n.lower().endswith(EXT):
                continue
            src = os.path.join(root, n).replace(os.sep, "/")
            base = os.path.join("thumbs", os.path.splitext(src)[0])
            im = None
            for s in SIZES:
                dst = f"{base}-{s}.webp"
                if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
                    continue
                if im is None:
                    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                t = im.copy(); t.thumbnail((s, s * 2), Image.LANCZOS)
                t.save(dst, "WEBP", quality=74, method=6)
                made += 1
            with Image.open(f"{base}-{SIZES[0]}.webp") as t:
                dims[src] = t.size
with open(os.path.join("thumbs", "sizes.json"), "w") as f:
    json.dump(dims, f, separators=(",", ":"))
print(made, "previews,", len(dims), "images")
