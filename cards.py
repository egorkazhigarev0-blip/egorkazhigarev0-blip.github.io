"""Наброски для тёплой рассылки, версия 3: вертикальная карточка 1080×1350 (4:5), которая в WhatsApp
и Telegram занимает весь экран телефона и читается без увеличения.

VARIANT=1 — первое касание: крупный телефон с первым экраном сайта (настоящее фото по теме, название как логотип,
девиз или заголовок ниши, рейтинг) и вынесенная карточка с НАСТОЯЩИМИ ценами из 2ГИС. Фон карточки берётся из цвета фото.
VARIANT=2 — повторное касание через 3–4 дня: показываем результат — экран записи/заказа на сайте и уведомление
«Новая заявка с сайта» в Telegram. Другая палитра (светлая), другое фото.

Запуск: LEADS_DIR=leads OUT_DIR=out TMP_DIR=tmp [VARIANT=2] python3 cards.py
Результат: out/<id>.jpg (вариант 1) и out/<id>-2.jpg (вариант 2) — те же имена, что у старого make_concepts.py.
"""
import json, os, glob, html, re, colorsys, hashlib, base64, io, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from niches import N, RULES
from shot import shoot
from PIL import Image

OUT = os.path.abspath(os.environ.get("OUT_DIR", "out")); TMP = os.path.abspath(os.environ.get("TMP_DIR", "tmp"))
VARIANT = int(os.environ.get("VARIANT", "1"))
PHOTOS = os.path.join(HERE, "photos")
try: PIDX = json.load(open(os.path.join(PHOTOS, "index.json")))
except Exception: PIDX = {}
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)

def h(s, salt=""): return int(hashlib.md5((s + salt).encode()).hexdigest(), 16)
def esc(s): return html.escape(str(s or ""))
def tidy(t): return re.sub(r"(?<![\w-])(\w{1,2}) ", lambda m: m.group(1) + " ", t)
def plural(n, a, b, c):
    n = abs(int(n)) % 100
    if 11 <= n <= 19: return c
    n %= 10
    return a if n == 1 else b if 2 <= n <= 4 else c

def niche_of(l):
    for text in (str(l.get("niche", "")).lower(), str(l.get("name", "")).lower(), str(l.get("about", "")).lower()):
        for key, rx in RULES:
            if text and re.search(rx, text): return key
    return {"cake": "cake", "bakery": "bakery", "beauty": "salon", "barber": "barber", "repair": "watch"}.get(l.get("cat"), "other")

# какой экран показывать во втором касании
MODE = {**{k: "book" for k in ["nails", "brows", "salon", "tan", "massage", "pets", "kids", "fitness", "barber", "auto", "photo", "tattoo"]},
        **{k: "order" for k in ["cake", "bakery", "coffee", "flowers", "cleaning"]},
        **{k: "ask" for k in ["watch", "shoe", "phone", "keys", "tailor", "renovation", "furniture", "other"]}}
PHOTO_KEY = {"tan": "salon", "kids": "kids", "other": None}

# ——— фото ———
def photo_list(k):
    ids = PIDX.get(PHOTO_KEY.get(k, k) or "", []) if PHOTO_KEY.get(k, k) else []
    return ids
def photo_path(i): return os.path.join(PHOTOS, f"{i}.jpg" if isinstance(i, str) else f"p{i}.jpg")
_used = set()
def pick_photo(l, k, salt):
    ids = photo_list(k)
    if not ids: return None
    pool = ids[:6] if salt == "1" else ids
    start = h(l["id"], salt) % len(pool)
    order = pool[start:] + pool[:start]
    p = next((i for i in order if (i, salt) not in _used), order[0]); _used.add((p, salt))
    return p
def photo_data(i, w=900):
    im = Image.open(photo_path(i)).convert("RGB"); im.thumbnail((w, w * 2))
    b = io.BytesIO(); im.save(b, "JPEG", quality=86)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode(), im
def edge_color(im):
    """Средний цвет краёв фото — это фон студийного снимка; из него делаем фон всей карточки."""
    w, hh = im.size; s = im.resize((40, int(40 * hh / w)))
    px = [s.getpixel((x, y)) for x in range(s.width) for y in range(s.height) if x < 4 or x >= s.width - 4 or y < 4]
    r, g, b = (sum(p[i] for p in px) / len(px) / 255 for i in range(3))
    return r, g, b
def hexc(rgb): return "#%02X%02X%02X" % tuple(max(0, min(255, round(c * 255))) for c in rgb)
def tone(rgb, L, smin=0.0, smax=1.0):
    hh, l, s = colorsys.rgb_to_hls(*rgb); return colorsys.hls_to_rgb(hh, L, max(smin, min(smax, s)))
def hex2rgb(x): x = x.lstrip("#"); return tuple(int(x[i:i + 2], 16) / 255 for i in (0, 2, 4))

# ——— данные ———
def services(l, k):
    real = [x for x in (l.get("services") or []) if isinstance(x, (list, tuple)) and len(x) == 3 and x[0]]
    return (real[:5], True) if len(real) >= 2 else ([list(x) for x in N[k]["services"]][:4], False)
def brand(l):
    n = l["name"].split(",")[0].strip().strip("«»\"")
    return n
def headline(l, k, v):
    n = N[k]; motto = str(l.get("motto") or "").strip().strip("«»\"").rstrip(".!")
    if v == 1 and motto and len(motto) <= 48: return motto
    return n["heads"][(h(l["id"], "h") + v - 1) % len(n["heads"])]
def rating(l):
    r, c = l.get("rating"), l.get("reviews")
    if not r or not c or c < 5 or float(r) < 4.5: return ""
    return f'★ {float(r):.1f}'.replace(".", ",") + f' · {c} {plural(c, "оценка", "оценки", "оценок")}'

LEADS = {"book": "Выберите услугу и удобное время: запись подтвердим в Telegram.",
         "order": "Выберите, что хотите, и оставьте заявку: ответим в течение часа.",
         "ask": "Цены на сайте. Напишите мастеру и приложите фото: ответим, сколько стоит и когда будет готово."}
FONTS = {"industrial": ("Unbounded", 700), "elegant": ("Geologica", 700), "friendly": ("Geologica", 800)}

ICON = {
 "wa": '<svg viewBox="0 0 24 24" fill="#25D366"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.2c-.2.6-1.3 1.2-1.8 1.2s-1 .3-3.4-.7c-2.9-1.2-4.7-4.1-4.8-4.3-.1-.2-1.2-1.6-1.2-3s.7-2.2 1-2.5c.3-.3.6-.3.8-.3h.6c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.4 0 .6l-.4.6-.4.5c-.1.2-.3.3-.1.6.2.3.9 1.4 1.9 2.3 1.3 1.1 2.4 1.5 2.7 1.6.3.2.5.1.7-.1l.9-1.1c.2-.3.4-.2.7-.1l2 1c.3.1.5.2.6.3.1.2.1.8-.1 1.4z"/></svg>',
 "tg": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#2AABEE"/><path fill="#fff" d="M17.6 7.2 15.7 16.6c-.1.6-.5.8-1 .5l-2.9-2.2-1.4 1.4c-.2.2-.3.3-.6.3l.2-3 5.4-4.9c.2-.2 0-.3-.4-.1l-6.7 4.2-2.9-.9c-.6-.2-.6-.6.1-.9l11.3-4.4c.5-.2 1 .1.8 1z"/></svg>',
 "max": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#6C4CF5"/><path d="M7.5 15.5V9l4.5 4.5L16.5 9v6.5" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "vk": '<svg viewBox="0 0 24 24"><rect width="24" height="24" rx="7" fill="#0077FF"/><path fill="#fff" d="M12.8 16.6c-4.7 0-7.4-3.2-7.5-8.6h2.4c.1 3.9 1.8 5.6 3.1 5.9V8h2.2v3.4c1.3-.1 2.7-1.7 3.2-3.4h2.2c-.4 2.1-1.9 3.6-3 4.2 1.1.5 2.9 1.9 3.6 4.4h-2.4c-.5-1.6-1.8-2.9-3.6-3.1v3.1z"/></svg>',
 "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
}

def messengers(l):
    out = []
    if l.get("wa"): out.append(("wa", "WhatsApp"))
    if l.get("tg"): out.append(("tg", "Telegram"))
    if l.get("maxUrl"): out.append(("max", "MAX"))
    if l.get("vk") and len(out) < 3: out.append(("vk", "ВКонтакте"))
    return out[:3] or [("wa", "WhatsApp"), ("tg", "Telegram")]

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:"Geologica","Manrope",sans-serif;-webkit-font-smoothing:antialiased;background:var(--bg);color:var(--fg);position:relative}
.phone{position:absolute;border-radius:74px;background:#0d0d0f;padding:16px;box-shadow:0 60px 90px -40px rgba(0,0,0,.65),0 0 0 2px rgba(255,255,255,.06) inset}
.scr{width:390px;border-radius:44px;overflow:hidden;background:var(--sbg);color:var(--sink);position:relative}
.notch{position:absolute;top:12px;left:50%;translate:-50% 0;width:118px;height:34px;border-radius:20px;background:#0d0d0f;z-index:5}
.sb{height:50px;display:flex;justify-content:space-between;align-items:flex-end;padding:0 30px 6px;font-size:15px;font-weight:600}
.sb i{display:inline-block;width:24px;height:11px;border:1.5px solid currentColor;border-radius:3px;opacity:.8}
.hd{display:flex;align-items:center;gap:10px;padding:10px 18px 12px}
.mark{width:34px;height:34px;border-radius:11px;background:var(--ac);color:var(--acink);display:grid;place-items:center;font-weight:800;font-size:17px}
.hd b{font-family:var(--df);font-weight:var(--dw);font-size:17px;letter-spacing:-.01em;line-height:1.05;max-width:250px}
.hd small{display:block;font-size:11px;opacity:.6;font-family:"Geologica";font-weight:400;margin-top:2px}
.burger{margin-left:auto;width:22px;height:14px;border-top:2.5px solid currentColor;border-bottom:2.5px solid currentColor;position:relative;opacity:.8}
.burger::after{content:"";position:absolute;left:0;right:0;top:3.5px;border-top:2.5px solid currentColor}
.rate{position:absolute;left:12px;bottom:12px;background:rgba(255,255,255,.94);color:#1b1b1b;border-radius:999px;padding:7px 12px;font-size:13px;font-weight:600}
.btn{display:inline-flex;align-items:center;justify-content:center;height:46px;padding:0 20px;border-radius:999px;font-weight:650;font-size:15px}
.btn.p{background:var(--ac);color:var(--acink)}
.btn.g{box-shadow:inset 0 0 0 1.5px currentColor;opacity:.85}
.note{position:absolute;font-size:22px;line-height:1.35;opacity:.78}
"""

def ink_for(rgb):
    r, g, b = rgb; lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#16110D" if lum > 0.55 else "#FFFFFF"

def page_v1(l, k):
    n = N[k]; pal = n["palettes"][h(l["id"]) % len(n["palettes"])]
    ac, ac2, sbg, surf, sink, muted, line, theme = pal
    lay = n["layout"]; df, dw = FONTS[lay]
    pid = pick_photo(l, k, "1")
    if pid is not None:
        uri, im = photo_data(pid); ec = edge_color(im)
    else:
        uri, ec = None, hex2rgb(ac)
    bg = tone(ec, 0.24, 0.25, 0.75)          # глубокий тон цвета фона фотографии
    glow = tone(ec, 0.42, 0.3, 0.8)
    name = brand(l); head = tidy(headline(l, k, 1)); rt = rating(l)
    svcs, real = services(l, k)
    city = esc(l.get("city", ""))
    nsize = 92 if len(name) <= 12 else 76 if len(name) <= 18 else 62 if len(name) <= 26 else 52
    if df == "Unbounded": nsize = int(nsize * .82)
    lines = 1 if len(name) * nsize * 0.62 < 950 else 2
    ptop = 150 + lines * nsize + 50
    side, oside = ("left", "right") if h(l["id"], "m") % 2 == 0 else ("right", "left")
    hsize = 31 if max((len(w) for w in head.split()), default=0) < 12 else 26
    hero = f'<div style="position:relative;margin:0 12px;border-radius:26px;overflow:hidden;height:250px;background:{hexc(tone(ec,.6))}"><img src="{uri}" style="width:100%;height:100%;object-fit:cover">{f"<span class=rate>{esc(rt)}</span>" if rt else ""}</div>' if uri else \
           f'<div style="margin:0 12px;border-radius:26px;height:250px;background:linear-gradient(140deg,{ac},{ac2})"></div>'
    chips = "".join(f'<span style="padding:7px 12px;border-radius:999px;background:{line};font-size:12.5px;font-weight:500">{esc(c)}</span>' for c in (n.get("chips") or n.get("badges") or ["Цены на сайте", "Заявки в Telegram", "Работаем каждый день"])[:3])
    rows = "".join(f'''<div class="row"><div><b>{esc(s[0])}</b>{f"<small>{esc(s[1])}</small>" if s[1] else ""}</div><span>{esc(s[2])}</span></div>''' for s in svcs[:5 if len(svcs) > 4 and all(len(s[0]) < 22 for s in svcs) else 4])
    ms = "".join(f'<span class="ms">{ICON[i]}{t}</span>' for i, t in messengers(l))
    acink = ink_for(hex2rgb(ac))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
:root{{--bg:{hexc(bg)};--fg:#fff;--ac:{ac};--acink:{acink};--sbg:{sbg};--sink:{sink};--df:"{df}";--dw:{dw}}}
body{{background:radial-gradient(900px 700px at 20% 60%,{hexc(glow)} 0%,transparent 65%),var(--bg)}}
.top{{position:absolute;left:64px;top:58px;right:64px}}
.top .k{{font-size:28px;opacity:.75;font-weight:400}}
.top h1{{font-family:"{df}";font-weight:{dw};font-size:{nsize}px;line-height:.98;letter-spacing:-.035em;margin:10px 0 0;text-wrap:balance}}
.top .c{{font-size:26px;opacity:.7;margin-top:14px}}
.phone{{{side}:52px;top:{ptop}px}}
.scr{{zoom:1.45;height:760px}}
h2.hh{{font-family:"{df}";font-weight:{dw};font-size:{hsize}px;line-height:1.04;letter-spacing:-.025em;padding:20px 20px 0;text-wrap:balance}}
.lead{{font-size:14.5px;line-height:1.45;color:{muted};padding:10px 20px 0}}
.prices{{position:absolute;{oside}:48px;top:{ptop+90}px;width:470px;background:{surf if theme=='light' else '#FFFFFF'};color:{sink if theme=='light' else '#1d1a1c'};border-radius:36px;padding:34px 34px 28px;box-shadow:0 40px 80px -30px rgba(0,0,0,.55)}}
.prices h3{{font-family:"{df}";font-weight:{dw};font-size:34px;letter-spacing:-.02em;line-height:1}}
.prices .src{{font-size:17px;opacity:.6;margin-top:8px}}
.row{{display:flex;justify-content:space-between;gap:16px;align-items:baseline;padding:16px 0;border-bottom:2px solid {line if theme=='light' else '#eee'}}}
.row:last-child{{border-bottom:0;padding-bottom:4px}}
.row b{{font-size:25px;font-weight:600;line-height:1.15;display:block}}
.row small{{font-size:18px;opacity:.6;display:block;margin-top:3px}}
.row span{{font-size:26px;font-weight:750;white-space:nowrap;color:{ac if theme=='light' else '#1d1a1c'}}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:250px;padding:0 64px 48px;display:flex;flex-direction:column;justify-content:flex-end;gap:20px;background:linear-gradient(180deg,transparent 0,var(--bg) 48%)}}
.msg{{display:flex;flex-wrap:wrap;gap:10px}}
.ms{{display:inline-flex;align-items:center;gap:10px;background:rgba(255,255,255,.14);backdrop-filter:blur(8px);border-radius:999px;padding:12px 20px 12px 14px;font-size:22px;font-weight:550}}
.ms svg{{width:30px;height:30px}}
.foot .note{{position:static;max-width:860px}}
</style></head><body>
<div class="top"><div class="k">Набросок сайта для</div><h1>{esc(name)}</h1><div class="c">{city}</div></div>
<div class="phone"><div class="scr"><div class="notch"></div>
  <div class="sb"><span>9:41</span><i></i></div>
  <div class="hd"><div class="mark">{esc(name[:1].upper())}</div><b>{esc(name)}<small>{esc(n["label"])}</small></b><div class="burger"></div></div>
  {hero}
  <h2 class="hh">{esc(head)}</h2>
  <p class="lead">{esc(n.get("lead") or LEADS.get(MODE.get(k, "ask")))}</p>
  <div style="display:flex;gap:8px;padding:16px 20px 0"><span class="btn p">{esc(n["cta"])}</span><span class="btn g">Цены</span></div>
  <div style="display:flex;gap:6px;flex-wrap:wrap;padding:14px 20px 0">{chips}</div>
</div></div>
<div class="prices"><h3>Услуги и цены</h3><div class="src">{"цены из вашей карточки в 2ГИС" if real else "примерные цены, поставим ваши"}</div>{rows}</div>
<div class="foot"><div class="msg">{ms}</div><div class="note">Это первый набросок: цвета, стиль и разделы можно полностью поменять под вас</div></div>
</body></html>"""

def page_v2(l, k):
    n = N[k]; pals = n["palettes"]
    pal = next((p for p in pals[(h(l["id"]) + 1) % len(pals):] + pals if p[7] == "light"), pals[0])
    ac, ac2, sbg, surf, sink, muted, line, theme = pal
    lay = n["layout"]; df, dw = FONTS[lay]
    mode = MODE.get(k, "ask")
    pid = pick_photo(l, k, "2")
    uri = photo_data(pid, 700)[0] if pid is not None else None
    acr = hex2rgb(ac)
    bg = tone(acr, 0.93, 0.25, 0.6); fg = "#15110F"
    name = brand(l); svcs, real = services(l, k)
    s0 = svcs[0]; acink = ink_for(acr)
    today = datetime.date.today(); wd = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
    days = [today + datetime.timedelta(days=i + 1) for i in range(5)]
    dchips = "".join(f'<span class="d{" on" if i == 1 else ""}"><small>{wd[d.weekday()]}</small><b>{d.day}</b></span>' for i, d in enumerate(days))
    first_names = ["Андрей", "Мария", "Ольга", "Дмитрий", "Екатерина", "Сергей", "Анна", "Ирина"]
    who = first_names[h(l["id"], "n") % len(first_names)]
    tail = f"{h(l['id'], 't') % 90 + 10}"
    dlabel = f"{days[1].day} {['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'][days[1].month-1]}"
    if mode == "book":
        title, big = "Онлайн-запись", "Клиенты записываются сами, даже ночью"
        sub = "Человек выбирает услугу и свободное время, а вы получаете готовую заявку в Telegram. Без звонков и переписки."
        body = f'''<div class="lbl">Услуга</div><div class="sel"><div><b>{esc(s0[0])}</b><small>{esc(s0[1])}</small></div><span>{esc(s0[2])}</span></div>
          <div class="lbl">День</div><div class="days">{dchips}</div>
          <div class="lbl">Время</div><div class="slots"><span class="x">10:00</span><span>11:30</span><span class="on">14:00</span><span>15:30</span><span class="x">17:00</span><span>18:30</span></div>
          <div class="cta">Записаться на 14:00</div>'''
        notif = f"{s0[0]} — {dlabel}, 14:00"
    elif mode == "order":
        title, big = "Заказ на сайте", "Заказы приходят прямо вам в Telegram"
        sub = "Клиент выбирает, что хочет, и дату, а вы получаете готовую заявку с телефоном. Ничего не теряется в переписке."
        body = f'''<div class="lbl">Что заказать</div><div class="sel"><div><b>{esc(s0[0])}</b><small>{esc(s0[1])}</small></div><span>{esc(s0[2])}</span></div>
          <div class="lbl">Дата</div><div class="days">{dchips}</div>
          <div class="lbl">Комментарий</div><div class="ta">Надпись «С днём рождения, мама!», доставка к 15:00</div>
          <div class="cta">Отправить заказ</div>'''
        notif = f"{s0[0]} на {dlabel}"
    else:
        title, big = "Вопрос мастеру", "Вопросы мастеру приходят в Telegram"
        sub = "Клиент описывает проблему и прикладывает фото, а вы отвечаете, когда удобно. Цена и срок понятны сразу."
        body = f'''<div class="lbl">Услуга</div><div class="sel"><div><b>{esc(s0[0])}</b><small>{esc(s0[1])}</small></div><span>{esc(s0[2])}</span></div>
          <div class="lbl">Что случилось</div><div class="ta">Нужно сделать к пятнице, сколько будет стоить?</div>
          <div class="att">＋ Фото прикреплено</div>
          <div class="cta">Отправить мастеру</div>'''
        notif = f"{s0[0]}: вопрос с фото"
    strip = f'<div style="margin:0 12px;height:150px;border-radius:24px;overflow:hidden"><img src="{uri}" style="width:100%;height:100%;object-fit:cover"></div>' if uri else ""
    bsize = 66 if len(big) <= 34 else 58
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
:root{{--bg:{hexc(bg)};--fg:{fg};--ac:{ac};--acink:{acink};--sbg:#FFFFFF;--sink:{sink};--df:"{df}";--dw:{dw}}}
.lt{{position:absolute;left:64px;top:64px;width:430px}}
.lt .nm{{display:inline-flex;align-items:center;gap:12px;font-family:"{df}";font-weight:{dw};font-size:28px;letter-spacing:-.01em}}
.lt .nm i{{width:44px;height:44px;border-radius:14px;background:var(--ac);color:var(--acink);display:grid;place-items:center;font-style:normal;font-size:22px}}
.lt h1{{font-family:"Geologica";font-weight:800;font-size:{bsize}px;line-height:1;letter-spacing:-.035em;margin:34px 0 0;text-wrap:balance}}
.lt p{{font-size:26px;line-height:1.4;margin-top:26px;color:#3b332e}}
.phone{{right:40px;top:230px}}
.scr{{zoom:1.3;height:840px}}
.st{{font-family:"{df}";font-weight:{dw};font-size:26px;letter-spacing:-.02em;padding:16px 20px 4px}}
.lbl{{font-size:13px;font-weight:600;opacity:.6;padding:14px 20px 8px}}
.sel{{margin:0 16px;border:2px solid var(--ac);border-radius:18px;padding:12px 14px;display:flex;justify-content:space-between;gap:10px;align-items:center}}
.sel b{{font-size:16px;display:block;line-height:1.2}}.sel small{{font-size:12.5px;opacity:.6}}.sel span{{font-weight:700;font-size:16px;white-space:nowrap}}
.days{{display:flex;gap:7px;padding:0 16px}}
.days .d{{flex:1;border-radius:14px;background:{line};text-align:center;padding:7px 0}}
.days small{{display:block;font-size:11px;opacity:.65}}.days b{{font-size:18px}}
.days .on,.slots .on{{background:var(--ac);color:var(--acink)}}
.slots{{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;padding:0 16px}}
.slots span{{background:{line};border-radius:12px;text-align:center;padding:10px 0;font-size:15px;font-weight:600}}
.slots .x{{opacity:.35;text-decoration:line-through}}
.ta{{margin:0 16px;border:1.5px solid {line};border-radius:14px;padding:12px;font-size:14px;line-height:1.4;min-height:70px}}
.att{{margin:10px 16px 0;font-size:13.5px;font-weight:600;color:var(--ac)}}
.cta{{margin:18px 16px 0;height:52px;border-radius:999px;background:var(--ac);color:var(--acink);display:grid;place-items:center;font-weight:700;font-size:16px}}
.nt{{position:absolute;left:40px;top:{870 if bsize>60 else 830}px;width:560px;background:#1F2125;color:#fff;border-radius:34px;padding:24px 26px;box-shadow:0 30px 70px -18px rgba(20,15,10,.55);display:flex;gap:18px;z-index:10}}
.nt .ic{{width:64px;height:64px;flex:none}}.nt .ic svg{{width:64px;height:64px}}
.nt .t{{font-size:20px;opacity:.6;display:flex;justify-content:space-between}}
.nt b{{display:block;font-size:27px;margin-top:4px;line-height:1.2}}
.nt p{{font-size:23px;line-height:1.35;margin-top:6px;color:rgba(255,255,255,.82)}}
.note{{left:64px;bottom:56px;width:430px;color:#3b332e}}
</style></head><body>
<div class="lt"><div class="nm"><i>{esc(name[:1].upper())}</i>{esc(name)}</div><h1>{esc(tidy(big))}</h1><p>{esc(sub)}</p></div>
<div class="phone"><div class="scr"><div class="notch"></div>
  <div class="sb"><span>9:41</span><i></i></div>
  <div class="hd"><div class="mark">{esc(name[:1].upper())}</div><b>{esc(name)}<small>{esc(n["label"])}</small></b><div class="burger"></div></div>
  {strip}
  <div class="st">{title}</div>
  {body}
</div></div>
<div class="nt"><div class="ic">{ICON["tg"]}</div><div style="flex:1"><div class="t"><span>Telegram</span><span>сейчас</span></div><b>Новая заявка с сайта</b><p>{esc(notif)}<br>{who}, +7 9•• •••-••-{tail}</p></div></div>
<div class="note">Ещё один набросок: так выглядит заявка с сайта. Цвета и разделы подстроим под вас</div>
</body></html>"""

def render(leads):
    jobs = []
    for l in leads:
        k = niche_of(l)
        doc = page_v1(l, k) if VARIANT == 1 else page_v2(l, k)
        p = f"{TMP}/{l['id']}-card{VARIANT}.html"; open(p, "w").write(doc)
        jobs.append({"src": p, "out": f"{TMP}/{l['id']}-card{VARIANT}.png", "w": 1080, "h": 1350, "scale": 1, "wait": 400})
        print(l["id"], k)
    shoot(jobs)
    sfx = "" if VARIANT == 1 else f"-{VARIANT}"
    for l in leads:
        Image.open(f"{TMP}/{l['id']}-card{VARIANT}.png").convert("RGB").save(f"{OUT}/{l['id']}{sfx}.jpg", quality=88, optimize=True)

if __name__ == "__main__":
    src = os.environ.get("LEADS_DIR", "leads")
    leads = [json.load(open(f)) | {"id": os.path.basename(f)[:-5]} for f in sorted(glob.glob(src + "/*.json"))]
    only = os.environ.get("ONLY")
    if only: leads = [l for l in leads if l["id"] in only.split(",")]
    render(leads); print("done", len(leads))
