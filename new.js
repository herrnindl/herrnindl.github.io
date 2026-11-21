/* new. marker: a small dot on a menu tab when something was added since the visitor's last visit.
   The first visit shows no dots (everything is new then). Opening the tab removes its dot.
   play., glow up., wardrobe., ask me. have no dates, so bump MORE_NEW when you add something there. */
(function () {
  var MORE_NEW = "2026-11-21";   /* last time something new came to more. (wardrobe stories) */
  function latest(list) { return (list || []).reduce(function (m, x) { var id = String(x.id || "").slice(0, 10); return id > m ? id : m; }, ""); }
  window.mnNew = function (sets, here) {
    if (!sets) return;
    var R = latest(sets.recaps);
    var L = { journal: latest(sets.journal), posts: latest(sets.posts), more: MORE_NEW > R ? MORE_NEW : R };   /* recaps. sits under more. */
    var seen = null;
    try { seen = JSON.parse(localStorage.getItem("mn-seen") || "null"); } catch (e) {}
    if (!seen) seen = Object.assign({}, L);
    if (here && L[here]) seen[here] = L[here];
    try { localStorage.setItem("mn-seen", JSON.stringify(seen)); } catch (e) {}
    document.querySelectorAll("[data-new]").forEach(function (el) {
      var k = el.dataset.new;
      el.classList.toggle("isnew", !!L[k] && L[k] > (seen[k] || ""));
    });
  };
})();
