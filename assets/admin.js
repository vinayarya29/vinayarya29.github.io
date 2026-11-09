/* Website admin page. Talks to the GitHub REST API directly from the browser and edits
   data/news.json (Home page News, shared with LabNotebook) and data/linkedin.json
   (LinkedIn posts on Talks & Outreach). Every save is a commit; the "Render site data"
   workflow then regenerates index.html / talks.html. No server, no third parties. */
(function () {
  var REPO = "vinayarya29/vinayarya29.github.io", BRANCH = "main", API = "https://api.github.com/repos/" + REPO;
  var KEY = "vinayarya-admin-token", NEWS_ON_HOME = 5;
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var token = "", files = { news: { path: "data/news.json", data: [], sha: null }, li: { path: "data/linkedin.json", data: [], sha: null } };
  var $ = function (id) { return document.getElementById(id); };

  function status(id, msg, kind) { var el = $(id); el.textContent = msg; el.className = "status" + (kind ? " " + kind : ""); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function md(s) { return esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\*(.+?)\*/g, "<i>$1</i>"); }
  function b64e(str) { var b = new TextEncoder().encode(str), s = ""; for (var i = 0; i < b.length; i++) s += String.fromCharCode(b[i]); return btoa(s); }
  function b64d(b64) { var s = atob(b64.replace(/\n/g, "")), b = new Uint8Array(s.length); for (var i = 0; i < s.length; i++) b[i] = s.charCodeAt(i); return new TextDecoder().decode(b); }

  function gh(path, opts) {
    opts = opts || {};
    return fetch(path.indexOf("http") === 0 ? path : API + path, {
      method: opts.method || "GET",
      headers: { "Authorization": "Bearer " + token, "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" },
      body: opts.body ? JSON.stringify(opts.body) : undefined, cache: "no-store"
    }).then(function (r) {
      if (r.status === 204) return null;
      return r.json().then(function (j) { if (!r.ok) throw new Error((j && j.message) || ("HTTP " + r.status)); return j; });
    });
  }
  function read(f) {
    return gh("/contents/" + f.path + "?ref=" + BRANCH).then(function (r) { f.data = JSON.parse(b64d(r.content)); f.sha = r.sha; },
      function (e) { if (/Not Found/.test(e.message)) { f.data = []; f.sha = null; } else throw e; });
  }
  function save(f, message, statusId) {
    status(statusId, "Saving…");
    var body = { message: message, content: b64e(JSON.stringify(f.data, null, 1) + "\n"), branch: BRANCH };
    if (f.sha) body.sha = f.sha;
    return gh("/contents/" + f.path, { method: "PUT", body: body }).then(function (r) {
      f.sha = r.content.sha; render(); status(statusId, "Saved. The site updates in about 2–3 minutes.", "ok");
    }).catch(function (e) {
      status(statusId, "Not saved: " + e.message + (/sha|match/i.test(e.message) ? " (it was changed elsewhere, e.g. from LabNotebook; reload the page)" : ""), "err");
      throw e;
    });
  }

  // ---------------------------------------------------------------- password lock
  // The GitHub token is stored in assets/admin-key.json, encrypted with the admin password
  // (PBKDF2-SHA256, 600k iterations -> AES-256-GCM). Only the password unlocks it.
  var KEYFILE = "assets/admin-key.json", ITER = 600000;
  var RAW = "https://raw.githubusercontent.com/" + REPO + "/" + BRANCH + "/" + KEYFILE;
  var u8 = function (b64) { return Uint8Array.from(atob(b64), function (c) { return c.charCodeAt(0); }); };
  var tob64 = function (buf) { var a = new Uint8Array(buf), s = ""; for (var i = 0; i < a.length; i++) s += String.fromCharCode(a[i]); return btoa(s); };
  function deriveKey(pw, salt, iter) {
    return crypto.subtle.importKey("raw", new TextEncoder().encode(pw), "PBKDF2", false, ["deriveKey"]).then(function (k) {
      return crypto.subtle.deriveKey({ name: "PBKDF2", salt: salt, iterations: iter, hash: "SHA-256" }, k, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
    });
  }
  function encryptToken(tok, pw) {
    var salt = crypto.getRandomValues(new Uint8Array(16)), iv = crypto.getRandomValues(new Uint8Array(12));
    return deriveKey(pw, salt, ITER).then(function (k) { return crypto.subtle.encrypt({ name: "AES-GCM", iv: iv }, k, new TextEncoder().encode(tok)); })
      .then(function (ct) { return { v: 1, kdf: "PBKDF2-SHA256", iter: ITER, salt: tob64(salt), iv: tob64(iv), ct: tob64(ct) }; });
  }
  function decryptToken(blob, pw) {
    return deriveKey(pw, u8(blob.salt), blob.iter).then(function (k) { return crypto.subtle.decrypt({ name: "AES-GCM", iv: u8(blob.iv) }, k, u8(blob.ct)); })
      .then(function (pt) { return new TextDecoder().decode(pt); });
  }
  function fetchKey(url) { return fetch(url + "?t=" + Date.now(), { cache: "no-store" }).then(function (r) { if (!r.ok) throw new Error("missing"); return r.json(); }); }
  function tryKey(url, pw) { return fetchKey(url).then(function (blob) { return decryptToken(blob, pw); }); }

  function unlock(t) {
    token = t;
    return gh("").then(function (repo) {
      if (!repo.permissions || !repo.permissions.push) throw new Error("the stored token can no longer write to the repository");
      try { sessionStorage.setItem(KEY, token); } catch (e) {}
      $("locked").hidden = true; $("unlocked").hidden = false;
      return load();
    });
  }
  function openWithPassword() {
    var pw = $("pw").value; if (!pw) return;
    status("pw-status", "Checking… (this takes a few seconds)");
    tryKey(KEYFILE, pw).catch(function () { return tryKey(RAW, pw); }).catch(function () {
      return fetchKey(RAW).then(function () { throw new Error("wrong password"); },
                                function () { throw new Error("no password has been set up yet — use “Set up or change the password”"); });
    }).then(unlock).then(function () { status("pw-status", ""); }).catch(function (e) {
      token = ""; status("pw-status", "Could not open: " + e.message + (/expired|Bad credentials/i.test(e.message) ? " — the GitHub token has expired; set up the password again with a new token" : ""), "err");
    });
  }
  $("pw-go").addEventListener("click", openWithPassword);
  $("pw").addEventListener("keydown", function (e) { if (e.key === "Enter") openWithPassword(); });
  $("show-setup").addEventListener("click", function (e) { e.preventDefault(); $("pw-card").hidden = true; $("setup-card").hidden = false; });
  $("hide-setup").addEventListener("click", function () { $("pw-card").hidden = false; $("setup-card").hidden = true; });
  $("setup-go").addEventListener("click", function () {
    var tok = $("tok").value.trim(), p1 = $("newpw").value, p2 = $("newpw2").value;
    if (!tok) return status("setup-status", "Paste the GitHub token.", "err");
    if (p1.length < 6) return status("setup-status", "Use at least 6 characters.", "err");
    if (p1 !== p2) return status("setup-status", "The passwords do not match.", "err");
    token = tok; status("setup-status", "Checking the token…");
    gh("").then(function (repo) {
      if (!repo.permissions || !repo.permissions.push) throw new Error("this token cannot write to " + REPO);
      return encryptToken(tok, p1);
    }).then(function (blob) {
      return gh("/contents/" + KEYFILE + "?ref=" + BRANCH).then(function (f) { return f.sha; }, function () { return undefined; }).then(function (sha) {
        var body = { message: "Set admin password", content: b64e(JSON.stringify(blob) + "\n"), branch: BRANCH };
        if (sha) body.sha = sha;
        return gh("/contents/" + KEYFILE, { method: "PUT", body: body });
      });
    }).then(function () {
      $("tok").value = $("newpw").value = $("newpw2").value = "";
      status("setup-status", "Password saved.", "ok");
      return unlock(token);
    }).catch(function (e) { token = ""; status("setup-status", "Not saved: " + e.message, "err"); });
  });
  $("signout").addEventListener("click", function () { try { sessionStorage.removeItem(KEY); } catch (e) {} location.reload(); });
  try { var saved = sessionStorage.getItem(KEY); if (saved) unlock(saved).catch(function () { sessionStorage.removeItem(KEY); $("locked").hidden = false; $("unlocked").hidden = true; }); } catch (e) {}

  function load() {
    return Promise.all([read(files.news), read(files.li)]).then(function () {
      $("who").textContent = "Signed in. Editing " + REPO + ".";
      render();
    });
  }

  // ---------------------------------------------------------------- helpers shared with tools/render.py
  function parseWhen(t) {
    t = (t || "").trim();
    var m = /^(\d{4})(?:-(\d{1,2}))?$/.exec(t);
    if (m) { if (!m[2]) return m[1]; var k = +m[2]; return k >= 1 && k <= 12 ? m[1] + "-" + (k < 10 ? "0" : "") + k : null; }
    m = /^([A-Za-z]{3})[a-z]*\.?\s+(\d{4})$/.exec(t);
    if (m) { var i = MONTHS.indexOf(m[1][0].toUpperCase() + m[1].slice(1, 3).toLowerCase()); if (i >= 0) return m[2] + "-" + (i < 9 ? "0" : "") + (i + 1); }
    return null;
  }
  function whenLabel(w) { return w && w.length === 7 ? MONTHS[+w.slice(5) - 1] + " " + w.slice(0, 4) : (w || ""); }
  // same order as tools/render.py: by date string, then id, newest first
  function sortNews(a) { return a.sort(function (x, y) { var wx = x.when || "", wy = y.when || ""; return wx < wy ? 1 : wx > wy ? -1 : (y.id || 0) - (x.id || 0); }); }
  function liUrn(x) {
    var m = /urn:li:(share|activity|ugcPost):(\d+)/.exec(x || "") || /(activity)-(\d{15,})/.exec(x || "");
    return m ? "urn:li:" + m[1] + ":" + m[2] : null;
  }
  function empty() { return '<li><span></span><span class="status">Nothing yet.</span><span></span></li>'; }

  // ---------------------------------------------------------------- render
  function render() {
    var news = sortNews(files.news.data);
    $("news-list").innerHTML = news.length ? news.map(function (n, i) {
      return '<li' + (i >= NEWS_ON_HOME ? ' class="off" title="Not shown on Home (only the latest ' + NEWS_ON_HOME + ' are)"' : "") + "><time>" + esc(whenLabel(n.when)) + "</time><span>" +
        (n.title ? "<b>" + esc(n.title) + "</b><br>" : "") + '<span class="' + (n.title ? "sub" : "") + '">' + md(n.text) + "</span>" +
        (n.link ? ' <a href="' + esc(n.link) + '" target="_blank" rel="noopener">link</a>' : "") + "</span>" +
        '<span class="ops"><button data-op="edit" data-i="' + i + '">Edit</button><button data-op="del" data-i="' + i + '" class="danger">Delete</button></span></li>';
    }).join("") : empty();
    var li = files.li.data;
    $("li-list").innerHTML = li.length ? li.map(function (p, i) {
      return "<li><time>Post " + (i + 1) + '</time><span><a href="https://www.linkedin.com/feed/update/' + esc(p.urn) + '/" target="_blank" rel="noopener">' + esc(p.urn) + "</a>" +
        (p.by ? '<br><span class="sub">' + md(p.by) + "</span>" : "") + "</span>" +
        '<span class="ops"><button data-op="edit" data-i="' + i + '">Edit</button><button data-op="up" data-i="' + i + '"' + (i ? "" : " disabled") + ' title="Move up">↑</button>' +
        '<button data-op="down" data-i="' + i + '"' + (i < li.length - 1 ? "" : " disabled") + ' title="Move down">↓</button>' +
        '<button data-op="del" data-i="' + i + '" class="danger">Delete</button></span></li>';
    }).join("") : empty();
  }

  // ---------------------------------------------------------------- news
  var editNews = null;  // index into the sorted list being edited
  function setNewsEdit(i) {
    editNews = i; var n = i == null ? {} : files.news.data[i];
    $("n-when").value = i == null ? "" : whenLabel(n.when); $("n-title").value = n.title || ""; $("n-text").value = n.text || ""; $("n-link").value = n.link || "";
    $("n-add").textContent = i == null ? "Add news" : "Save changes"; $("n-cancel").hidden = i == null;
    status("n-status", i == null ? "" : "Editing — change it and press Save changes.");
    if (i != null) { $("n-title").focus(); $("n-add").scrollIntoView({ block: "center", behavior: "smooth" }); }
  }
  $("n-cancel").addEventListener("click", function () { setNewsEdit(null); });
  $("news-list").addEventListener("click", function (ev) {
    var b = ev.target.closest("button"); if (!b) return;
    var i = +b.dataset.i, arr = files.news.data;
    if (b.dataset.op === "edit") return setNewsEdit(i);
    if (!confirm("Delete this news item?")) return;
    var gone = arr.splice(i, 1)[0]; setNewsEdit(null);
    save(files.news, "Delete news: " + String(gone.title || gone.text).replace(/\*/g, "").slice(0, 60), "n-status").catch(function () { arr.splice(i, 0, gone); render(); });
  });
  $("n-add").addEventListener("click", function () {
    var when = parseWhen($("n-when").value), title = $("n-title").value.trim(), text = $("n-text").value.trim(), link = $("n-link").value.trim();
    if (!when) return status("n-status", "Give a date like “Nov 2026” or “2026”.", "err");
    if (!title && !text) return status("n-status", "Write a heading or the details.", "err");
    if (link && !/^https?:\/\//i.test(link)) return status("n-status", "The link must start with https://", "err");
    var arr = files.news.data, label = (title || text).replace(/\*/g, "").slice(0, 60);
    if (editNews != null) {
      var i = editNews, old = arr[i], upd = Object.assign({}, old, { when: when, title: title, text: text, link: link });
      if (!title) delete upd.title;
      arr[i] = upd;
      return save(files.news, "Edit news: " + label, "n-status").then(function () { setNewsEdit(null); status("n-status", "Saved. The site updates in about 2–3 minutes.", "ok"); })
        .catch(function () { arr[i] = old; render(); });
    }
    var item = { id: arr.reduce(function (m, n) { return Math.max(m, n.id || 0); }, 0) + 1, when: when, text: text, link: link };
    if (title) item.title = title;
    arr.push(item);
    save(files.news, "Add news: " + label, "n-status").then(function () { setNewsEdit(null); status("n-status", "Added. The site updates in about 2–3 minutes.", "ok"); })
      .catch(function () { arr.splice(arr.indexOf(item), 1); render(); });
  });

  // ---------------------------------------------------------------- linkedin
  var editLi = null;
  function setLiEdit(i) {
    editLi = i; var p = i == null ? {} : files.li.data[i];
    $("li-in").value = p.urn || ""; $("li-by").value = p.by || "";
    $("li-add").textContent = i == null ? "Add post" : "Save changes"; $("li-cancel").hidden = i == null;
    status("li-status", i == null ? "" : "Editing post " + (i + 1) + ".");
    if (i != null) { $("li-by").focus(); $("li-add").scrollIntoView({ block: "center", behavior: "smooth" }); }
  }
  $("li-cancel").addEventListener("click", function () { setLiEdit(null); });
  $("li-list").addEventListener("click", function (ev) {
    var b = ev.target.closest("button"); if (!b) return;
    var arr = files.li.data, i = +b.dataset.i, op = b.dataset.op, before = arr.slice(), msg;
    if (op === "edit") return setLiEdit(i);
    setLiEdit(null);
    if (op === "del") { if (!confirm("Remove this LinkedIn post from the website?")) return; arr.splice(i, 1); msg = "Remove LinkedIn post"; }
    else { var j = op === "up" ? i - 1 : i + 1, t = arr[i]; arr[i] = arr[j]; arr[j] = t; msg = "Reorder LinkedIn posts"; }
    save(files.li, msg, "li-status").catch(function () { files.li.data = before; render(); });
  });
  $("li-add").addEventListener("click", function () {
    var urn = liUrn($("li-in").value), by = $("li-by").value.trim(), arr = files.li.data, before = arr.slice();
    if (!urn) return status("li-status", "That does not look like a LinkedIn post link or embed code.", "err");
    var dup = arr.findIndex(function (p) { return p.urn === urn; });
    if (dup >= 0 && dup !== editLi) return status("li-status", "That post is already on the site.", "err");
    var item = { urn: urn }; if (by) item.by = by;
    if (editLi != null) arr[editLi] = item; else arr.unshift(item);
    save(files.li, (editLi != null ? "Edit" : "Add") + " LinkedIn post " + urn, "li-status")
      .then(function () { setLiEdit(null); status("li-status", "Saved. The site updates in about 2–3 minutes.", "ok"); })
      .catch(function () { files.li.data = before; render(); });
  });
})();
