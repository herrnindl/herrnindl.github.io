/* The address is never written in one piece in the page source, so spam bots that scan websites don't find it.
   Links marked data-mail get their mailto: here. */
(function () {
  var a = ["booking", "herrnindl.com"].join("@");
  function go() { document.querySelectorAll("a[data-mail]").forEach(function (l) { l.href = "mailto:" + a; }); }
  window.mnMail = go;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
})();
