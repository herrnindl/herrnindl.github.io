/* shared bits for the small pages: chapters (same as index.html), page colour, menu and footer */
const CHAPTERS = [
  { id: "red",       label: "red.",        bg: "#B3202A", fg: "#FFF8BB", line: "the fire" },
  { id: "ember",     label: "ember.",      bg: "#E9A283", fg: "#3A1E14", line: "the spark" },
  { id: "ber",       label: "ber.",        bg: "#B8C98B", fg: "#234C3D", line: "septem·ber to decem·ber" },
  { id: "vanilla-2", label: "vanilla. II", bg: "#B8B05F", fg: "#24220F", line: "i mog di" },
  { id: "vanilla",   label: "vanilla.",    bg: "#FFF8BB", fg: "#1C1C14", line: "a new colour" },
  { id: "grey",      label: "grey.",       bg: "#A9A9A9", fg: "#262626", line: "searching for vanilla" },
  { id: "navy-blue", label: "navy blue.",  bg: "#343A4E", fg: "#E8EAF0", line: "the end?" },
  { id: "lavendel",  label: "lavendel.",   bg: "#BAB6DE", fg: "#2A2342", line: "love" },
  { id: "baby-blue", label: "baby blue.",  bg: "#91B2EB", fg: "#1D2547", line: "the beginning" },
  { id: "white",     label: "white.",      bg: "#FFFFFF", fg: "#1A1A1A", line: "my first photoshoot" },
  { id: "origin",    label: "origin.",     bg: "#000000", fg: "#FFFFFF", line: "my 22nd birthday" },
];
/* address of the Cloudflare worker (cloudflare/guestbook-worker.js) — the same one as GB_API in index.html.
   While it is empty, ask me. shows "opens soon." and send nothing. */
const API = "https://mn-dots.herrnindl.workers.dev";
const byId = Object.fromEntries(CHAPTERS.map(c => [c.id, c]));
const $ = id => document.getElementById(id);
const el = (t, c, txt) => { const e = document.createElement(t); if (c) e.className = c; if (txt != null) e.textContent = txt; return e; };

let painted = null;
window.addEventListener("mn-dark", () => paint(painted));
function paint(c) {
  painted = c || null;
  c = c || (window.mnDark && mnDark() ? { bg: "#1C1C14", fg: "#FFF8BB" } : { bg: "#FFF8BB", fg: "#1C1C14" });
  const h = c.fg, r = parseInt(h.slice(1, 3), 16), g = parseInt(h.slice(3, 5), 16), b = parseInt(h.slice(5, 7), 16), s = document.documentElement.style;
  s.setProperty("--bg", c.bg); s.setProperty("--fg", c.fg);
  s.setProperty("--soft", `rgba(${r},${g},${b},.62)`); s.setProperty("--line", `rgba(${r},${g},${b},.18)`);
  const m = document.querySelector('meta[name="theme-color"]'); if (m) m.content = c.bg;
}

/* menu + footer: menu.js */

/* photos.json from the site build (only photos with a clearly visible face for close crops) */
const loadPhotos = () => fetch("photos.json", { cache: "no-cache" }).then(r => r.json()).then(l => l.filter(p => !p.video && byId[p.chapter])).catch(() => []);
const big = p => p.thumb2 || p.thumb || p.src;
