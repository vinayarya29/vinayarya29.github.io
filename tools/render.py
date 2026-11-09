"""Render the admin-editable parts of the site from data/*.json (Python standard library only).

  data/news.json      -> index.html, between <!-- LN:news --> and <!-- /LN:news -->
                         (the latest NEWS_ON_HOME items, newest first)
  data/linkedin.json  -> talks.html, between <!-- SITE:linkedin --> and <!-- /SITE:linkedin -->

Both files are edited from admin.html (in the browser) and news.json also from LabNotebook.
GitHub Actions runs this after every change to data/ (.github/workflows/render.yml), and
LabNotebook runs it when it publishes. Run by hand with:  python3 tools/render.py
"""
import datetime
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
NEWS_ON_HOME = 5          # latest items shown on Home
NEWS_NEW_DAYS = 120       # items newer than this get a "New" badge
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def esc(s):
    # same output as markupsafe.escape (used by LabNotebook), so both give identical HTML
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&#34;").replace("'", "&#39;"))


def md(text):
    """Escape, then allow **bold** and *italic* only."""
    h = esc(text)
    h = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", h)
    return re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", h)


def load(name):
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def sorted_news(items):
    return sorted(items, key=lambda n: (n.get("when") or "", n.get("id") or 0), reverse=True)


def when_label(when):
    if when and len(when) == 7:
        return f"{MONTHS[int(when[5:]) - 1]} {when[:4]}"
    return when or ""


def is_new(when, today):
    try:
        d = datetime.date(int(when[:4]), int(when[5:7]) if len(when) == 7 else 12, 1)
    except (ValueError, TypeError):
        return False
    return (today - d).days <= NEWS_NEW_DAYS


def news_region(today=None):
    today = today or datetime.date.today()
    items = sorted_news(load("news.json"))[:NEWS_ON_HOME]
    if not items:
        return ""
    lis = []
    for n in items:
        when = n.get("when") or ""
        body = md(n.get("text"))
        if n.get("title"):
            body = f"<b>{esc(n['title'])}</b>" + (f"<br>{body}" if body else "")
        link = (n.get("link") or "").strip()
        if link.lower().startswith(("http://", "https://")):
            body += f' <a href="{esc(link)}" target="_blank" rel="noopener">Read&nbsp;more&nbsp;→</a>'
        cls = ' class="new"' if is_new(when, today) else ""
        lis.append(f'        <li{cls}><time>{when_label(when)}</time><span class="what">{body}</span></li>')
    return ("    <section id=\"news\">\n      <h2>News</h2>\n      <ul class=\"news\">\n"
            + "\n".join(lis) + "\n      </ul>\n    </section>")


def li_embed_url(post):
    """A post link, embed code or URN -> the official LinkedIn embed URL (None if not recognised)."""
    m = re.search(r"urn:li:(share|activity|ugcPost):(\d+)", post or "") or re.search(r"(activity)-(\d{15,})", post or "")
    return f"https://www.linkedin.com/embed/feed/update/urn:li:{m.group(1)}:{m.group(2)}" if m else None


def linkedin_region():
    cards = []
    for p in load("linkedin.json"):
        u = li_embed_url(p.get("urn"))
        if not u:
            continue
        cap = f'<figcaption>{md(p["by"])}</figcaption>' if p.get("by") else ""
        cards.append(f'        <figure class="li-post"><iframe src="{esc(u)}" title="LinkedIn post" loading="lazy" allowfullscreen></iframe>{cap}</figure>')
    if not cards:
        return ""
    return ("    <section id=\"linkedin\">\n      <h2>Highlighted on LinkedIn</h2>\n"
            "      <p class=\"li-lead\">Posts by my institute, department and collaborators about our work.</p>\n"
            "      <div class=\"li-grid\">\n" + "\n".join(cards) + "\n      </div>\n    </section>")


def replace_region(html, marker, name, new):
    pat = re.compile(rf"^([ \t]*)(<!-- {marker}:{name} -->)(.*?)[ \t]*(<!-- /{marker}:{name} -->)", re.S | re.M)
    if not pat.search(html):
        raise SystemExit(f"missing <!-- {marker}:{name} --> … <!-- /{marker}:{name} --> markers")
    body = new.strip("\n")
    return pat.sub(lambda m: m.group(1) + m.group(2) + "\n" + (body + "\n" if body else "") + m.group(1) + m.group(4),
                   html, count=1)


def write_if_changed(path, text):
    if path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    changed = []
    idx = ROOT / "index.html"
    if write_if_changed(idx, replace_region(idx.read_text(encoding="utf-8"), "LN", "news", news_region())):
        changed.append("index.html")
    talks = ROOT / "talks.html"
    if write_if_changed(talks, replace_region(talks.read_text(encoding="utf-8"), "SITE", "linkedin", linkedin_region())):
        changed.append("talks.html")
    print("changed: " + (", ".join(changed) or "nothing"))


if __name__ == "__main__":
    main()
