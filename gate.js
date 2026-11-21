/* Pages behind the coming-soon password: without it, go to the coming-soon page. */
(function () {
  var ok = false;
  try { ok = localStorage.getItem("mn-key") === "7c362ae2f50e8da10d4c1c903cfb236edc7d09f40cc5eb2f749f9d0fb78aebd4"; } catch (e) {}
  if (Date.now() >= Date.parse("2026-12-01T00:00:00+01:00")) ok = true;   /* open for everyone from 01.12.2026 */
  if (!ok) { document.documentElement.style.visibility = "hidden"; location.replace("./"); }
})();
