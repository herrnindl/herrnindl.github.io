/*
  MN. worker — one Cloudflare Worker with one KV namespace bound as DOTS. Three things:

  "leave a dot." (guestbook, start page)        path /
  GET  → list of dots   [{ c: "#E9A283", n: "anna", t: 1731400000000 }, …]
  POST → { c, n }       adds one dot, returns the new list

  "ask me." (ask.html)                          path /ask
  POST → { q }          stores the question privately (key "ask"). Nothing is shown on the site
                        until Markus answers it himself in ask.html.

  "time capsule." (capsule.html)                path /capsule
  GET  → { open, count, messages }   messages stay locked (empty) until 01.01.2027
  POST → { m, n }       stores one message (key "capsule")
  To read or delete questions/messages: Cloudflare → Workers & Pages → KV → DOTS → key "ask" / "capsule".

  Stored per dot: colour, optional first name, time. Nothing else.
  The visitor's IP is only used as a one-way hash for 24 h to stop spam, then deleted automatically.
  To remove a dot: Cloudflare → Workers & Pages → KV → DOTS → key "all" → edit the list.
*/
const ORIGINS = ["https://herrnindl.com", "https://www.herrnindl.com", "https://herrnindl.github.io"];
const COLOURS = ["#000000", "#FFFFFF", "#91B2EB", "#BAB6DE", "#343A4E", "#A9A9A9", "#FFF8BB", "#B8B05F", "#B8C98B", "#E9A283", "#B3202A"];
const MAX = 3000;
const OPENS = Date.parse("2027-01-01T00:00:00+01:00");
const clean = (v, n) => String(v || "").replace(/[\u0000-\u001f\u007f<>]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);

export default {
  async fetch(req, env) {
    const origin = req.headers.get("Origin") || "";
    const cors = {
      "Access-Control-Allow-Origin": ORIGINS.includes(origin) ? origin : ORIGINS[0],
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "content-type",
      "Vary": "Origin",
    };
    const json = (data, status = 200) => new Response(JSON.stringify(data), { status, headers: { ...cors, "content-type": "application/json", "cache-control": "no-store" } });
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });

    const path = new URL(req.url).pathname.replace(/\/+$/, "") || "/";
    /* one-way hash of the visitor's IP + day, kept 24 h, only to stop spam */
    const ip = req.headers.get("CF-Connecting-IP") || "";
    const h = [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(ip + new Date().toISOString().slice(0, 10))))].map(b => b.toString(16).padStart(2, "0")).join("");
    const limit = async (kind, max) => { const k = kind + ":" + h, n = +((await env.DOTS.get(k)) || 0); if (n >= max) return false; await env.DOTS.put(k, String(n + 1), { expirationTtl: 86400 }); return true; };
    let body = {};
    if (req.method === "POST") {
      if (!ORIGINS.includes(origin)) return json({ error: "origin" }, 403);
      try { body = await req.json(); } catch (e) { return json({ error: "body" }, 400); }
    } else if (req.method !== "GET") return json({ error: "method" }, 405);

    if (path === "/ask") {
      if (req.method !== "POST") return json({ error: "method" }, 405);
      const q = clean(body.q, 300);
      if (q.length < 3) return json({ error: "empty" }, 400);
      if (!(await limit("ask", 3))) return json({ error: "three a day" }, 429);
      const all = JSON.parse((await env.DOTS.get("ask")) || "[]");
      all.push({ q, t: Date.now() }); while (all.length > MAX) all.shift();
      await env.DOTS.put("ask", JSON.stringify(all));
      return json({ ok: true });
    }

    if (path === "/capsule") {
      const all = JSON.parse((await env.DOTS.get("capsule")) || "[]"), open = Date.now() >= OPENS;
      const view = () => ({ open, count: all.length, messages: open ? all.map(x => ({ m: x.m, n: x.n })) : [] });
      if (req.method === "GET") return json(view());
      if (open) return json({ error: "closed" }, 403);
      const m = clean(body.m, 280), n = clean(body.n, 20);
      if (m.length < 2) return json({ error: "empty" }, 400);
      if (!(await limit("cap", 1))) return json({ error: "once a day" }, 429);
      all.push({ m, n, t: Date.now() }); while (all.length > MAX) all.shift();
      await env.DOTS.put("capsule", JSON.stringify(all));
      return json(view());
    }

    const list = JSON.parse((await env.DOTS.get("all")) || "[]");
    if (req.method === "GET") return json(list);
    const c = String(body.c || "").toUpperCase();
    if (!COLOURS.includes(c)) return json({ error: "colour" }, 400);
    const n = String(body.n || "").replace(/[^\p{L}\p{N} .\-_']/gu, "").trim().slice(0, 20);

    if (!(await limit("ip", 1))) return json({ error: "once a day" }, 429);

    list.push({ c, n, t: Date.now() });
    while (list.length > MAX) list.shift();
    await env.DOTS.put("all", JSON.stringify(list));
    return json(list);
  },
};
