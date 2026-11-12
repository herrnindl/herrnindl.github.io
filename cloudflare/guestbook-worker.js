/*
  MN. guestbook — "leave a dot."
  Runs as a Cloudflare Worker with one KV namespace bound as DOTS.
  GET  → list of dots   [{ c: "#E9A283", n: "anna", t: 1731400000000 }, …]
  POST → { c, n }       adds one dot, returns the new list
  Stored per dot: colour, optional first name, time. Nothing else.
  The visitor's IP is only used as a one-way hash for 24 h to stop spam, then deleted automatically.
  To remove a dot: Cloudflare → Workers & Pages → KV → DOTS → key "all" → edit the list.
*/
const ORIGINS = ["https://herrnindl.com", "https://www.herrnindl.com", "https://herrnindl.github.io"];
const COLOURS = ["#000000", "#FFFFFF", "#91B2EB", "#BAB6DE", "#343A4E", "#A9A9A9", "#FFF8BB", "#B8B05F", "#B8C98B", "#E9A283", "#B3202A"];
const MAX = 3000;

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

    const list = JSON.parse((await env.DOTS.get("all")) || "[]");
    if (req.method === "GET") return json(list);
    if (req.method !== "POST") return json({ error: "method" }, 405);
    if (!ORIGINS.includes(origin)) return json({ error: "origin" }, 403);

    let body = {};
    try { body = await req.json(); } catch (e) { return json({ error: "body" }, 400); }
    const c = String(body.c || "").toUpperCase();
    if (!COLOURS.includes(c)) return json({ error: "colour" }, 400);
    const n = String(body.n || "").replace(/[^\p{L}\p{N} .\-_']/gu, "").trim().slice(0, 20);

    const ip = req.headers.get("CF-Connecting-IP") || "";
    const h = [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(ip + new Date().toISOString().slice(0, 10))))].map(b => b.toString(16).padStart(2, "0")).join("");
    if (await env.DOTS.get("ip:" + h)) return json({ error: "once a day" }, 429);
    await env.DOTS.put("ip:" + h, "1", { expirationTtl: 86400 });

    list.push({ c, n, t: Date.now() });
    while (list.length > MAX) list.shift();
    await env.DOTS.put("all", JSON.stringify(list));
    return json(list);
  },
};
