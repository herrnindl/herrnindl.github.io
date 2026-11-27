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

ember · ber · vanilla-2 · vanilla · grey · navy-blue · lavendel · baby-blue · white · origin

## Faces (photos/faces.json)

Where the face is in each photo: `"photo path": [x, y, size, ok]` (0–1, from the top left).
Crops on the site and in the games keep the face in view. `ok` = 0 means no clear face
(back view, landscape, detail): the photo stays in the galleries but not in the games.
New photos without a line still work, they are just cropped from the middle and left out of the games.

## Small pages

- `wardrobe.html` — brands per shoot in LOOKS at the top.
- `ask.html` — your answers in ANSWERS at the top.
- `ask.html` switches on when the worker address is set in `extra.js` (API) — the same worker as the guestbook (`cloudflare/guestbook-worker.js`).

## Highlight stories (highlights/)

Every story from the Instagram highlights, one folder per chapter (`highlights/vanilla/`, `highlights/ember/` …), and nothing that isn't in a highlight.
File names are the moment the story went up (`2026-04-15_144121.jpg`), so they sort by time and "on this day" knows their date.
Updated on the 1st of every month from a fresh Instagram export; put the date in `highlights/info.txt` (`updated: 01.12.26`).
Trips take their stories from here: `stories: vanilla 2026-04-15_144121 – 2026-04-23_173007` in the trip's info.txt.
