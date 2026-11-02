/* Shared by every page.
 * 1. Top bar: hidden when the page is embedded (Google Sites supplies the menu),
 *    shown when someone opens vinayarya29.github.io directly.
 * 2. NAV below is the one place to change menu names/links. Keep it in the same
 *    order and wording as the Google Sites menu.
 */
(function () {
  var GS = "https://sites.google.com/view/vinayarya";
  var NAV = [
    { id: "home",         label: "Home",          href: GS + "/home" },
    { id: "research",     label: "Research",      href: GS + "/research" },
    { id: "publications", label: "Publications",  href: GS + "/publications" },
    { id: "teaching",     label: "Teaching & CV", href: GS + "/teaching-cv" }
  ];

  var embedded = false;
  try { embedded = window.self !== window.top; } catch (e) { embedded = true; }
  document.documentElement.classList.toggle("embedded", embedded);

  document.addEventListener("DOMContentLoaded", function () {
    var bar = document.getElementById("topbar");
    if (bar && !embedded) {
      var current = document.body.dataset.page;
      var nav = bar.querySelector("nav");
      NAV.forEach(function (n) {
        var a = document.createElement("a");
        a.href = n.href; a.textContent = n.label; a.target = "_top";
        if (n.id === current) a.className = "active";
        nav.appendChild(a);
      });
    }
    // Links to my other pages (data-nav="research" etc.) leave the embed box
    // and open the matching Google Sites page.
    document.querySelectorAll("a[data-nav]").forEach(function (a) {
      var n = NAV.filter(function (x) { return x.id === a.dataset.nav; })[0];
      if (n) { a.href = n.href; a.target = "_top"; }
    });
    // Chart tooltips
    var tip = document.getElementById("tip");
    if (tip) document.querySelectorAll(".chart .hit").forEach(function (r) {
      r.addEventListener("mousemove", function (e) { tip.textContent = r.dataset.tip; tip.style.left = (e.clientX + 12) + "px"; tip.style.top = (e.clientY - 26) + "px"; tip.style.opacity = 1; });
      r.addEventListener("mouseleave", function () { tip.style.opacity = 0; });
    });
  });
})();
