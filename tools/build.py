#!/usr/bin/env python3
"""Генерує стрічки анонсів і новин з data/<країна>.json.

Запуск з кореня репозиторію:  python3 tools/build.py
Створює <країна>/index.html (усі міста з фільтром) і <країна>/<місто>/index.html.
Минулі анонси відкидаються під час збирання і ховаються в браузері за датою.
"""
import datetime as dt
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MONTHS = ["січня", "лютого", "березня", "квітня", "травня", "червня",
          "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
MONTHS_NOM = ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
              "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"]
DAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "нд"]

e = lambda s: html.escape(str(s), quote=True)

CSS = """
:root{--bg:#f3f0f6;--paper:#fbfaf7;--ink:#1d1a2b;--muted:#5d5873;--lapis:#23306b;--lapis-ink:#eef0fb;
--gold:#b0811f;--gold-soft:#e8d6a6;--rule:#d9d3e3;--date:#23306b;
--f-display:"Ruslan Display","Alegreya",Georgia,serif;--f-body:"Alegreya",Georgia,"Times New Roman",serif;
--f-ui:"Fira Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12111c;--paper:#1a1928;--ink:#ebe8f2;--muted:#a9a3bf;
--lapis:#1c2557;--gold:#dcb257;--gold-soft:#5a4a24;--rule:#2f2d42;--date:#c9cff5;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#12111c;--paper:#1a1928;--ink:#ebe8f2;--muted:#a9a3bf;--lapis:#1c2557;--gold:#dcb257;
--gold-soft:#5a4a24;--rule:#2f2d42;--date:#c9cff5;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:1.15rem;line-height:1.6;margin:0}
.wrap{max-width:46rem;margin:0 auto;padding-inline:20px}
h1,h2,h3{text-wrap:balance;margin:0}p{margin:0}a{color:inherit}
.eyebrow{font-family:var(--f-ui);font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;font-weight:600}
.hero{background:var(--lapis);color:var(--lapis-ink);padding-block:3.5rem 2.6rem;position:relative;overflow:hidden}
.hero::before{content:"";position:absolute;inset:auto -10% -55% auto;width:34rem;height:34rem;border-radius:50%;
background:radial-gradient(circle,rgba(220,178,87,.32),rgba(220,178,87,0) 65%);pointer-events:none}
.hero .wrap{position:relative;display:grid;gap:1rem}
.crumbs{font-family:var(--f-ui);font-size:.85rem;color:#c5cae6;display:flex;flex-wrap:wrap;gap:.3rem .6rem}
.crumbs a{color:#e3c47c;text-decoration:none}
.hero h1{font-family:var(--f-display);font-weight:400;font-size:clamp(2.4rem,8vw,4rem);line-height:1.05}
.hero .lede{font-size:1.15rem;font-style:italic;color:#d6daf0;max-width:36rem}
.chips{display:flex;flex-wrap:wrap;gap:.45rem}
.chip{font-family:var(--f-ui);font-size:.88rem;border:1px solid rgba(227,196,124,.55);color:#eef0fb;background:transparent;
border-radius:999px;padding:.3rem .85rem;cursor:pointer;text-decoration:none}
.chip[aria-pressed="true"],.chip.on{background:#e3c47c;color:#1d1a2b;border-color:#e3c47c}
.chip:focus-visible{outline:3px solid #e3c47c;outline-offset:2px}
main{padding-block:2.2rem 1rem}
.sec{margin-bottom:2.5rem}
.sec>h2{font-family:var(--f-display);font-weight:400;font-size:clamp(1.7rem,6vw,2.3rem);margin-bottom:1rem}
.month{font-family:var(--f-ui);font-size:.82rem;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);font-weight:600;margin:1.6rem 0 .7rem}
.list{list-style:none;margin:0;padding:0;display:grid;gap:1rem}
.card{background:var(--paper);border:1px solid var(--rule);border-radius:14px;padding:1.1rem 1.2rem}
.ev{display:grid;grid-template-columns:3.6rem 1fr;gap:1rem;align-items:start}
.date{text-align:center;border-right:1px solid var(--rule);padding-right:.9rem}
.date b{display:block;font-family:var(--f-display);font-weight:400;font-size:2rem;line-height:1;color:var(--date)}
.date span{font-family:var(--f-ui);font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
.body{min-width:0;display:grid;gap:.35rem}
.card h3{font-family:var(--f-body);font-weight:700;font-size:1.3rem;line-height:1.2}
.card h3 a{text-decoration:none}.card h3 a:hover{text-decoration:underline}
.meta{font-family:var(--f-ui);font-size:.88rem;color:var(--muted)}
.card p{font-size:1.05rem}
.src{font-family:var(--f-ui);font-size:.78rem;color:var(--muted)}
.tag{font-family:var(--f-ui);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--gold);font-weight:600}
.poster{width:100%;height:auto;border-radius:10px;border:1px solid var(--rule);display:block;margin-bottom:.4rem}
.news .card{display:grid;gap:.5rem}
.view{display:flex;justify-content:flex-end;gap:.4rem;margin-bottom:1rem;font-family:var(--f-ui);font-size:.85rem;color:var(--muted);align-items:center}
.view button{font:inherit;border:1px solid var(--rule);background:var(--paper);color:var(--ink);border-radius:8px;padding:.3rem .7rem;cursor:pointer;display:inline-flex;gap:.35rem;align-items:center}
.view button[aria-pressed="true"]{border-color:var(--gold);box-shadow:inset 0 0 0 1px var(--gold)}
.view svg{width:1rem;height:1rem;fill:currentColor}
.compact .card{position:relative}
.compact .ev .body,.compact .news .card{grid-template-columns:1fr 4.5rem;column-gap:.8rem}
.compact .ev{grid-template-columns:2.6rem 1fr;gap:.7rem}.compact .date{padding-right:.6rem}.compact .date b{font-size:1.6rem}
.compact .card p{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.compact .poster{grid-column:2;grid-row:1/span 6;width:4.5rem;height:4.5rem;object-fit:cover;margin:0;align-self:start}
.compact .body>*:not(.poster),.compact .news .card>*:not(.poster){grid-column:1}
.empty{font-family:var(--f-ui);color:var(--muted);font-size:.95rem}
[hidden]{display:none!important}
footer{padding-block:2rem 3rem;font-family:var(--f-ui);font-size:.85rem;color:var(--muted)}
footer .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:.5rem}
.copy{display:inline-block;width:.72em;height:.72em;vertical-align:baseline;margin-right:.08em}
.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
"""

COPY = ('<span class="visually-hidden">©</span><svg class="copy" viewBox="0 0 20 20" aria-hidden="true">'
        '<circle cx="10" cy="10" r="8.6" fill="none" stroke="currentColor" stroke-width="1.6"/>'
        '<path d="M13.1 7.4a4 4 0 1 0 0 5.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg> 2026 apostol.ua')

JS = """<script>
(function(){
  var t=new Date(new Date().toLocaleString('en-US',{timeZone:'America/Toronto'}));
  var today=t.getFullYear()+'-'+String(t.getMonth()+1).padStart(2,'0')+'-'+String(t.getDate()).padStart(2,'0');
  var city='all';
  function apply(){
    document.querySelectorAll('[data-cities]').forEach(function(el){
      var past=el.dataset.date&&el.classList.contains('ev')&&el.dataset.date<today;
      var off=city!=='all'&&el.dataset.cities.split(' ').indexOf(city)<0;
      el.hidden=past||off;
    });
    document.querySelectorAll('.month').forEach(function(m){
      var l=m.nextElementSibling;m.hidden=!l.querySelector('li:not([hidden])');l.hidden=m.hidden;
    });
    document.querySelectorAll('.sec').forEach(function(s){
      var n=s.querySelector('.empty');if(n)n.hidden=!!s.querySelector('[data-cities]:not([hidden])');
    });
  }
  document.querySelectorAll('button.chip').forEach(function(b){
    b.addEventListener('click',function(){
      city=b.dataset.city;
      document.querySelectorAll('button.chip').forEach(function(x){x.setAttribute('aria-pressed',x===b)});
      apply();
    });
  });
  function setView(v){
    document.body.classList.toggle('compact',v==='compact');
    document.querySelectorAll('[data-view]').forEach(function(x){x.setAttribute('aria-pressed',x.dataset.view===v)});
    try{localStorage.setItem('apostol-view',v)}catch(_){}
  }
  document.querySelectorAll('[data-view]').forEach(function(b){b.addEventListener('click',function(){setView(b.dataset.view)})});
  var sv='big';try{sv=localStorage.getItem('apostol-view')||'big'}catch(_){}
  setView(sv);
  apply();
})();
</script>"""


def fdate(d):
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def sources(item):
    parts = [f'<a href="{e(u)}">{e(t)}</a>' for t, u in item.get("sources", [])]
    s = ("Джерела: " if len(parts) > 1 else "Джерело: ") + ", ".join(parts)
    if item.get("tickets"):
        s += f' · Квитки: <a href="{e(item["tickets"][1])}">{e(item["tickets"][0])}</a>'
    return f'<div class="src">{s}</div>'


def poster(src, alt):
    if not src:
        return ""
    return (f'<img class="poster" src="{e(src)}" alt="{e(alt)}" loading="lazy" '
            f'referrerpolicy="no-referrer" onerror="this.remove()">')


def city_names(item, cities):
    return " · ".join(cities[c]["name"] for c in item["cities"] if c in cities)


def events_html(events, cities, show_city):
    if not events:
        return ""
    out, cur = [], None
    for ev in events:
        d = dt.date.fromisoformat(ev["date"])
        if (d.year, d.month) != cur:
            if cur:
                out.append("</ul>")
            cur = (d.year, d.month)
            out.append(f'<h3 class="month">{MONTHS_NOM[d.month - 1]} {d.year}</h3><ul class="list">')
        meta = " · ".join(x for x in [ev.get("time"), ev.get("place")] if x)
        tag = f'<span class="tag">{e(city_names(ev, cities))}</span>' if show_city else ""
        out.append(
            f'<li class="card ev" data-date="{ev["date"]}" data-cities="{" ".join(ev["cities"])}">'
            f'<div class="date"><b>{d.day}</b><span>{DAYS[d.weekday()]}</span></div><div class="body">'
            f'{poster(ev.get("poster"), ev.get("posterAlt", ev["title"]))}{tag}'
            f'<h3>{e(ev["title"])}</h3><div class="meta">{e(meta)}</div><p>{e(ev["text"])}</p>{sources(ev)}</div></li>')
    out.append("</ul>")
    return "".join(out)


def news_html(news, cities, show_city):
    out = ['<ul class="list news">']
    for n in news:
        d = dt.date.fromisoformat(n["date"])
        title = f'<a href="{e(n["url"])}">{e(n["title"])}</a>' if n.get("url") else e(n["title"])
        kicker = " · ".join(x for x in [n.get("kicker"), city_names(n, cities) if show_city else ""] if x)
        out.append(
            f'<li class="card" data-cities="{" ".join(n["cities"])}">'
            f'{poster(n.get("image"), n.get("imageAlt", n["title"]))}'
            f'<span class="tag">{e(kicker)}</span><h3>{title}</h3>'
            f'<div class="meta">{fdate(d)}</div><p>{e(n["text"])}</p>{sources(n)}</li>')
    out.append("</ul>")
    return "".join(out)


def page(title, desc, crumbs, h1, lede, chips, events, news):
    return f"""<!doctype html><html lang="uk"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Ruslan+Display&family=Alegreya:ital,wght@0,400;0,500;0,700;1,400;1,500&family=Fira+Sans:wght@400;500;600&display=swap">
<style>{CSS}</style></head><body>
<header class="hero"><div class="wrap">
<nav class="crumbs" aria-label="Розділи">{crumbs}</nav>
<h1>{e(h1)}</h1><p class="lede">{e(lede)}</p>{chips}
</div></header>
<main class="wrap">
<div class="view" role="group" aria-label="Вигляд"><span>Вигляд:</span>
<button type="button" data-view="big" aria-pressed="true"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1" y="1" width="14" height="9" rx="1.5"/><rect x="1" y="12" width="14" height="3" rx="1"/></svg>Великі афіші</button>
<button type="button" data-view="compact" aria-pressed="false"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1" y="2" width="9" height="2" rx="1"/><rect x="1" y="6" width="7" height="2" rx="1"/><rect x="11" y="1" width="4" height="4" rx="1"/><rect x="1" y="10" width="9" height="2" rx="1"/><rect x="11" y="9" width="4" height="4" rx="1"/></svg>Іконки збоку</button>
</div>
<section class="sec" id="anonsy" aria-labelledby="h-a"><h2 id="h-a">Анонси</h2>{events}
<p class="empty" hidden>Найближчих анонсів поки немає.</p></section>
<section class="sec" id="novyny" aria-labelledby="h-n"><h2 id="h-n">Новини</h2>{news}
<p class="empty" hidden>Новин поки немає.</p></section>
</main>
<footer><div class="wrap"><span>Анонси й новини Української Греко-Католицької Церкви та громади</span><span>{COPY}</span></div></footer>
{JS}
</body></html>
"""


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("  ", path.relative_to(ROOT))


def build(data_file):
    data = json.loads(data_file.read_text(encoding="utf-8"))
    cc, cname, cities = data["country"]["code"], data["country"]["name"], data["cities"]
    today = dt.date.today() - dt.timedelta(days=1)  # запас на часовий пояс; решту ховає браузер
    events = sorted((x for x in data["events"] if dt.date.fromisoformat(x["date"]) >= today),
                    key=lambda x: (x["date"], x.get("time", "")))
    news = sorted(data["news"], key=lambda x: x["date"], reverse=True)

    chips = ('<div class="chips" role="group" aria-label="Місто">'
             '<button class="chip" type="button" data-city="all" aria-pressed="true">Усі міста</button>'
             + "".join(f'<button class="chip" type="button" data-city="{k}" aria-pressed="false">{e(v["name"])}</button>'
                       for k, v in cities.items()) + "</div>")
    write(ROOT / cc / "index.html", page(
        f"{cname} · apostol.ua", f"Анонси й новини УГКЦ і української громади: {cname}",
        f'<a href="/">apostol.ua</a><span>/</span><span>{e(cname)}</span>',
        cname, "Анонси й новини Української Греко-Католицької Церкви та громади.",
        chips, events_html(events, cities, True), news_html(news, cities, True)))

    for key, c in cities.items():
        ev = [x for x in events if key in x["cities"]]
        nw = [x for x in news if key in x["cities"]]
        links = ('<div class="chips">' + "".join(
            f'<a class="chip{" on" if k == key else ""}" href="/{cc}/{k}/">{e(v["name"])}</a>'
            for k, v in cities.items()) + "</div>")
        write(ROOT / cc / key / "index.html", page(
            f"{c['name']} · apostol.ua", f"Анонси й новини УГКЦ і української громади {c['loc']}",
            f'<a href="/">apostol.ua</a><span>/</span><a href="/{cc}/">{e(cname)}</a><span>/</span><span>{e(c["name"])}</span>',
            c["name"], f"Анонси й новини церкви та української громади {c['loc']}.",
            links, events_html(ev, cities, False), news_html(nw, cities, False)))


if __name__ == "__main__":
    for f in sorted((ROOT / "data").glob("*.json")):
        print(f.name)
        build(f)
