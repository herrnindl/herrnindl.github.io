"""Creates small preview images in thumbs/ for the grids (the full photos open in the viewer).
Run after adding photos: python3 make_thumbs.py"""
import os
from PIL import Image, ImageOps

EXT = (".jpg", ".jpeg", ".png", ".webp")
SIZE = 900
made = 0
for top in ("photos", "recaps", "posts", "journal", "press"):
    for root, _, files in os.walk(top):
        for n in files:
            if not n.lower().endswith(EXT):
                continue
            src = os.path.join(root, n)
            dst = os.path.join("thumbs", os.path.splitext(src)[0] + ".jpg")
            if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            im.thumbnail((SIZE, SIZE), Image.LANCZOS)
            im.save(dst, "JPEG", quality=80, optimize=True, progressive=True)
            made += 1
print(made, "thumbs")
