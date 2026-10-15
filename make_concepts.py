"""Наброски сайтов v2: 3D-иллюстрации (Microsoft Fluent Emoji, MIT), ниши из niches.py, настоящие шрифты.
Запуск: LEADS_DIR=leads OUT_DIR=out TMP_DIR=tmp python3 make_concepts2.py"""
import json, os, html, hashlib, glob, re, base64, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shot import shoot
from cover import cover
from niches import N, RULES

ASSETS = os.environ.get("ASSETS_DIR", os.path.join(HERE, "assets3d"))
OUT = os.path.abspath(os.environ.get("OUT_DIR", "/home/claude/mockups"))
TMP = os.path.abspath(os.environ.get("TMP_DIR", "/tmp/concepts_tmp"))
os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)

def h(s, salt=""):
    return int(hashlib.md5((s + salt).encode()).hexdigest(), 16)

ASSETS2D = os.environ.get("ASSETS2D_DIR", os.path.join(HERE, "assets2d"))
_cache = {}
def img(slug):
    """3D-иллюстрация; во втором варианте — плоская 2D-версия того же предмета (другой стиль)."""
    flat = os.environ.get("VARIANT", "1") == "2"
    key = (slug, flat)
    if key not in _cache:
        p2 = os.path.join(ASSETS2D, slug + ".svg")
        p3 = os.path.join(ASSETS, slug + ".png")
        if flat and os.path.exists(p2):
            _cache[key] = "data:image/svg+xml;base64," + base64.b64encode(open(p2, "rb").read()).decode()
        elif os.path.exists(p3):
            _cache[key] = "data:image/png;base64," + base64.b64encode(open(p3, "rb").read()).decode()
        else:
            _cache[key] = ""
    return _cache[key]

def niche_of(l):
    for text in (str(l.get("niche", "")).lower(), str(l.get("name", "")).lower()):
        for key, rx in RULES:
            if text and re.search(rx, text): return key
    return {"cake": "cake", "bakery": "bakery", "beauty": "salon", "barber": "barber", "repair": "watch"}.get(l.get("cat"), "other")

VARIANT = int(os.environ.get("VARIANT", "1"))  # 2 = второй вариант для повторного касания: другая палитра, заголовок и раскладка

def palette(l, k):
    opts = N[k]["palettes"]
    return opts[(h(l["id"]) + VARIANT - 1) % len(opts)]

def services(l, k):
    real = [x for x in (l.get("services") or []) if isinstance(x, (list, tuple)) and len(x) == 3]
    return real[:5] if len(real) >= 3 else N[k]["services"]

def plural(n, a, b, c):
    n = abs(int(n)) % 100
    if 11 <= n <= 19: return c
    n %= 10
    return a if n == 1 else b if 2 <= n <= 4 else c

def rating_chip(l):
    r, n = l.get("rating"), l.get("reviews")
    if not r or not n or n < 5: return ""
    return f'<span class="rate"><b>★ {float(r):.1f}'.replace(".", ",") + f'</b> · {n} {plural(n, "оценка", "оценки", "оценок")} на картах</span>'

DECOR = {"sparkles", "star", "glowing_star", "paw_prints", "bubbles", "herb", "cherry_blossom", "strawberry", "droplet", "sparkling_heart", "gem_stone", "leafy_green"}
ANIMALS = {"dog", "poodle", "cat", "dragon"}
BANNED = {"barber_pole", "baguette_bread", "candle", "hot_dog", "carrot"}  # формы, которые могут выглядеть двусмысленно

def art(keys, ac, ac2, theme, v):
    """Спокойная композиция: один главный предмет в центре на мягком круге, максимум один второстепенный
    предмет и 1–2 мелких декоративных акцента по углам, без наложений."""
    main = keys[0]
    rest = keys[1:]
    decor = [k for k in rest if k in DECOR][:2] or ["sparkles"]
    second = next((k for k in rest if k not in DECOR and k not in ANIMALS and k not in BANNED and k != main), None)
    flip = v == 1
    A, B = ("left", "right") if not flip else ("right", "left")
    disc = f"radial-gradient(circle at 35% 30%,{ac}2e,{ac2}1c 60%,{ac}0a)"
    parts = [f'<div class="disc" style="background:{disc}"></div><div class="ring" style="border-color:{ac}33"></div>',
             f'<div class="floor"></div><img class="o main" src="{img(main)}">']
    if second:
        parts.append(f'<img class="o second" src="{img(second)}" style="{B}:3%;bottom:7%">')
    parts.append(f'<img class="o d1" src="{img(decor[0])}" style="{B}:9%;top:9%">')
    if len(decor) > 1 and not second:
        parts.append(f'<img class="o d2" src="{img(decor[1])}" style="{A}:8%;bottom:12%">')
    elif len(decor) > 1:
        parts.append(f'<img class="o d2" src="{img(decor[1])}" style="{A}:9%;top:14%">')
    return '<div class="art3d">' + "".join(parts) + "</div>"

ART_CSS = """.art3d{position:relative;width:100%;aspect-ratio:1/1;max-width:440px;margin:0 auto}
.art3d .disc{position:absolute;inset:9%;border-radius:50%}
.art3d .ring{position:absolute;inset:4%;border-radius:50%;border:1.5px dashed}
.art3d .floor{position:absolute;left:28%;right:28%;bottom:17%;height:7%;border-radius:50%;background:radial-gradient(closest-side,rgba(0,0,0,.22),rgba(0,0,0,0))}
.art3d .o{position:absolute;filter:drop-shadow(0 14px 18px rgba(0,0,0,.20))}
.art3d .main{width:54%;left:23%;top:19%}
.art3d .second{width:21%;transform:rotate(-8deg)}
.art3d .d1{width:13%;transform:rotate(10deg)}.art3d .d2{width:11%;transform:rotate(-12deg);opacity:.95}
.ob{display:block;filter:drop-shadow(0 10px 14px rgba(0,0,0,.18))}
.brand{display:flex;align-items:center;gap:12px;white-space:nowrap}
.brand .mark{width:42px;height:42px;border-radius:13px;display:grid;place-items:center;flex:none;background:linear-gradient(145deg,var(--ac),var(--ac2));box-shadow:0 6px 16px -6px var(--ac)}
.brand .mark img{width:28px;height:28px;filter:drop-shadow(0 2px 3px rgba(0,0,0,.25))}
.brand .wm{line-height:1}.brand .wm em{font-style:normal;color:var(--ac)}
.brand small{display:block;font-family:"Manrope",sans-serif;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--mu);margin-top:4px;font-weight:700}
@media(max-width:720px){.brand .wm{font-size:21px!important}.brand .mark{width:36px;height:36px;border-radius:11px}.brand .mark img{width:23px;height:23px}.brand small{font-size:9px}}"""

def logo(name, n, font_css):
    """Логотип: значок ниши в цветной плитке + название, второе слово акцентом, подпись вида деятельности."""
    words = name.split(" ")
    wm = name if len(words) == 1 else " ".join(words[:-1]) + f" <em>{words[-1]}</em>"
    return f'<div class="brand"><span class="mark"><img src="{img(n["hero"][0])}"></span><span class="wm" style="{font_css}">{wm}<small>{html.escape(n["label"])}</small></span></div>'

def base_css(P, glow):
    ac, ac2, bg, sf, fg, mu, ln, theme = P
    return f""":root{{--ac:{ac};--ac2:{ac2};--bg:{bg};--sf:{sf};--fg:{fg};--mu:{mu};--ln:{ln};--glow:{glow};color-scheme:{theme}}}
*{{box-sizing:border-box}}html,body{{margin:0}}p{{margin:0}}h1,h2,h3{{margin:0}}
body{{background:radial-gradient(900px 520px at 85% -5%,var(--glow),transparent 70%) no-repeat,var(--bg);color:var(--fg);font-family:"Manrope",system-ui,sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 20px}}
.cta{{background:var(--ac);color:#fff;font-weight:700;white-space:nowrap;display:inline-block}}
.mu{{color:var(--mu)}}
.rate{{display:inline-flex;gap:6px;align-items:center;font-size:14px;color:var(--mu);margin-top:16px}}.rate b{{color:var(--fg)}}
.map{{border-radius:18px;border:1px solid var(--ln);background:repeating-linear-gradient(0deg,transparent 0 38px,var(--ln) 38px 40px),repeating-linear-gradient(90deg,transparent 0 58px,var(--ln) 58px 60px),var(--sf);position:relative;min-height:200px}}
.map img{{position:absolute;left:50%;top:44%;transform:translate(-50%,-50%);width:64px}}
footer{{margin-top:44px;border-top:1px solid var(--ln);color:var(--mu);padding:22px 0;font-size:14px}}
{ART_CSS}"""

HEAD = '<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;700&family=Unbounded:wght@600&family=Oswald:wght@500;600&family=Cormorant:ital,wght@0,600;1,600&display=swap">'

def contact_box(addr, cta, radius, title_css=""):
    return f'''<section><div class="contact"><div class="box"><h2 style="margin:0;{title_css}">Контакты</h2><p>{addr}</p><p class="mu">Telegram · WhatsApp · ВКонтакте</p><span class="cta" style="align-self:flex-start;border-radius:{radius};padding:12px 18px">{cta}</span></div><div class="map"><img src="{img("round_pushpin")}"></div></div></section>'''

def industrial(l, k, P, name, head, svcs, addr, v):
    n = N[k]; ac, ac2, bg, sf, fg, mu, ln, theme = P
    rows = "".join(f'<div class="row"><span>{html.escape(a)}<small>{html.escape(b)}</small></span><span class="dots"></span><b>{html.escape(c)}</b></div>' for a, b, c in svcs)
    badges = "".join(f"<span>{t}</span>" for t in n.get("badges", []))
    steps = "".join(f'<div><b>{i}</b><strong>{html.escape(t)}</strong><span class="mu">{html.escape(d)}</span></div>' for i, (t, d) in enumerate((n.get("steps") or [("Выберите", "услугу"), ("Оставьте заявку", "на сайте"), ("Подтверждение", "в мессенджере")])[:3], 1))
    lead = n.get("lead", "Цены на все работы, часы работы и вопрос мастеру прямо с сайта.")
    order = "order:-1" if v else ""
    grid = "repeating-linear-gradient(0deg,transparent 0 31px,var(--ln) 31px 32px),repeating-linear-gradient(90deg,transparent 0 31px,var(--ln) 31px 32px),"
    return HEAD + f"""<style>{base_css(P, ac + '26')}
.top{{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:18px 0;border-bottom:1px solid var(--ln)}}
.logo{{font-family:"Oswald",sans-serif;font-size:22px;text-transform:uppercase;letter-spacing:.04em;display:flex;align-items:center;gap:10px}}.logo img{{width:30px}}
.pill{{display:inline-flex;gap:8px;align-items:center;background:var(--sf);border:1px solid var(--ln);border-radius:999px;padding:7px 14px;font-weight:700;font-size:14px}}
.pill i{{width:9px;height:9px;border-radius:50%;background:#5BC98A}}
.hero{{display:grid;grid-template-columns:1.1fr 1fr;gap:30px;align-items:center;padding:40px 0}}.hero>*{{min-width:0}}
h1{{font-family:"Oswald",sans-serif;text-transform:uppercase;font-size:clamp(34px,6vw,62px);line-height:1.1;letter-spacing:.01em}}
.lead{{font-size:17px;color:var(--mu);margin:16px 0 0;max-width:38ch}}
.badges{{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}}.badges span{{border:2px solid var(--ln);border-radius:8px;padding:5px 10px;font-weight:700;font-size:13px}}
.btns{{display:flex;gap:10px;margin-top:22px;flex-wrap:wrap}}.cta{{border-radius:8px;padding:13px 20px}}.ghost{{border:2px solid var(--ln);border-radius:8px;padding:11px 18px;font-weight:700}}
.panel{{{order};border-radius:22px;border:1px solid var(--ln);background:{grid}var(--sf);padding:14px}}
h2{{font-family:"Oswald",sans-serif;text-transform:uppercase;font-size:30px;margin-bottom:16px}}
section{{padding:34px 0 0}}
.table{{background:var(--sf);border:1px solid var(--ln);border-radius:14px;padding:6px 18px}}
.row{{display:flex;align-items:baseline;gap:10px;padding:13px 0;border-bottom:1px solid var(--ln);font-size:16px}}.row:last-child{{border:0}}.row small{{display:block;color:var(--mu);font-size:13px;margin-top:2px}}
.dots{{flex:1;border-bottom:2px dotted var(--ln);transform:translateY(-4px)}}.row b{{color:var(--ac);white-space:nowrap}}
.steps{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}
.steps div{{background:var(--sf);border:1px solid var(--ln);border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:4px}}
.steps b{{font-family:"Oswald",sans-serif;font-size:40px;color:var(--ac);line-height:1;margin-bottom:6px}}
.contact{{display:grid;grid-template-columns:1fr 1.3fr;gap:14px}}.box{{background:var(--sf);border:1px solid var(--ln);border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:8px}}
@media(max-width:720px){{.hero,.contact{{grid-template-columns:1fr}}.panel{{order:0}}.steps{{grid-template-columns:1fr}}.pill{{display:none}}}}
</style></head><body><div class="wrap">
<div class="top">{logo(name, n, 'font-family:Oswald,sans-serif;font-size:28px;text-transform:uppercase;letter-spacing:.05em')}<span class="pill"><i></i>Открыто сейчас</span></div>
<div class="hero"><div><p class="mu" style="font-weight:700;letter-spacing:.1em;text-transform:uppercase;font-size:13px">{html.escape(l["city"])} · {html.escape(l["addr"])}</p>
<h1 style="margin-top:12px">{html.escape(head)}</h1><p class="lead">{lead}</p>
<div class="badges">{badges}</div>{rating_chip(l)}<div class="btns"><span class="cta">{n['cta']}</span><span class="ghost">Цены</span></div></div>
<div class="panel">{art(n['hero'], ac, ac2, theme, v)}</div></div>
<section><h2>Цены</h2><div class="table">{rows}</div></section>
<section><h2>{n.get('steps_title', 'Как это работает')}</h2><div class="steps">{steps}</div></section>
{contact_box(addr, n['cta'], '8px')}
<footer>{name} · {html.escape(l["city"])}</footer></div></body></html>"""

def elegant(l, k, P, name, head, svcs, addr, v):
    n = N[k]; ac, ac2, bg, sf, fg, mu, ln, theme = P
    words = head.split(" ")
    h1 = html.escape(" ".join(words[:-1])) + f' <em>{html.escape(words[-1])}</em>'
    items = "".join(f'<div class="item"><span class="t">{html.escape(a)}<small>{html.escape(b)}</small></span><span class="dots"></span><span class="p">{html.escape(c)}</span></div>' for a, b, c in svcs)
    tiles = "".join(f'<div class="tile" style="background:linear-gradient(160deg,{c1}33,{c2}12)"><img class="ob" src="{img(s)}"><span>{html.escape(t)}</span></div>'
                    for (s, t), (c1, c2) in zip(n.get("tiles") or [(n["hero"][i % 4], svcs[i % len(svcs)][0]) for i in range(4)], [(ac, ac2), (ac2, ac), (ac, ac), (ac2, ac2)]))
    frame = "border-radius:240px 240px 28px 28px" if v == 0 else "border-radius:50%"
    lead = n.get("lead", "Выберите услугу и удобное время прямо на сайте. Подтверждение придёт в Telegram.")
    return HEAD + f"""<style>{base_css(P, ac + '22')}
nav{{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;padding:20px 0;border-bottom:1px solid var(--ln);font-size:14px}}
nav .l{{display:flex;gap:18px;color:var(--mu)}}nav .r{{justify-self:end}}
.logo{{font-family:"Cormorant",serif;font-size:30px;font-weight:600;white-space:nowrap}}
.cta{{border-radius:999px;padding:12px 22px}}.ghost{{border:1px solid var(--ln);border-radius:999px;padding:11px 20px;font-weight:700}}
.hero{{display:grid;grid-template-columns:1fr 1fr;gap:36px;align-items:center;padding:44px 0}}.hero>*{{min-width:0}}
.frame{{{'order:-1;' if v else ''}{frame};background:linear-gradient(170deg,var(--sf),{ac}14);border:1px solid var(--ln);padding:28px 22px 18px;overflow:hidden;aspect-ratio:1/1.02;display:flex;align-items:center}}
.eyebrow{{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--mu);font-weight:700}}
h1{{font-family:"Cormorant",serif;font-weight:600;font-size:clamp(40px,6.4vw,72px);line-height:1.02;margin:14px 0}}
h1 em,h2 em{{color:var(--ac)}}
.lead{{color:var(--mu);font-size:17px;max-width:36ch}}.btns{{display:flex;gap:10px;margin-top:24px;flex-wrap:wrap}}
section{{padding:36px 0 0}}h2{{font-family:"Cormorant",serif;font-weight:600;font-size:44px;margin-bottom:16px}}
.list{{display:grid;grid-template-columns:1fr 1fr;gap:4px 40px}}
.item{{display:flex;align-items:baseline;gap:10px;padding:14px 0;border-bottom:1px solid var(--ln)}}.item .t{{font-family:"Cormorant",serif;font-size:24px;font-weight:600}}
.item .t small{{display:block;font-family:"Manrope",sans-serif;font-size:13px;color:var(--mu);font-weight:400;margin-top:2px}}
.dots{{flex:1;border-bottom:1px dotted var(--mu);opacity:.5;transform:translateY(-6px)}}.item .p{{color:var(--ac);font-weight:700;white-space:nowrap}}
.tiles{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.tile{{aspect-ratio:1;border-radius:20px;border:1px solid var(--ln);display:flex;flex-direction:column;justify-content:space-between;padding:12px 14px 14px;font-weight:700;overflow:hidden}}
.tile .ob{{width:62%;margin:6% auto 0}}
.contact{{display:grid;grid-template-columns:1fr 1.3fr;gap:14px}}.box{{background:var(--sf);border:1px solid var(--ln);border-radius:24px;padding:22px;display:flex;flex-direction:column;gap:8px}}
@media(max-width:720px){{.hero,.contact,.list{{grid-template-columns:1fr}}.frame{{order:0}}nav{{grid-template-columns:1fr auto}}nav .l{{display:none}}.logo{{font-size:26px}}.tiles{{grid-template-columns:1fr 1fr}}}}
</style></head><body><div class="wrap">
<nav><div class="l"><span>Услуги</span><span>Работы</span><span>Контакты</span></div>{logo(name, n, 'font-family:Cormorant,serif;font-size:34px;font-weight:600')}<div class="r"><span class="cta">{n['cta']}</span></div></nav>
<div class="hero"><div><p class="eyebrow">{html.escape(l["city"])} · {html.escape(n['label'])}</p><h1>{h1}</h1>
<p class="lead">{lead}</p>
<div class="btns"><span class="cta">{n['cta']}</span><span class="ghost">Услуги и цены</span></div>{rating_chip(l)}</div>
<div class="frame">{art(n['hero'], ac, ac2, theme, v)}</div></div>
<section><h2>Услуги <em>и цены</em></h2><div class="list">{items}</div></section>
<section><h2>Наши <em>работы</em></h2><div class="tiles">{tiles}</div></section>
{contact_box(addr, n['cta'], '999px', 'font-family:Cormorant,serif;font-size:36px')}
<footer>{name} · {html.escape(l["city"])}</footer></div></body></html>"""

def friendly(l, k, P, name, head, svcs, addr, v):
    n = N[k]; ac, ac2, bg, sf, fg, mu, ln, theme = P
    cols = [(ac, ac2), (ac2, ac), (ac, "#E8B86A"), (ac2, "#E8B86A")]
    cards = "".join(f'<div class="card"><div class="sw" style="background:linear-gradient(160deg,{c1}30,{c2}14)"><img class="ob" src="{img(s)}"></div><b>{html.escape(a)}</b><span class="mu">{html.escape(b)}</span><b class="pr">{html.escape(c)}</b></div>'
                    for (a, b, c), s, (c1, c2) in zip(svcs, n.get("cards") or n["hero"], cols))
    chips = "".join(f"<span>{t}</span>" for t in n.get("chips", []))
    steps = "".join(f'<div><i>{i}</i><b>{html.escape(t)}</b><span class="mu">{html.escape(d)}</span></div>' for i, (t, d) in enumerate(n.get("steps") or [("Выберите", "услугу"), ("Оставьте заявку", "на сайте"), ("Подтверждение", "в мессенджере")], 1))
    return HEAD + f"""<style>{base_css(P, ac + '1f')}
.top{{display:flex;justify-content:space-between;align-items:center;padding:18px 0}}
.logo{{font-family:"Unbounded",sans-serif;font-size:18px;display:flex;align-items:center;gap:10px}}.logo img{{width:32px}}
.cta{{border-radius:999px;padding:13px 22px}}.ghost{{border:1.5px solid var(--ln);background:var(--sf);border-radius:999px;padding:12px 20px;font-weight:700}}
.heroc{{background:linear-gradient({'135deg' if v == 0 else '225deg'},{ac}26,{ac2}22);border:1px solid var(--ln);border-radius:34px;padding:34px;display:grid;grid-template-columns:1.1fr 1fr;gap:20px;align-items:center}}.heroc>*{{min-width:0}}
h1{{font-family:"Unbounded",sans-serif;font-size:clamp(28px,4.6vw,50px);line-height:1.12}}
.lead{{color:var(--mu);font-size:17px;margin-top:14px;max-width:34ch}}.btns{{display:flex;gap:10px;margin-top:22px;flex-wrap:wrap}}
.chips{{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px}}.chips span{{background:var(--sf);border-radius:999px;padding:7px 12px;font-size:13px;font-weight:700;border:1px solid var(--ln)}}
section{{padding:36px 0 0}}h2{{font-family:"Unbounded",sans-serif;font-size:26px;margin-bottom:16px}}
.cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}}
.card{{background:var(--sf);border:1px solid var(--ln);border-radius:24px;padding:14px;display:flex;flex-direction:column;gap:6px}}
.sw{{height:132px;border-radius:16px;display:flex;justify-content:center;align-items:center;overflow:hidden;margin-bottom:6px}}.sw .ob{{height:78%}}.pr{{color:var(--ac)}}
.steps{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}}.steps div{{display:flex;flex-direction:column;gap:6px}}
.steps i{{width:44px;height:44px;border-radius:50%;background:var(--ac);color:#fff;display:grid;place-items:center;font-style:normal;font-weight:700;font-family:"Unbounded",sans-serif}}
.contact{{display:grid;grid-template-columns:1fr 1.3fr;gap:14px}}.box{{background:var(--sf);border:1px solid var(--ln);border-radius:24px;padding:22px;display:flex;flex-direction:column;gap:8px}}
@media(max-width:720px){{.heroc,.contact{{grid-template-columns:1fr}}.cards,.steps{{grid-template-columns:1fr 1fr}}.heroc{{padding:22px}}}}
</style></head><body><div class="wrap">
<div class="top">{logo(name, n, 'font-family:Unbounded,sans-serif;font-size:22px')}<span class="cta">{n['cta']}</span></div>
<div class="heroc"><div><h1>{html.escape(head)}</h1><p class="lead">{n.get('lead', '')}</p>
<div class="btns"><span class="cta">{n['cta']}</span><span class="ghost">{n.get('menu_title', 'Меню')} и цены</span></div>
<div class="chips">{chips}</div>{rating_chip(l)}</div><div>{art(n['hero'], ac, ac2, theme, v)}</div></div>
<section><h2>{n.get('menu_title', 'Меню')}</h2><div class="cards">{cards}</div></section>
<section><h2>Как заказать</h2><div class="steps">{steps}</div></section>
{contact_box(addr, n['cta'], '999px')}
<footer>{name} · {html.escape(l["city"])}</footer></div></body></html>"""

def page(l):
    k = niche_of(l); n = N[k]; P = palette(l, k)
    name = html.escape(l["name"].split(",")[0].strip())
    head = n["heads"][(h(l["id"], "h") + VARIANT - 1) % len(n["heads"])]
    motto = str(l.get("motto") or "").strip().strip("«»\"").rstrip(".!")
    if VARIANT == 1 and motto and len(motto) <= 48: head = motto  # девиз самого бизнеса — самый личный заголовок
    addr = html.escape(f'{l["city"]}, {l["addr"]}')
    v = (h(l["id"], "v") + VARIANT - 1) % 2
    lay = n["layout"] if VARIANT == 1 else {"industrial": "elegant", "elegant": "friendly", "friendly": "elegant"}[n["layout"]]
    fn = {"industrial": industrial, "elegant": elegant, "friendly": friendly}[lay]
    return fn(l, k, P, name, head, services(l, k), addr, v), k, P

def render(leads):
    jobs, meta = [], {}
    for l in leads:
        doc, k, P = page(l); meta[l["id"]] = (k, P)
        p = f"{TMP}/{l['id']}.html"; open(p, "w").write(doc)
        sfx = "" if VARIANT == 1 else f"-{VARIANT}"
        jobs += [{"src": p, "out": f"{TMP}/{l['id']}_d.png", "w": 1280, "h": 800, "scale": 2},
                 {"src": p, "out": f"{TMP}/{l['id']}_f.png", "w": 390, "h": 844, "full": True, "scale": 2},
                 {"src": p, "out": f"{TMP}/{l['id']}_m.png", "w": 390, "h": 844, "scale": 2}]
    shoot(jobs)
    for l in leads:
        k, P = meta[l["id"]]
        ac, _, bg, *_ = P
        dark = bg if P[7] == "dark" else "#1A1D22"
        sw = [p[0] for p in N[k]["palettes"]] + ["#5C8DD6", "#7E9C8A", "#C9A46A"]
        seen = []; [seen.append(c) for c in sw if c not in seen]
        name = l["name"].split(",")[0].strip()
        sfx = "" if VARIANT == 1 else f"-{VARIANT}"
        cover(f"{TMP}/{l['id']}_d.png", f"{TMP}/{l['id']}_f.png", f"{TMP}/{l['id']}_m.png", f"{OUT}/{l['id']}{sfx}.jpg",
              f"Так может выглядеть сайт: {name}" if VARIANT == 1 else f"Ещё один вариант сайта: {name}", "Компьютер и телефон, заявки сразу в Telegram", ac, dark,
              note=("Это первый набросок: цвета, стиль и разделы можно полностью поменять под вас" if VARIANT == 1 else "Другой стиль для сравнения: можно выбрать любой или смешать, всё подстроим под вас"), swatches=seen[:5])
    return meta

if __name__ == "__main__":
    src = os.environ.get("LEADS_DIR", "leads")
    leads = [json.load(open(f)) | {"id": os.path.basename(f)[:-5]} for f in sorted(glob.glob(src + "/*.json"))]
    meta = render(leads)
    for i, (k, P) in meta.items(): print(i, k)
    print("done", len(leads))
