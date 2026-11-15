/* On every page except the start page: tap the MN. logo five times and something happens.
   One tap still goes to the start page (after a short wait, so quick taps can be counted).
   Also adds the small hint line at the bottom of the page. */
(function () {
  const st = document.createElement("style");
  st.textContent = ".egg{position:fixed;inset:0;z-index:55;pointer-events:none;overflow:hidden}.egg i{position:absolute;top:-30px;border-radius:50%}.egg p{position:absolute;left:50%;top:42%;transform:translate(-50%,-50%);margin:0;padding:12px 20px;border-radius:999px;background:#1C1C14;color:#FFE135;font-weight:500;letter-spacing:-.01em;white-space:nowrap}.eggnote{display:block;flex-basis:100%;margin-top:6px;font-size:11px;letter-spacing:.14em;opacity:.6}";
  document.head.append(st);
  const COLS = ["#FFE135", "#B3202A", "#E9A283", "#B8C98B", "#B8B05F", "#FFF8BB", "#A9A9A9", "#343A4E", "#BAB6DE", "#91B2EB"];
  const calm = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  function rain() {
    if (document.querySelector(".egg")) return;
    const w = document.createElement("div"); w.className = "egg";
    const n = calm() ? 0 : 70;
    for (let i = 0; i < n; i++) {
      const d = document.createElement("i"), s = 8 + Math.random() * 18;
      d.style.cssText = `left:${Math.random() * 100}%;width:${s}px;height:${s}px;background:${COLS[i % COLS.length]};box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)`;
      w.append(d);
      d.animate([{ transform: "translateY(0)" }, { transform: `translate(${(Math.random() - .5) * 120}px, ${innerHeight + 60}px)` }], { duration: 1400 + Math.random() * 1400, delay: Math.random() * 900, easing: "cubic-bezier(.3,.1,.6,1)", fill: "forwards" });
    }
    const m = document.createElement("p"); m.textContent = "you found it. thank you for being early."; w.append(m);
    m.animate([{ opacity: 0, transform: "translate(-50%,-40%)" }, { opacity: 1, transform: "translate(-50%,-50%)" }], { duration: 300, fill: "both" });
    document.body.append(w);
    setTimeout(() => w.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 500, fill: "forwards" }).onfinish = () => w.remove(), 3600);
  }
  const mark = document.querySelector("a.mark, #mark");
  if (mark) {
    let taps = 0, timer = null;
    mark.addEventListener("click", e => {
      e.preventDefault(); taps++; clearTimeout(timer);
      if (taps >= 5) { taps = 0; rain(); return; }
      timer = setTimeout(() => { const one = taps === 1; taps = 0; if (one) location.href = mark.getAttribute("href") || "./"; }, 450);
    });
  }
  const foot = document.querySelector("footer");
  if (foot && !foot.querySelector(".eggnote")) { const n = document.createElement("span"); n.className = "eggnote"; n.textContent = "tap the MN. logo 5 times. something will happen."; foot.append(n); }
})();
