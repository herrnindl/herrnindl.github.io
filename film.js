/* The film: when nobody touches the site for 40 seconds, the chapters play one after the other.
   Shared by the start page and the small pages. Tap anywhere to go back to where you were.
   Not loaded on impressum, datenschutz and lebenslauf on purpose.
   It waits while someone is typing, while a game is running (play.html) or while a photo or sheet is open (start page). */
window.MN_BEST = {"origin": ["origin-06.jpg", "origin-02.jpg", "origin-08.jpg"], "white": ["250223-Studioportrait-alpindis.at-0292-Bearbeitet.jpg", "lake-00275.jpg", "lake-00301.jpg"], "baby-blue": ["wekreat-01b.jpg", "wekreat-05b.jpg", "wekreat-07b.jpg"], "lavendel": ["0V4A0304.jpg", "2025-06-17_00009.jpg", "0V4A0231.jpg"], "navy-blue": ["0V4A9118x_1.jpg", "0V4A9324x_1.jpg", "0V4A9240x_1x.jpg"], "vanilla-2": ["2026-07-08_033.jpg", "MP_2026_Brand-Shootings_Markus-Nindl_072.jpg", "MP_2026_Brand-Shootings_Markus-Nindl_046.jpg"], "ber": ["2026-07-08_154.jpg", "MP_2026_Brand-Shootings_Markus-Nindl_012.jpg", "2026-07-08_178.jpg"]};
(function () {
  /* the chapters, oldest first: the start page uses its own list, the small pages this copy (keep it the same as CHAPTERS in index.html) */
  const OWN = [
    { id: "origin",    name: "origin",     bg: "#000000", fg: "#FFFFFF", dates: "26.08.24 – 02.03.25", line: "my 22nd birthday", place: "pinzgau",
      notes: ["instagram opened", "3 platzhirsch articles", "MN. 01.01.25", "the first pictures"] },
    { id: "white",     name: "white",      bg: "#FFFFFF", fg: "#1A1A1A", dates: "03.03. – 22.05.25", line: "my first photoshoot", place: "neukirchen" },
    { id: "baby-blue", name: "baby blue",  bg: "#91B2EB", fg: "#1D2547", dates: "23.05. – 23.06.25", line: "the beginning", place: "fürstenfeld · graz" },
    { id: "lavendel",  name: "lavendel",   bg: "#BAB6DE", fg: "#2A2342", dates: "07.07. – 07.09.25", line: "love", place: "italia" },
    { id: "navy-blue", name: "navy blue",  bg: "#343A4E", fg: "#E8EAF0", dates: "21.10. – 21.12.25", line: "the end?", place: "dublin" },
    { id: "grey",      name: "grey",       bg: "#A9A9A9", fg: "#262626", dates: "01.01. – 31.03.26", line: "searching for vanilla", place: "munich" },
    { id: "vanilla",   name: "vanilla",    bg: "#FFF8BB", fg: "#1C1C14", dates: "01.04. – 22.06.26", line: "a new colour", place: "france" },
    { id: "vanilla-2", name: "vanilla",    suffix: " II", bg: "#B8B05F", fg: "#24220F", dates: "23.06. – 31.08.26", line: "i mog di", place: "königsleiten · salzburg" },
    { id: "ber",       name: "ber",        bg: "#B8C98B", fg: "#234C3D", dates: "01.09. – 31.10.26", line: "septem·ber to decem·ber", vanilla: true },
    { id: "ember",     name: "ember",      bg: "#E9A283", fg: "#3A1E14", dates: "01.11. – 31.12.26", line: "the spark", place: "wildkogel", vanilla: true },
  ];
  const chapters = () => (typeof CHAPTERS !== "undefined" && CHAPTERS[0] && CHAPTERS[0].dates) ? CHAPTERS : OWN;
  const BEST = window.MN_BEST;
  const el = (t, c, txt) => { const e = document.createElement(t); if (c) e.className = c; if (txt != null) e.textContent = txt; return e; };
  const facePos = (img, it) => { if (it && it.f) img.style.objectPosition = Math.round(it.f[0] * 100) + "% " + Math.round(it.f[1] * 100) + "%"; };
  const calm = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

  const st = document.createElement("style");
  st.textContent = `.film { position: fixed; inset: 0; z-index: 45; display: grid; place-items: center; background: var(--fb, #000); color: var(--ff, #fff); cursor: none; overflow: hidden; contain: strict; }
.film .fwash { position: absolute; inset: 0; will-change: transform, opacity; }
.film .fbomb { position: absolute; border-radius: 50%; will-change: transform; backface-visibility: hidden; }
.film .fin { grid-area: 1 / 1; position: relative; z-index: 1; display: grid; justify-items: center; gap: 12px; text-align: center; padding: 24px; }
.film .fph { width: min(54vw, 300px); aspect-ratio: 4 / 5; border-radius: 8px; overflow: hidden; box-shadow: 0 30px 60px -30px rgba(0,0,0,.6); will-change: transform, opacity; }
.film .fph img { width: 100%; height: 100%; object-fit: cover; display: block; }
.film .fdates { font-size: 12px; letter-spacing: .3em; opacity: .8; }
.film b { font-weight: 800; font-size: clamp(56px, 16vw, 150px); letter-spacing: -.06em; line-height: .86; padding-bottom: .16em; white-space: nowrap; will-change: transform; }
.film b .fc { display: inline-block; white-space: pre; font-style: normal; will-change: transform, opacity; }
.film .fspark { position: absolute; border-radius: 50%; z-index: 2; pointer-events: none; box-shadow: 0 0 8px 1px rgba(255,220,140,.6); will-change: transform, opacity; }
.film .fline { font-size: clamp(16px, 4vw, 22px); opacity: .85; }
.film .fhint { z-index: 4; color: var(--ff); transition: color .9s ease; position: absolute; bottom: calc(18px + env(safe-area-inset-bottom, 0px)); left: 0; right: 0; text-align: center; font-size: 11px; letter-spacing: .24em; opacity: .55; }`;
  document.head.append(st);

  /* photos.json from the site build, loaded once, the first time the film is needed */
  let photos = [], loading = null;
  const load = () => loading || (loading = fetch("photos.json", { cache: "no-cache" }).then(r => r.json()).then(d => { photos = d.filter(p => !p.video); }).catch(() => { loading = null; }));

  let filmTimer = 0, filmOn = null;
  const typing = () => { const a = document.activeElement; return !!a && (a.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)); };
  const filmReady = () => document.visibilityState === "visible" && !calm() && !typing()
    && !document.documentElement.classList.contains("locked")
    && !document.querySelector(".wrapped, .launch, .egg, .film, dialog[open]")
    && !(window.mnFilmBlock && window.mnFilmBlock());
  function armFilm() {
    clearTimeout(filmTimer); if (filmOn) return;
    filmTimer = setTimeout(() => {
      if (!filmReady()) { armFilm(); return; }
      load().then(() => { if (!filmOn && filmReady() && photos.length) playFilm(); else armFilm(); });
    }, 40000);
  }
  const isBest = p => (BEST[p.chapter] || []).includes(p.src.split("/").pop());
  const lastFilm = {};
/* The screensaver: one chapter after the other, and every handover means something.
   dot   – the dot after the name takes on the next colour and grows until it is everything
   fade  – one colour melts into the next            blind – the next colour comes down like a blind
   dim   – the lights go down and come back up        morph – the word stays and becomes the next word
   Everything moves with transform and opacity only, and the next photo is loaded before its turn, so nothing stutters or pops. */
const FILM_TRANS = { "baby-blue>lavendel": "fade", "lavendel>navy-blue": "blind", "navy-blue>grey": "dim" };
function playFilm() {
  if (filmOn) return;
  const f = el("div", "film"); f.setAttribute("role", "dialog"); f.setAttribute("aria-label", "my life in colours. — tap to stop");
  const hint = el("div", "fhint", "TAP ANYWHERE TO GO BACK"); f.tabIndex = -1; f.append(hint); document.body.append(f); f.focus({ preventScroll: true });
  let dead = false; const timers = new Set();
  const wait = ms => new Promise(r => { const t = setTimeout(() => { timers.delete(t); r(); }, ms); timers.add(t); });
  const fin = a => a.finished.catch(() => {});
  const OUT = "cubic-bezier(.5,0,.8,.4)", IN = "cubic-bezier(.16,.84,.3,1)", MOVE = "cubic-bezier(.65,0,.2,1)";
  const paint = c => { f.style.setProperty("--fb", c.bg); f.style.setProperty("--ff", c.fg); };

  /* the photo for a chapter, loaded and decoded before it is needed */
  const pick = c => {
    const all = photos.filter(p => p.chapter === c.id && !p.video);
    const inColour = all.filter(p => (p.cm || 0) >= .06).sort((a, b) => b.cm - a.cm).slice(0, 3);
    const top = inColour.length ? inColour : all.filter(isBest);
    let pics = top.length ? top : all; if (pics.length > 1) pics = pics.filter(p => p !== lastFilm[c.id]);
    if (!pics.length) return Promise.resolve(null);
    const p = pics[Math.floor(Math.random() * pics.length)]; lastFilm[c.id] = p;
    const im = new Image(); im.alt = ""; facePos(im, p); im.src = p.thumb2 || p.thumb || p.src;
    return Promise.race([im.decode().then(() => im, () => im), new Promise(r => setTimeout(() => r(im.complete && im.naturalWidth ? im : null), 2500))]);
  };
  /* a chapter's card: photo, dates, the name letter by letter, its line */
  const card = (c, im) => {
    const box = el("div", "fin"); box.style.color = c.fg;
    const b = el("b"), toks = [], add = (ch, cls) => { const x = el(cls ? "i" : "span", "fc" + (cls ? " " + cls : ""), ch); b.append(x); toks.push(x); return x; };
    [...c.name].forEach(ch => add(ch)); const dot = add(".", "fdot"); if (c.suffix) [...c.suffix].forEach(ch => add(ch));
    const meta = [];
    if (im) { const ph = el("div", "fph"); ph.append(im); box.append(ph); meta.push(ph); }
    const dates = el("small", "fdates", c.dates.toUpperCase()), line = el("span", "fline", c.line);
    box.append(dates, b, line); meta.splice(im ? 1 : 0, 0, dates); meta.push(line);
    return { c, box, b, toks, dot, meta, im, str: c.name + "." + (c.suffix || "") };
  };
  /* letters rise in one after the other, the dot lands last, then the rest follows */
  const enter = (k, at = 0, only) => {
    const ls = only || k.toks.filter(t => t !== k.dot); let t = at;
    ls.forEach((x, n) => x.animate([{ opacity: 0, transform: "translateY(.38em)" }, {}], { duration: 620, delay: t + n * 42, easing: IN, fill: "backwards" }));
    t += ls.length * 42 + 180;
    if (!only) k.dot.animate([{ opacity: 0, transform: "scale(0)" }, { opacity: 1, transform: "scale(1.35)", offset: .6 }, {}], { duration: 420, delay: t, easing: "ease-out", fill: "backwards" });
    k.meta.forEach((x, n) => x.animate([{ opacity: 0, transform: "translateY(12px)" }, {}], { duration: 800, delay: at + 260 + n * 110, easing: IN, fill: "backwards" }));
  };
  /* where the ink of the dot really is: its exact centre and size, whatever the layout (photo or not, long name or short) */
  const dotInk = k => {
    const cs = getComputedStyle(k.b), fs = parseFloat(cs.fontSize), r = k.dot.getBoundingClientRect();
    const probe = el("span"); probe.style.cssText = "display:inline-block;width:0;height:0;vertical-align:baseline"; k.dot.before(probe);
    const base = probe.getBoundingClientRect().bottom; probe.remove();
    const cv = dotInk.cv || (dotInk.cv = document.createElement("canvas").getContext("2d")); cv.font = cs.fontWeight + " " + fs + "px " + cs.fontFamily;
    const m = cv.measureText(".");
    return { x: r.left + (m.actualBoundingBoxRight - m.actualBoundingBoxLeft) / 2, y: base + (m.actualBoundingBoxDescent - m.actualBoundingBoxAscent) / 2, d: m.actualBoundingBoxAscent + m.actualBoundingBoxDescent };
  };
  const leave = (els, ms = 460) => els.map((x, n) => x.animate([{}, { opacity: 0, transform: "translateY(-12px)" }], { duration: ms, delay: n * 40, easing: OUT, fill: "forwards" }));
  const layer = (cls, bg, z) => { const w = el("div", cls); w.style.background = bg; w.style.zIndex = z; f.insertBefore(w, hint); return w; };

  const handover = async (old, c, im) => {
    const kind = FILM_TRANS[old.c.id + ">" + c.id] || ((c.name + "." + (c.suffix || "")).includes(old.str) ? "morph" : "dot");
    const W = innerWidth, H = innerHeight, k = card(c, im);
    const swap = w => { paint(c); old.box.remove(); if (w) w.remove(); };
    if (kind === "dot") {
      /* the dot turns into the next colour, takes a breath, and grows over everything */
      const { x: ox, y: oy, d } = dotInk(old);   /* measured, so it sits exactly on the dot wherever the name stands */
      const big = 2 * Math.hypot(Math.max(ox, W - ox), Math.max(oy, H - oy)) + 40, s0 = (d * 1.1 + 1) / big;   /* a hair bigger than the dot, so it covers it completely */
      const w = layer("fbomb", c.bg, 3); w.style.cssText += `;left:${ox}px;top:${oy}px;width:${big}px;height:${big}px`;
      const T = "translate(-50%,-50%) scale(";
      await fin(w.animate([{ transform: T + s0 + ")", opacity: 0 }, { transform: T + s0 + ")", opacity: 1, offset: .14 }, { transform: T + s0 * 2.4 + ")", opacity: 1, offset: .36, easing: "cubic-bezier(.7,0,.25,1)" }, { transform: T + "1)", opacity: 1 }], { duration: 1500, fill: "forwards" }));
      if (dead) return k; swap(w); f.insertBefore(k.box, hint); enter(k, 60);
    } else if (kind === "blind") {
      const w = layer("fwash", c.bg, 3);
      await fin(w.animate([{ transform: "translateY(-101%)" }, { transform: "none" }], { duration: 1100, easing: MOVE, fill: "forwards" }));
      if (dead) return k; swap(w); f.insertBefore(k.box, hint); enter(k, 60);
    } else if (kind === "dim") {
      /* the lights go down … */
      leave(old.meta.concat(old.b), 700);
      const w = layer("fwash", "#000", 3);
      await fin(w.animate([{ opacity: 0 }, { opacity: .62 }], { duration: 760, easing: "ease-in", fill: "forwards" }));
      if (dead) return k; paint(c); old.box.remove(); f.insertBefore(k.box, hint); enter(k, 420);
      /* … and come back up in the next colour */
      fin(w.animate([{ opacity: .62 }, { opacity: 0 }], { duration: 900, easing: "ease-out", fill: "forwards" })).then(() => w.remove());
    } else if (kind === "fade") {
      leave(old.meta.concat(old.b), 520);
      const w = layer("fwash", c.bg, 0);
      await fin(w.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 1100, easing: "ease-in-out", fill: "forwards" }));
      if (dead) return k; swap(w); f.insertBefore(k.box, hint); enter(k, 0);
    } else if (kind === "morph") {
      /* the word stays where it is, the colour changes around it, and the new letters join it */
      const at = k.str.indexOf(old.str); f.insertBefore(k.box, hint);
      const a0 = old.toks[0].getBoundingClientRect(), b0 = k.toks[at].getBoundingClientRect();
      old.b.style.visibility = "hidden"; leave(old.meta);
      const w = layer("fwash", c.bg, 0); w.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 1200, easing: "ease-in-out", fill: "forwards" });
      k.box.animate([{ color: old.c.fg }, {}], { duration: 1200, easing: "ease-in-out", fill: "backwards" });
      k.b.animate([{ transform: `translate(${a0.left - b0.left}px, ${a0.top - b0.top}px)` }, { transform: "none" }], { duration: 1150, delay: 150, easing: MOVE, fill: "backwards" });
      const fresh = k.toks.slice(0, at).reverse().concat(k.toks.slice(at + old.toks.length));   /* the letter next to the word comes first */
      fresh.forEach((x, n) => x.animate([{ opacity: 0, transform: `translateX(${k.toks.indexOf(x) < at ? "-.3em" : ".3em"})` }, {}], { duration: 700, delay: 850 + n * 110, easing: IN, fill: "backwards" }));
      k.meta.forEach((x, n) => x.animate([{ opacity: 0, transform: "translateY(12px)" }, {}], { duration: 800, delay: 1250 + n * 110, easing: IN, fill: "backwards" }));
      await wait(1350); if (dead) return k; swap(w); await wait(700);
    } else {   /* spark */
      leave(old.meta);
      old.toks.forEach((x, n) => x.animate([{ color: old.c.fg }, { color: "#FFE9B0", opacity: 1, transform: "none", offset: .4 }, { color: "#FFE9B0", opacity: 0, transform: "translateY(-.4em) scale(.86)" }], { duration: 700, delay: 150 + n * 95, easing: "ease-in", fill: "forwards" }));
      const w = layer("fwash", c.bg, 0); w.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 1500, delay: 350, easing: "ease-in-out", fill: "both" });
      for (let n = 0; n < 34; n++) {   /* embers rise */
        const sp = el("i", "fspark"), size = 2 + Math.random() * 4, far = H * (.35 + Math.random() * .6);
        sp.style.cssText = `left:${Math.random() * W}px;top:${H * (.5 + Math.random() * .55)}px;width:${size}px;height:${size}px;background:${Math.random() < .5 ? "#FFF8BB" : "#F6C46A"}`;
        f.insertBefore(sp, hint);
        sp.animate([{ transform: "translate(0,0)", opacity: 0 }, { opacity: 1, offset: .18 }, { transform: `translate(${(Math.random() - .5) * 140}px, ${-far}px)`, opacity: 0 }], { duration: 1700 + Math.random() * 1500, delay: 200 + Math.random() * 1100, easing: "cubic-bezier(.2,.5,.3,1)", fill: "both" }).onfinish = () => sp.remove();
      }
      await wait(1500); if (dead) return k; swap(null); f.insertBefore(k.box, hint);
      k.b.animate([{ transform: "scale(.9)" }, { transform: "none" }], { duration: 900, easing: IN });
      enter(k, 0); await wait(420); w.remove();
    }
    return k;
  };

  (async () => {
    /* on a chapter of the start page, the film begins with that chapter */
    const from = window.mnFilmFrom && window.mnFilmFrom();
    let i = Math.max(0, chapters().findIndex(x => x.id === from)), c = chapters()[i]; paint(c);
    f.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 600, easing: "ease-out" });
    let cur = card(c, await pick(c)); if (dead) return;
    f.insertBefore(cur.box, hint); enter(cur, 350);
    while (!dead) {
      const nx = chapters()[++i % chapters().length], im = pick(nx);
      await wait(3900); if (dead) return;
      cur = await handover(cur, nx, await im);
    }
  })();
  const stop = () => { dead = true; timers.forEach(clearTimeout); ["pointerdown", "keydown", "wheel", "touchstart"].forEach(ev => removeEventListener(ev, stop, true)); f.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 350, fill: "forwards" }).onfinish = () => f.remove(); filmOn = null; armFilm(); };
  filmOn = stop;
  setTimeout(() => ["pointerdown", "keydown", "wheel", "touchstart"].forEach(ev => addEventListener(ev, stop, true)), 300);
}
  ["pointermove", "pointerdown", "keydown", "scroll", "wheel", "touchstart", "input"].forEach(ev => addEventListener(ev, () => { if (!filmOn) armFilm(); }, { passive: true }));
  armFilm();
})();
