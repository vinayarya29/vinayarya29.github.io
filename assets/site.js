/* Shared by every page.
 * Opened directly (vinayarya29.github.io): shows its own top bar; links move
 *   between the GitHub pages.
 * Embedded in Google Sites: hides the top bar (Google Sites supplies the menu);
 *   links to my other pages open the matching Google Sites page over the whole window.
 * NAV is the one place to change menu names/links. Keep it in the same order and
 * wording as the Google Sites menu; `gs` must match each Google Sites page address.
 */
(function () {
  var GS = "https://sites.google.com/view/vinayarya";
  var NAV = [
    { id: "home",         label: "Home",          gh: "./",                gs: GS + "/home" },
    { id: "research",     label: "Research",      gh: "research.html",     gs: GS + "/research" },
    { id: "publications", label: "Publications",  gh: "publications.html", gs: GS + "/publications" },
    { id: "teaching",     label: "Teaching & CV", gh: "teaching.html",     gs: GS + "/teaching" }
  ];

  var embedded = false;
  try { embedded = window.self !== window.top; } catch (e) { embedded = true; }
  document.documentElement.classList.toggle("embedded", embedded);

  function hrefFor(n) { return embedded ? n.gs : n.gh; }

  document.addEventListener("DOMContentLoaded", function () {
    var bar = document.getElementById("topbar");
    if (bar && !embedded) {
      var current = document.body.dataset.page;
      var nav = bar.querySelector("nav");
      NAV.forEach(function (n) {
        var a = document.createElement("a");
        a.href = n.gh; a.textContent = n.label;
        if (n.id === current) a.className = "active";
        nav.appendChild(a);
      });
    }
    document.querySelectorAll("a[data-nav]").forEach(function (a) {
      var n = NAV.filter(function (x) { return x.id === a.dataset.nav; })[0];
      if (!n) return;
      a.href = hrefFor(n) + (a.dataset.hash ? "#" + a.dataset.hash : "");
      if (embedded) a.target = "_top";
    });
    // Chart tooltips
    var tip = document.getElementById("tip");
    if (tip) document.querySelectorAll(".chart .hit").forEach(function (r) {
      r.addEventListener("mousemove", function (e) { tip.textContent = r.dataset.tip; tip.style.left = (e.clientX + 12) + "px"; tip.style.top = (e.clientY - 26) + "px"; tip.style.opacity = 1; });
      r.addEventListener("mouseleave", function () { tip.style.opacity = 0; });
    });
    // Publication filters (publications page)
    var tabs = document.querySelectorAll(".tabs button"), search = document.querySelector(".search"), kind = "all";
    function apply() {
      var q = (search && search.value || "").trim().toLowerCase(), shown = 0;
      document.querySelectorAll(".ygroup").forEach(function (g) {
        var any = false;
        g.querySelectorAll(".cite").forEach(function (c) {
          var ok = (kind === "all" || c.dataset.kind === kind) && (!q || (c.dataset.text || "").indexOf(q) !== -1);
          c.style.display = ok ? "" : "none"; if (ok) { any = true; shown++; }
        });
        g.style.display = any ? "" : "none";
      });
      var none = document.querySelector(".none"); if (none) none.style.display = shown ? "none" : "block";
    }
    tabs.forEach(function (b) { b.addEventListener("click", function () { tabs.forEach(function (x) { x.classList.remove("on"); }); b.classList.add("on"); kind = b.dataset.kind; apply(); }); });
    if (search) search.addEventListener("input", apply);
  });
})();
