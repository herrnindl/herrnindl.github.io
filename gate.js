/* Pages behind the coming-soon password: without it, go to the coming-soon page. */
(function () {
  var ok = false;
  try { ok = localStorage.getItem("mn-key") === "1e39f3691a7dcd34ef2e5d19e3fd1f640ed375443b8c539ddf54581276657502"; } catch (e) {}
  if (Date.now() >= Date.parse("2026-12-01T00:00:00+01:00")) ok = true;   /* open for everyone from 01.12.2026 */
  if (!ok) { document.documentElement.style.visibility = "hidden"; location.replace("./"); }
})();
