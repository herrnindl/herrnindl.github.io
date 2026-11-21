/* small "preview." tag next to the MN. logo while the site is behind the password.
   Switches itself off on launch day (01.12.2026), nothing to remove. */
(function () {
  if (Date.now() >= Date.parse("2026-12-01T00:00:00+01:00")) return;
  var s = document.createElement("style");
  s.textContent = ".mark .pv { font-family: Inter, 'Helvetica Neue', Arial, sans-serif; font-weight: 500; font-size: 9px; letter-spacing: .32em; color: var(--soft, rgba(28,28,20,.62)); margin-left: 10px; vertical-align: .55em; user-select: none; }";
  document.head.appendChild(s);
  var add = function () {
    document.querySelectorAll("a.mark").forEach(function (m) {
      if (m.querySelector(".pv")) return;
      var t = document.createElement("small"); t.className = "pv"; t.textContent = "preview."; m.appendChild(t);
    });
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", add); else add();
})();
