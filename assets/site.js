/* Shared by every page.
 * Opened directly (vinayarya29.github.io): shows its own top bar; links move
 *   between the GitHub pages.
 * Embedded in Google Sites: hides the top bar (Google Sites supplies the menu).
 *   The embed frame is sandboxed without top-navigation, so links to my other
 *   pages, email and phone open in a new tab.
 * NAV is the one place to change menu names/links. Keep it in the same order and
 * wording as the Google Sites menu; `gs` must match each Google Sites page address.
 */
(function () {
  var GS = "https://sites.google.com/view/vinayarya";
  var NAV = [
    { id: "home",         label: "Home",          gh: "./",                gs: GS + "/home" },
    { id: "research",     label: "Research",      gh: "research.html",     gs: GS + "/research" },
    { id: "publications", label: "Publications",  gh: "publications.html", gs: GS + "/publications" },
    { id: "talks",        label: "Talks & Outreach", gh: "talks.html",     gs: GS + "/talks" },
    { id: "teaching",     label: "Teaching & CV", gh: "teaching.html",     gs: GS + "/teaching" }
  ];

  // Visitor counts (GoatCounter: free, no cookies, no personal data). Counting starts once the
  // account "vinayarya" exists at https://www.goatcounter.com — until then the request just fails quietly.
  var GOATCOUNTER = "https://vinayarya.goatcounter.com/count";
  if (/\.github\.io$/.test(location.hostname)) {
    var gc = document.createElement("script");
    gc.async = true; gc.src = "https://gc.zgo.at/count.js"; gc.setAttribute("data-goatcounter", GOATCOUNTER);
    gc.setAttribute("data-goatcounter-settings", '{"allow_frame": true}');  // count visits through the Google Sites embeds too
    document.head.appendChild(gc);
  }

  var root = document.documentElement;
  var embedded = false;
  try { embedded = window.self !== window.top; } catch (e) { embedded = true; }
  root.classList.toggle("embedded", embedded);

  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canAnimate = !reduceMotion && "IntersectionObserver" in window;
  if (canAnimate) root.classList.add("anim");  // set before first paint so nothing flashes

  function hrefFor(n) { return embedded ? n.gs : n.gh; }

  document.addEventListener("DOMContentLoaded", function () {
    // ---- visible visitor count in the footer -------------------------------
    // Needs GoatCounter → Settings → "Allow adding visitor counts on your website". If that's off
    // (403) or the request fails, nothing is shown.
    var foot = document.querySelector("footer");
    if (foot && window.fetch && /\.github\.io$/.test(location.hostname)) {
      fetch("https://vinayarya.goatcounter.com/counter/TOTAL.json")
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) {
          if (!j || !j.count || j.count === "0") return;
          var s = document.createElement("span"); s.className = "visits";
          s.textContent = j.count + " visitors";
          var first = foot.firstElementChild;
          if (first) first.appendChild(document.createTextNode(" · ")), first.appendChild(s);
        })
        .catch(function () {});
    }

    // ---- navigation -------------------------------------------------------
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
    });
    if (embedded) {
      document.querySelectorAll('a[data-nav], a[target="_top"], a[href^="mailto:"], a[href^="tel:"]').forEach(function (a) {
        a.target = "_blank"; a.rel = "noopener";
      });
    }

    // ---- chart tooltips ---------------------------------------------------
    var tip = document.getElementById("tip");
    if (tip) document.querySelectorAll(".chart .hit").forEach(function (r) {
      r.addEventListener("mousemove", function (e) { tip.textContent = r.dataset.tip; tip.style.left = (e.clientX + 12) + "px"; tip.style.top = (e.clientY - 26) + "px"; tip.style.opacity = 1; });
      r.addEventListener("mouseleave", function () { tip.style.opacity = 0; });
    });

    // ---- publications: filters, search, BibTeX ----------------------------
    var tabs = document.querySelectorAll(".tabs button"), search = document.querySelector(".search"), kind = "all";
    function apply() {
      var q = (search && search.value || "").trim().toLowerCase(), shown = 0;
      document.querySelectorAll(".ygroup").forEach(function (g) {
        var any = false;
        g.querySelectorAll(".cite").forEach(function (c) {
          var okKind = kind === "all" || (kind === "first" ? c.dataset.first === "1" : c.dataset.kind === kind);
          var ok = okKind && (!q || (c.dataset.text || "").indexOf(q) !== -1);
          c.style.display = ok ? "" : "none"; if (ok) { any = true; shown++; }
        });
        g.style.display = any ? "" : "none";
      });
      var none = document.querySelector(".none"); if (none) none.style.display = shown ? "none" : "block";
    }
    tabs.forEach(function (b) { b.addEventListener("click", function () { tabs.forEach(function (x) { x.classList.remove("on"); }); b.classList.add("on"); kind = b.dataset.kind; apply(); }); });
    if (search) search.addEventListener("input", apply);

    function copyText(text, done) {
      function fallback() {
        var ta = document.createElement("textarea");
        ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        var ok = false; try { ok = document.execCommand("copy"); } catch (e) {}
        document.body.removeChild(ta);
        if (ok) done(); else window.prompt("Copy the BibTeX entry:", text);
      }
      if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, fallback);
      else fallback();
    }
    document.querySelectorAll("button.bib").forEach(function (b) {
      b.addEventListener("click", function () {
        copyText(b.dataset.bib, function () {
          b.classList.add("ok"); b.textContent = "Copied ✓";
          setTimeout(function () { b.classList.remove("ok"); b.textContent = "BibTeX"; }, 1600);
        });
      });
    });

    if (!canAnimate) return;

    // ---- motion: reveal on scroll ----------------------------------------
    var groups = [
      [".pagehead, main > section > h2, .lead, .chips, .thesis, .cta, .news, .taggroup, .edu li, .tbl, .pubbar", 0],
      [".highlights .hl, .tiles .tile, .minis .mini, .cards .card, .feature", 80]
    ];
    groups.forEach(function (g) {
      document.querySelectorAll(g[0]).forEach(function (el) {
        el.classList.add("reveal");
        if (g[1]) {
          var sibs = Array.prototype.filter.call(el.parentNode.children, function (x) { return x.matches(g[0]); });
          el.style.setProperty("--d", Math.min(sibs.indexOf(el), 5) * g[1] + "ms");
        }
      });
    });
    document.querySelectorAll(".journey li").forEach(function (li, i) { li.style.setProperty("--d", 250 + i * 160 + "ms"); });
    document.querySelectorAll(".chart .bar").forEach(function (b, i) { b.style.setProperty("--d", i * 90 + "ms"); });

    // ---- motion: count-up numbers ----------------------------------------
    function countUp(el) {
      var raw = el.textContent.trim(), m = raw.match(/^(\d[\d,]*)$/);
      if (!m) return;
      var target = parseInt(m[1].replace(/,/g, ""), 10);
      if (!target || target < 5) return;
      var t0 = null, dur = 1100;
      function step(ts) {
        if (!t0) t0 = ts;
        var p = Math.min(1, (ts - t0) / dur), e = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * e).toLocaleString("en-IN");
        if (p < 1) requestAnimationFrame(step); else el.textContent = raw;
      }
      el.textContent = "0";
      requestAnimationFrame(step);
    }

    var seen = false;
    setTimeout(function () {  // safety net: if the observer never reports, never leave content hidden
      if (!seen) document.querySelectorAll(".reveal, .chart, .journey").forEach(function (el) { el.classList.add("in"); });
    }, 2500);
    var io = new IntersectionObserver(function (entries) {
      seen = true;
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        el.classList.add("in");
        if (el.matches(".stats, .highlights, .metrics")) el.querySelectorAll("b").forEach(countUp);
        io.unobserve(el);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    document.querySelectorAll(".reveal, .chart, .journey, .stats, .highlights, .metrics").forEach(function (el) { io.observe(el); });

    // ---- motion: drifting molecules behind the thesis banner -------------
    document.querySelectorAll(".thesis .tx").forEach(function (box) {
      var c = document.createElement("canvas"); c.className = "mol"; c.setAttribute("aria-hidden", "true");
      box.insertBefore(c, box.firstChild);
      var ctx = c.getContext("2d"), dpr = Math.min(window.devicePixelRatio || 1, 2), W = 0, H = 0, pts = [], running = false;
      function size() {
        W = box.clientWidth; H = box.clientHeight; c.width = W * dpr; c.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        if (!pts.length) for (var i = 0; i < 26; i++) pts.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .18, vy: (Math.random() - .5) * .18, r: 1.4 + Math.random() * 2.2 });
      }
      function frame() {
        if (!running) return;
        ctx.clearRect(0, 0, W, H);
        for (var i = 0; i < pts.length; i++) {
          var p = pts[i]; p.x += p.vx; p.y += p.vy;
          if (p.x < -10) p.x = W + 10; if (p.x > W + 10) p.x = -10; if (p.y < -10) p.y = H + 10; if (p.y > H + 10) p.y = -10;
          for (var j = i + 1; j < pts.length; j++) {
            var q = pts[j], dx = p.x - q.x, dy = p.y - q.y, d2 = dx * dx + dy * dy;
            if (d2 < 9000) { ctx.strokeStyle = "rgba(255,255,255," + (0.10 * (1 - d2 / 9000)).toFixed(3) + ")"; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke(); }
          }
          ctx.fillStyle = "rgba(255,255,255,0.16)"; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill();
        }
        requestAnimationFrame(frame);
      }
      size(); window.addEventListener("resize", size);
      new IntersectionObserver(function (es) {  // only animate while the banner is on screen
        es.forEach(function (e) { var was = running; running = e.isIntersecting; if (running && !was) requestAnimationFrame(frame); });
      }).observe(box);
    });
  });
})();
