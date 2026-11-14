# MN.

Photo site of Markus Nindl, sorted by colour chapter.

## Add photos

1. Open the chapter folder in `photos/` (e.g. `photos/ember`).
2. **Add file → Upload files**, drop your photos in, **Commit changes**.
3. The site updates by itself in about a minute.

Keep photos around 2–3 MB (long side about 2500 px) so the site loads fast.

## Captions and photographer (optional)

Create `info.txt` in the chapter folder, one line per photo:

```
IMG_1234.jpg | Caption text | Photographer
```

## Chapter folders

red · ember · ber · vanilla-2 · vanilla · grey · navy-blue · lavendel · baby-blue · white · origin

## Faces (photos/faces.json)

Where the face is in each photo: `"photo path": [x, y, size, ok]` (0–1, from the top left).
Crops on the site and in the games keep the face in view. `ok` = 0 means no clear face
(back view, landscape, detail): the photo stays in the galleries but not in the games.
New photos without a line still work, they are just cropped from the middle and left out of the games.

## Small pages

- `now.html` — edit the NOW block at the top (song on repeat, working on, …). The chapter changes by itself.
- `wardrobe.html` — brands per shoot in LOOKS at the top.
- `ask.html` — your answers in ANSWERS at the top.
- `ask.html` and `capsule.html` switch on when the worker address is set in `extra.js` (API) — the same worker as the guestbook (`cloudflare/guestbook-worker.js`).
