/* Visitor stats with Cloudflare Web Analytics (no cookies).
   Open herrnindl.com/#me once on your own devices to stop counting them; #notme undoes it. */
(function () {
  try {
    if (location.hash === "#me") { localStorage.setItem("mn-me", "1"); history.replaceState(null, "", location.pathname); }
    if (location.hash === "#notme") { localStorage.removeItem("mn-me"); history.replaceState(null, "", location.pathname); }
    if (localStorage.getItem("mn-me") === "1") return;
  } catch (e) {}
  var s = document.createElement("script");
  s.defer = true;
  s.src = "https://static.cloudflareinsights.com/beacon.min.js";
  s.setAttribute("data-cf-beacon", '{"token": "6a462ce262f74e0289e70f16930588a0"}');
  document.head.appendChild(s);
})();
