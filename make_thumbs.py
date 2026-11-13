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

# How much of each photo is in its chapter's colour (the screensaver shows the photos that match).
COLOURS = {"origin": "#000000", "white": "#FFFFFF", "baby-blue": "#91B2EB", "lavendel": "#BAB6DE", "navy-blue": "#343A4E",
           "grey": "#A9A9A9", "vanilla": "#FFF8BB", "vanilla-2": "#B8B05F", "ber": "#B8C98B", "ember": "#E9A283", "red": "#B3202A"}
try:
    import numpy as np
    def lab(rgb):
        c=rgb/255.0; c=np.where(c>0.04045,((c+0.055)/1.055)**2.4,c/12.92)
        M=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
        xyz=c@M.T/np.array([0.95047,1,1.08883]); f=np.where(xyz>0.008856,np.cbrt(xyz),7.787*xyz+16/116)
        return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],-1)
    def score(path, hexcol):
        im=Image.open(path).convert('RGB'); im.thumbnail((160,160)); L=lab(np.asarray(im,dtype=float).reshape(-1,3))
        t=lab(np.array([[int(hexcol[i:i+2],16) for i in (1,3,5)]],dtype=float))[0]
        tc=np.hypot(t[1],t[2]); c=np.hypot(L[:,1],L[:,2])
        if tc<6:   # white / black / grey: match by lightness, little colour
            return float(((abs(L[:,0]-t[0])<10)&(c<8)).mean())
        th=np.degrees(np.arctan2(t[2],t[1])); h=np.degrees(np.arctan2(L[:,2],L[:,1])); dh=np.abs((h-th+180)%360-180)
        return float(((dh<22)&(c>tc*0.35)&(abs(L[:,0]-t[0])<32)).mean())

    match = {}
    for src in dims:
        parts = src.split("/")
        if len(parts) == 3 and parts[0] == "photos" and parts[1] in COLOURS:
            match[src] = round(score("thumbs/" + os.path.splitext(src)[0] + "-600.webp", COLOURS[parts[1]]), 3)
    with open(os.path.join("thumbs", "colour.json"), "w") as f:
        json.dump(match, f, separators=(",", ":"))
    print(len(match), "colour scores")
except ImportError:
    print("numpy missing: colour scores skipped")
print(made, "previews,", len(dims), "images")
