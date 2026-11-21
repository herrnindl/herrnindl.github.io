/* dark mode: vanilla text on ink instead of ink on vanilla.
   Follows the phone's setting until someone taps "dark mode." in the footer; then that choice is kept.
   Only the vanilla base changes: chapter colours stay as they are. */
(function () {
  var html = document.documentElement, KEY = "mn-dark";
  var saved = null; try { saved = localStorage.getItem(KEY); } catch (e) {}
  var mq = window.matchMedia ? matchMedia("(prefers-color-scheme: dark)") : null;
  var on = saved === "1" || (saved !== "0" && !!(mq && mq.matches));
  var css = document.createElement("style");
  css.textContent =
    "html.dark{--bg:#1C1C14;--fg:#FFF8BB;--soft:rgba(255,248,187,.62);--line:rgba(255,248,187,.16);--dot:#FFF8BB;color-scheme:dark}" +
    "html.dark body{background:var(--bg);color:var(--fg)}" +
    /* things that are ink on vanilla turn vanilla on ink, so they don't disappear */
    "html.dark [style*='--b:#1C1C14']{--b:#FFF8BB!important;--t:#1C1C14!important}" +
    "html.dark .gate button,html.dark .skip{background:#FFF8BB!important;color:#1C1C14!important}" +
    "html.dark .ticker .tape.b{background:#FFF8BB;color:#1C1C14}" +
    "html.dark .reveal-btn,html.dark .wrapcard,html.dark .embed,html.dark .frame,html.dark .mixphoto{box-shadow:inset 0 0 0 1px rgba(255,248,187,.22)}" +
    "html.dark nav.sub a{border-color:var(--line)!important}" +
    /* the password screen and the welcome, dark too */
    "html.dark.locked body,html.dark .gate{background:#1C1C14!important;color:#FFF8BB!important}" +
    "html.dark .gate input{border-color:rgba(255,248,187,.3)!important;background:rgba(255,248,187,.06)!important;color:#FFF8BB!important}" +
    "html.dark .gate input::placeholder{color:rgba(255,248,187,.4)}" +
    "html.dark .gate .msg,html.dark .gate .glinks,html.dark .gate .glinks a{color:rgba(255,248,187,.6)!important}" +
    "html.dark .gate .gdots i{box-shadow:inset 0 0 0 1px rgba(255,248,187,.3)}" +
    ".darkbtn{font:inherit;letter-spacing:inherit;text-transform:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer;text-decoration:underline;text-decoration-color:var(--line);text-decoration-thickness:1px;text-underline-offset:5px}";
  document.head.appendChild(css);

  function themeColor() {
    var m = document.querySelector('meta[name="theme-color"]');
    if (m && !m.dataset.chapter) m.content = on ? "#1C1C14" : "#FFF8BB";
  }
  function apply() {
    html.classList.toggle("dark", on);
    themeColor();
    try { window.dispatchEvent(new Event("mn-dark")); } catch (e) {}
    document.querySelectorAll(".darkbtn").forEach(function (b) { b.textContent = on ? "light mode." : "dark mode."; });
  }
  window.mnDark = function () { return on; };
  apply();
  if (mq && mq.addEventListener) mq.addEventListener("change", function (e) { if (saved === null) { on = e.matches; apply(); } });

  function addButton() {
    var f = document.querySelector("footer"); if (!f || f.querySelector(".darkbtn")) return;
    var b = document.createElement("button"); b.type = "button"; b.className = "darkbtn";
    b.onclick = function () {
      on = !on; saved = on ? "1" : "0";
      try { localStorage.setItem(KEY, saved); } catch (e) {}
      apply();
    };
    var l = f.querySelector('a[href$="datenschutz.html"], a[href$="impressum.html"]');
    var row = l && l.parentElement !== f ? l.parentElement : f;
    if (row !== f) { row.appendChild(document.createTextNode(" · ")); row.appendChild(b); }
    else { var s = document.createElement("span"); s.appendChild(b); f.appendChild(s); }
    apply();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", addButton); else addButton();
  /* glowup fills its footer later */
  setTimeout(addButton, 1500);
})();
