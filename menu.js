/* the start page's menu on every small page, with play. glow up. wardrobe. ask me. leave a dot. as sub tabs under "more.",
   and the start page's footer. Put <script src="menu.js"></script> right after the page's <header> and <nav class="more">. */
(function () {
  var here = location.pathname.split("/").pop() || "index.html";
  var MAIN = [["./", "colours."], ["./#posts", "posts.", "posts"], ["./#about", "about."], ["./#sedcard", "for brands."],
              ["./#booking", "book."], ["./#journal", "journal.", "journal"], ["play.html", "more.", "more"], ["dots.html", "leave a dot."]];
  var SUB = [["play.html", "play."], ["wardrobe.html", "wardrobe."], ["./#recaps", "recaps."], ["glowup.html", "glow up."], ["ask.html", "ask me."]];
  var inSub = SUB.some(function (s) { return s[0] === here; });
  var mainHere = inSub ? "play.html" : (here === "dots.html" ? "dots.html" : "");

  /* header: MN. left, the name right (like the start page) */
  var head = document.querySelector(".wrap > header");
  if (head) {
    head.classList.add("mn-head");
    var right = document.createElement("span"); right.className = "hright";
    var back = head.querySelector(".back"); if (back) right.appendChild(back);
    var nm = document.createElement("span"); nm.className = "name"; nm.innerHTML = "M A R K U S&nbsp;&nbsp;N I N D L"; right.appendChild(nm);
    head.appendChild(right);
  }

  /* main menu */
  var old = document.querySelector("nav.more");
  var nav = document.createElement("nav"); nav.className = "mn-views"; nav.setAttribute("aria-label", "Sections");
  MAIN.forEach(function (m) {
    var a = document.createElement("a"); a.href = m[0]; a.textContent = m[1];
    if (m[0] === mainHere) a.setAttribute("aria-current", "page");
    if (m[2]) a.dataset.new = m[2];
    if (m[1] === "posts.") { a.hidden = true; a.dataset.posts = "1"; }   /* like the start page: only once there is a post */
    nav.appendChild(a);
  });
  if (old) old.replaceWith(nav); else if (head) head.after(nav);

  /* sub tabs */
  if (inSub) {
    var sub = document.createElement("nav"); sub.className = "mn-sub"; sub.setAttribute("aria-label", "more");
    SUB.forEach(function (s) {
      var a = document.createElement("a"); a.href = s[0]; a.textContent = s[1];
      if (s[0] === here) a.setAttribute("aria-current", "page");
      sub.appendChild(a);
    });
    nav.after(sub);
  }

  var cur = nav.querySelector("[aria-current]");
  if (cur) nav.scrollLeft = Math.max(0, cur.offsetLeft + cur.offsetWidth - nav.clientWidth + 36);   /* only as far as needed, like the start page */
  var fade = function () { nav.classList.toggle("end", nav.scrollLeft + nav.clientWidth >= nav.scrollWidth - 4); };
  nav.addEventListener("scroll", fade, { passive: true }); window.addEventListener("resize", fade); fade();

  fetch("sets.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (s) {
    if (s.posts && s.posts.length) { nav.querySelector("[data-posts]").hidden = false; fade(); }
    if (window.mnNew) window.mnNew(s, inSub ? "more" : null);
  }).catch(function () {});

  /* footer: exactly the start page's */
  var fill = function () {
    var f = document.querySelector("footer.foot"); if (!f || f.dataset.mn) return; f.dataset.mn = "1";
    var dk = f.querySelector(".darkbtn");   /* dark mode. (from dark.js) stays */
    f.innerHTML = '<span><b>MN.</b>&nbsp; EST. 01.01.2025</span>' +
      '<span>© 2026 MN. · <a href="web.html">designed &amp; built by <span style="white-space:nowrap">M A R K U S&nbsp;&nbsp;N I N D L</span></a></span>' +
      '<span><a href="https://instagram.com/herrnindl" target="_blank" rel="noopener">instagram</a> · <a href="https://www.tiktok.com/@herrnindl" target="_blank" rel="noopener">tiktok</a> · <a href="links.html">links</a> · <a href="impressum.html">impressum</a> · <a href="datenschutz.html">datenschutz</a></span>' +
      '<span class="eggnote">tap the MN. logo 5 times. something will happen.</span>';
    if (dk) { var row = f.children[2]; row.appendChild(document.createTextNode(" · ")); row.appendChild(dk); }
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fill); else fill();
})();
