"""Персональные концепты сайтов для рассылки: тёмный первый экран, строка фактов, несколько разделов. Обложка в подаче «кейс»."""
import json, os, html, hashlib, glob
from shot import shoot
from cover import cover
from illus import BY_KIND

DB = "/tmp/claude-0/-home-claude-atremt-github-io/df46a9db-46d7-5fa7-a18d-c4a297ce7691/scratchpad/db2/leads"
OUT = os.environ.get("OUT_DIR", "/home/claude/mockups")
TMP = os.environ.get("TMP_DIR", "/tmp/claude-0/-home-claude-atremt-github-io/df46a9db-46d7-5fa7-a18d-c4a297ce7691/scratchpad/concept")
os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)

# палитры по типу бизнеса: акцент, второй тон, фон, поверхность, текст, приглушённый, линия, тема
KIND_PALETTES = {
 "cake":   [("#C2416E", "#7FAE8A", "#FBF5F3", "#FFFFFF", "#2E1E24", "#7D6870", "#EFDDE2", "light"),
            ("#B8476A", "#E2B65C", "#FCF7F2", "#FFFFFF", "#2E1F1F", "#806C66", "#EEDFD5", "light")],
 "bakery": [("#B8732E", "#7A9A62", "#FBF6EE", "#FFFFFF", "#2D2318", "#7E6E5C", "#ECDFCB", "light"),
            ("#A8612B", "#C9A25A", "#F8F2E8", "#FFFFFF", "#2A2016", "#7A6A58", "#E8DAC4", "light")],
 "nails":  [("#C9709F", "#9BB79A", "#FBF5F7", "#FFFFFF", "#2C1F27", "#7C6A74", "#EFDDE6", "light"),
            ("#D48AC0", "#9FBF97", "#1F1A21", "#29222C", "#F2EAF0", "#B7A8B3", "#3A3140", "dark")],
 "salon":  [("#C9A46A", "#D9A3A0", "#1D1B1A", "#272422", "#F1ECE6", "#B3AAA0", "#3A3530", "dark"),
            ("#B5677D", "#8FA88F", "#FBF4F5", "#FFFFFF", "#2D2026", "#7D6A72", "#EEDCE1", "light"),
            ("#7E9C8A", "#C99A7A", "#F4F6F2", "#FFFFFF", "#1F2A24", "#68756D", "#DCE4DD", "light"),
            ("#B7895A", "#C98E98", "#FAF6F2", "#FFFFFF", "#2A221E", "#7C6E66", "#ECE1D8", "light")],
 "tan":    [("#D9853B", "#C9706A", "#FCF6EF", "#FFFFFF", "#2C2016", "#80705F", "#F0E1CE", "light"),
            ("#E09A4A", "#D27E73", "#211A15", "#2B231C", "#F3EADF", "#B8A898", "#3D3329", "dark")],
 "watch":  [("#C9A24E", "#8FA9C4", "#181C22", "#21262E", "#ECEAE4", "#A6ACB4", "#323944", "dark"),
            ("#A8822F", "#2F4A6E", "#F7F4EE", "#FFFFFF", "#1E2430", "#6B6F78", "#E6E0D4", "light")],
 "shoe":   [("#C7834A", "#8FA59A", "#1D2023", "#262A2E", "#ECE8E2", "#A9A39B", "#363B40", "dark"),
            ("#A9693A", "#6E8A7E", "#F6F2EC", "#FFFFFF", "#26211C", "#776C61", "#E6DDD1", "light")],
 "phone":  [("#3FA7F0", "#7BE0C3", "#121822", "#1A2230", "#E7EEF6", "#9EABBC", "#2A3546", "dark"),
            ("#2E7FE0", "#26B8A0", "#F3F7FB", "#FFFFFF", "#162234", "#62718A", "#DCE5F0", "light")],
 "barber": [("#C8924A", "#7FA3A8", "#191A1C", "#232427", "#EDE8E1", "#A8A39C", "#36373B", "dark"),
            ("#C9A55A", "#6E9C86", "#15201C", "#1D2A25", "#E9EEE9", "#A3B2AA", "#2D3D36", "dark"),
            ("#B8433A", "#2F4A6E", "#F5F1EA", "#FFFFFF", "#1E2430", "#6B6F78", "#E4DDD1", "light"),
            ("#5C8DD6", "#D9A35A", "#141A24", "#1C2431", "#E8EDF5", "#A0AABA", "#2C3646", "dark"),
            ("#B5523B", "#C9A15E", "#1C1B1A", "#262422", "#EEE7DF", "#ABA298", "#3A3632", "dark")],
 "other":  [("#3E8E7E", "#D9A35A", "#F4F7F5", "#FFFFFF", "#1E2A26", "#66756F", "#DDE6E2", "light")],
}
ICONS = {
 "clock": '<svg class="ic" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
 "tag": '<svg class="ic" viewBox="0 0 24 24"><path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>',
 "chat": '<svg class="ic" viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z"/></svg>',
 "star": '<svg class="ic" viewBox="0 0 24 24"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/></svg>',
 "pin": '<svg class="ic" viewBox="0 0 24 24"><path d="M12 21s7-6.2 7-12a7 7 0 10-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
 "spark": '<svg class="ic" viewBox="0 0 24 24"><path d="M12 3v6M12 15v6M3 12h6M15 12h6"/></svg>',
}

def kind(l):
    n = l["name"].lower()
    if l["cat"] == "cake": return "cake"
    if l["cat"] == "bakery": return "bakery"
    if l["cat"] == "barber": return "barber"
    if l["cat"] == "beauty":
        if "загар" in n: return "tan"
        if "маникюр" in n or "нейл" in n or "ногт" in n: return "nails"
        if "имидж" in n or "салон" in n or "красоты" in n: return "salon"
        return "nails"
    if "час" in n: return "watch"
    if "обув" in n: return "shoe"
    if "телефон" in n or "mobile" in n: return "phone"
    return "other"

CONTENT = {
 "cake": ("Торты на заказ к вашему празднику", ["Торты на заказ", "Бенто-торты", "Капкейки", "Сладкий стол"], "Заказать торт"),
 "bakery": ("Свежая выпечка каждое утро", ["Хлеб", "Выпечка", "Торты на заказ", "Кофе с собой"], "Сделать предзаказ"),
 "tan": ("Ровный загар и ухоженные руки", ["Солярий", "Маникюр", "Покрытие гель-лаком", "Педикюр"], "Записаться"),
 "salon": ("Красота без долгих переписок", ["Стрижки", "Окрашивание", "Маникюр", "Макияж"], "Записаться"),
 "nails": ("Аккуратный маникюр с онлайн-записью", ["Маникюр", "Покрытие гель-лаком", "Педикюр", "Дизайн ногтей"], "Записаться"),
 "watch": ("Ремонт часов, пока вы ждёте", ["Замена батарейки", "Ремонт браслета", "Замена стекла", "Чистка механизма"], "Спросить мастера"),
 "shoe": ("Вернём любимой обуви вторую жизнь", ["Набойки", "Ремонт подошвы", "Замена молнии", "Растяжка обуви"], "Спросить мастера"),
 "phone": ("Ремонт телефонов без долгого ожидания", ["Замена экрана", "Замена аккумулятора", "Ремонт разъёма", "Диагностика"], "Оставить заявку"),
 "barber": ("Мужские стрижки с записью онлайн", ["Мужская стрижка", "Стрижка бороды", "Стрижка машинкой", "Отец + сын"], "Записаться"),
 "other": ("Услуги рядом с домом", ["Услуга", "Услуга", "Услуга", "Услуга"], "Оставить заявку"),
}

SAMPLE = {
 "nails": [("Маникюр без покрытия", "45 минут", "1 200 ₽"), ("Маникюр с покрытием", "гель-лак, 1,5 часа", "2 000 ₽"), ("Педикюр с покрытием", "1,5 часа", "2 400 ₽"), ("Дизайн ногтей", "за 1 ноготь", "от 100 ₽")],
 "salon": [("Женская стрижка", "с укладкой", "1 600 ₽"), ("Окрашивание", "в один тон", "от 3 500 ₽"), ("Укладка", "на любую длину", "1 200 ₽"), ("Маникюр с покрытием", "гель-лак", "1 900 ₽")],
 "tan": [("Солярий", "1 минута", "30 ₽"), ("Абонемент", "100 минут", "2 500 ₽"), ("Маникюр с покрытием", "гель-лак", "1 800 ₽"), ("Педикюр", "1 час", "2 200 ₽")],
 "barber": [("Мужская стрижка", "45 минут", "1 400 ₽"), ("Стрижка бороды", "с оформлением", "800 ₽"), ("Стрижка машинкой", "одна насадка", "900 ₽"), ("Отец + сын", "две стрижки", "2 200 ₽"), ("Детская стрижка", "до 12 лет", "1 000 ₽")],
 "cake": [("Торт на заказ", "любая начинка", "1 800 ₽/кг"), ("Бенто-торт", "на 2–3 человек", "1 500 ₽"), ("Капкейки", "набор из 6 шт.", "1 200 ₽"), ("Сладкий стол", "на праздник", "от 5 000 ₽")],
 "bakery": [("Хлеб на закваске", "каждое утро", "180 ₽"), ("Круассаны", "с маслом", "120 ₽"), ("Пироги", "мясо, рыба, ягоды", "от 450 ₽"), ("Торты на заказ", "от 1,5 кг", "1 700 ₽/кг")],
 "watch": [("Замена батарейки", "при вас, 5 минут", "от 300 ₽"), ("Ремонт браслета", "укорачивание, замена", "от 250 ₽"), ("Замена стекла", "1–2 дня", "от 800 ₽"), ("Чистка механизма", "с гарантией", "от 1 500 ₽"), ("Диагностика", "бесплатно при ремонте", "0 ₽")],
 "shoe": [("Набойки", "при вас", "от 350 ₽"), ("Ремонт подошвы", "1–2 дня", "от 900 ₽"), ("Замена молнии", "сапоги, куртки", "от 700 ₽"), ("Растяжка обуви", "1 день", "от 400 ₽"), ("Диагностика", "бесплатно", "0 ₽")],
 "phone": [("Замена экрана", "от 1 часа", "от 2 500 ₽"), ("Замена аккумулятора", "30 минут", "от 1 500 ₽"), ("Ремонт разъёма", "1 день", "от 900 ₽"), ("Чистка после воды", "1–2 дня", "от 1 200 ₽"), ("Диагностика", "бесплатно", "0 ₽")],
 "other": [("Услуга 1", "описание", "от 500 ₽"), ("Услуга 2", "описание", "от 800 ₽"), ("Услуга 3", "описание", "от 1 200 ₽"), ("Консультация", "бесплатно", "0 ₽")],
}
TILES = {"nails": ["Нюд", "Френч", "Дизайн", "Педикюр"], "salon": ["Стрижки", "Окрашивание", "Укладки", "Маникюр"],
         "tan": ["Солярий", "Маникюр", "Педикюр", "Уход"], "cake": ["Детские", "Свадебные", "Бенто", "Капкейки"], "bakery": ["Хлеб", "Выпечка", "Пироги", "Торты"]}

def samples(l):
    """Настоящие услуги и цены бизнеса (из 2ГИС), если они собраны в поле services: [[название, пояснение, цена], ...]."""
    real = [x for x in (l.get("services") or []) if isinstance(x, (list, tuple)) and len(x) == 3]
    return real[:5] if len(real) >= 3 else SAMPLE[kind(l)]

def plural(n, a, b, c):
    n = abs(int(n)) % 100
    if 11 <= n <= 19: return c
    n %= 10
    return a if n == 1 else b if 2 <= n <= 4 else c

def rating_chip(l):
    r, n = l.get("rating"), l.get("reviews")
    if not r or not n or n < 5: return ""
    return f'<span class="rate"><b>★ {str(r).replace(".", ",")}</b> · {n} {plural(n, "отзыв", "отзыва", "отзывов")} на картах</span>'

def palette(l):
    opts = KIND_PALETTES[kind(l)]
    return opts[int(hashlib.md5(l["id"].encode()).hexdigest(), 16) % len(opts)]

HEADS = {"watch": ["Ремонт часов, пока вы ждёте", "Часы снова идут точно", "Батарейка за 5 минут при вас"],
         "shoe": ["Вернём любимой обуви вторую жизнь", "Ремонт обуви рядом с домом"],
         "nails": ["Аккуратный маникюр с онлайн-записью", "Красивые руки без очередей", "Маникюр, к которому хочется вернуться"],
         "salon": ["Красота без долгих переписок", "Запишитесь к мастеру за минуту", "Стрижки и окрашивание, которым доверяют", "Ваш мастер рядом с домом"],
         "barber": ["Мужские стрижки с записью онлайн", "Стрижка и борода в одном месте", "Свободное время мастера на сайте", "Чёткая стрижка без ожидания", "Барбершоп, где помнят вашу стрижку"],
         "phone": ["Ремонт телефонов без долгого ожидания", "Вернём телефон к жизни за день"]}

LAYOUT = {"watch": "industrial", "shoe": "industrial", "phone": "industrial", "other": "industrial", "barber": "industrial",
          "nails": "elegant", "salon": "elegant", "tan": "elegant", "cake": "friendly", "bakery": "friendly"}

def base_css(ac, bg, sf, fg, mu, ln, theme, glow):
    return f""":root{{--ac:{ac};--bg:{bg};--sf:{sf};--fg:{fg};--mu:{mu};--ln:{ln};--glow:{glow};color-scheme:{theme}}}
*{{box-sizing:border-box}}html,body{{margin:0}}p{{margin:0}}h1,h2,h3{{margin:0}}
body{{background:radial-gradient(900px 520px at 85% -5%,var(--glow),transparent 70%) no-repeat,var(--bg);color:var(--fg)}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 20px}}
.cta{{background:var(--ac);color:#fff;font-weight:700;white-space:nowrap;display:inline-block}}
.mu{{color:var(--mu)}}
svg.ic{{width:22px;height:22px;fill:none;stroke:var(--ac);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}}
.illus{{width:100%;max-width:440px;display:block;margin:0 auto}}
.map{{border-radius:18px;border:1px solid var(--ln);background:repeating-linear-gradient(0deg,transparent 0 38px,var(--ln) 38px 40px),repeating-linear-gradient(90deg,transparent 0 58px,var(--ln) 58px 60px),var(--sf);position:relative;min-height:200px}}
.map i{{position:absolute;left:50%;top:45%;transform:translate(-50%,-50%);width:48px;height:48px;border-radius:50%;background:var(--ac);display:grid;place-items:center;box-shadow:0 0 0 10px var(--glow)}}
.map svg.ic{{stroke:#fff}}
footer{{margin-top:44px;border-top:1px solid var(--ln);color:var(--mu);padding:22px 0;font-size:14px}}"""

HEAD = '<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;700&family=Unbounded:wght@600&family=Oswald:wght@500;600&family=Cormorant:ital,wght@0,600;1,600&display=swap">'

EXTRA = {"barber": "Детская стрижка"}
LEADTXT = {"barber": "Цены, свободное время мастеров и запись в пару касаний, без звонков."}
NOTETXT = {"barber": "Цены условные, на настоящем сайте будут ваши."}
STEPS = {"barber": '<section><h2>Как записаться</h2><div class="steps"><div><b>1</b>Выбираете услугу и мастера</div><div><b>2</b>Отмечаете удобное время</div><div><b>3</b>Приходите, напоминание придёт заранее</div></div></section>'}

def industrial(l, P, art, name, head, svcs, cta, addr, v):
    ac, ac2, bg, sf, fg, mu, ln, theme = P
    rows = "".join(f'<div class="row"><span>{html.escape(n)}<small>{html.escape(d)}</small></span><span class="dots"></span><b>{p}</b></div>' for n, d, p in samples(l))
    badges = "".join(f'<span>{t}</span>' for t in (["Цены на сайте", "Свободные окна онлайн", "Запись в Telegram"] if kind(l)=="barber" else ["Цены на сайте", "Вопрос мастеру онлайн", "Заявки в Telegram"]))
    order = "" if v == 0 else "order:-1"
    return HEAD + f"""<style>{base_css(ac, bg, sf, fg, mu, ln, theme, ac + '26')}
body{{font-family:"Manrope",system-ui,sans-serif}}
.top{{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:18px 0;border-bottom:1px solid var(--ln)}}
.logo{{font-family:"Oswald",sans-serif;font-size:22px;text-transform:uppercase;letter-spacing:.04em}}
.pill{{display:inline-flex;gap:8px;align-items:center;background:var(--sf);border:1px solid var(--ln);border-radius:999px;padding:7px 14px;font-weight:700;font-size:14px}}
.pill i{{width:9px;height:9px;border-radius:50%;background:#5BC98A}}
.hero{{display:grid;grid-template-columns:1.1fr 1fr;gap:30px;align-items:center;padding:40px 0}}.hero>*{{min-width:0}}
h1{{font-family:"Oswald",sans-serif;text-transform:uppercase;font-size:clamp(34px,6vw,64px);line-height:1.1;letter-spacing:.01em}}
h1 em{{font-style:normal;color:var(--ac)}}
.lead{{font-size:17px;color:var(--mu);margin:16px 0 0;max-width:38ch}}
.badges{{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}}.badges span{{border:2px solid var(--ln);border-radius:8px;padding:5px 10px;font-weight:700;font-size:13px}}
.btns{{display:flex;gap:10px;margin-top:22px;flex-wrap:wrap}}.cta{{border-radius:8px;padding:13px 20px}}.ghost{{border:2px solid var(--ln);border-radius:8px;padding:11px 18px;font-weight:700}}
.panel{{{order};border-radius:20px;border:1px solid var(--ln);background:repeating-linear-gradient(0deg,transparent 0 31px,var(--ln) 31px 32px),repeating-linear-gradient(90deg,transparent 0 31px,var(--ln) 31px 32px),var(--sf);padding:18px}}
h2{{font-family:"Oswald",sans-serif;text-transform:uppercase;font-size:30px;margin-bottom:16px}}
section{{padding:34px 0 0}}
.table{{background:var(--sf);border:1px solid var(--ln);border-radius:14px;padding:6px 18px}}
.row{{display:flex;align-items:baseline;gap:10px;padding:13px 0;border-bottom:1px solid var(--ln);font-size:16px}}.row:last-child{{border:0}}.row small{{display:block;color:var(--mu);font-size:13px;margin-top:2px}}
.rate{{display:inline-flex;gap:6px;align-items:center;font-size:14px;color:var(--mu);margin-top:16px}}.rate b{{color:var(--fg)}}
.dots{{flex:1;border-bottom:2px dotted var(--ln);transform:translateY(-4px)}}.row b{{color:var(--ac)}}
.steps{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}
.steps div{{background:var(--sf);border:1px solid var(--ln);border-radius:14px;padding:18px}}
.steps b{{font-family:"Oswald",sans-serif;font-size:40px;color:var(--ac);line-height:1;display:block;margin-bottom:8px}}
.contact{{display:grid;grid-template-columns:1fr 1.3fr;gap:14px}}.box{{background:var(--sf);border:1px solid var(--ln);border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:8px}}
@media(max-width:720px){{.hero,.contact{{grid-template-columns:1fr}}.panel{{order:0}}.steps{{grid-template-columns:1fr}}.pill{{display:none}}}}
</style></head><body><div class="wrap">
<div class="top"><div class="logo">{name}</div><span class="pill"><i></i>Открыто сейчас</span></div>
<div class="hero"><div><p class="mu" style="font-weight:700;letter-spacing:.1em;text-transform:uppercase;font-size:13px">{html.escape(l["city"])} · {addr.split(", ",1)[1]}</p>
<h1 style="margin-top:12px">{html.escape(head)}</h1><p class="lead">{LEADTXT.get(kind(l), "Цены на все работы, часы работы и вопрос мастеру прямо с сайта.")}</p>
<div class="badges">{badges}</div>{rating_chip(l)}<div class="btns"><span class="cta">{cta}</span><span class="ghost">Цены</span></div></div>
<div class="panel">{art}</div></div>
<section><h2>Цены</h2><div class="table">{rows}</div><p class="mu" style="margin-top:10px;font-size:14px">{NOTETXT.get(kind(l), "Точную цену мастер назовёт после осмотра, диагностика бесплатная.")}</p></section>
{STEPS.get(kind(l)) or '''<section><h2>Как сдать в ремонт</h2><div class="steps"><div><b>1</b>Приносите вещь или пишете вопрос на сайте</div><div><b>2</b>Мастер смотрит и называет цену и срок</div><div><b>3</b>Забираете готовое, мы напомним в Telegram</div></div></section>'''}
<section><div class="contact"><div class="box"><h2 style="margin:0">Контакты</h2><p>{addr}</p><p class="mu">Telegram · WhatsApp · ВКонтакте</p><span class="cta" style="align-self:flex-start;border-radius:8px;padding:12px 18px">{cta}</span></div><div class="map"><i>{ICONS["pin"]}</i></div></div></section>
<footer>{name} · {html.escape(l["city"])}</footer></div></body></html>"""

def elegant(l, P, art, name, head, svcs, cta, addr, v):
    ac, ac2, bg, sf, fg, mu, ln, theme = P
    words = head.split(" ")
    h1 = html.escape(" ".join(words[:-1])) + f' <em>{html.escape(words[-1])}</em>'
    items = "".join(f'<div class="item"><span class="t">{html.escape(n)}<small>{html.escape(d)}</small></span><span class="dots"></span><span class="p">{p}</span></div>' for n, d, p in samples(l))
    k = kind(l); caps = TILES.get(k, ["Работа", "Работа", "Работа", "Работа"])
    combos = [(ac, ac2), (ac2, ac), ("#E9D5C6", ac), (ac, "#E9D5C6")]
    tiles = "".join(f'<div class="tile" style="background:linear-gradient(160deg,{c1}40,{c2}14)">{BY_KIND[k](c1, c2, "transparent", "#0b0d10")}<span>{t}</span></div>' for (c1, c2), t in zip(combos, caps))
    swap = "order:-1" if v == 0 else ""
    return HEAD + f"""<style>{base_css(ac, bg, sf, fg, mu, ln, theme, ac + '22')}
body{{font-family:"Manrope",system-ui,sans-serif}}
nav{{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;padding:20px 0;border-bottom:1px solid var(--ln);font-size:14px}}
nav .l{{display:flex;gap:18px;color:var(--mu)}}nav .r{{justify-self:end}}
.logo{{font-family:"Cormorant",serif;font-size:30px;font-weight:600}}
.cta{{border-radius:999px;padding:12px 22px}}.ghost{{border:1px solid var(--ln);border-radius:999px;padding:11px 20px;font-weight:700}}
.hero{{display:grid;grid-template-columns:1fr 1fr;gap:36px;align-items:center;padding:44px 0}}.hero>*{{min-width:0}}
.arch{{{swap};border-radius:220px 220px 24px 24px;background:var(--sf);border:1px solid var(--ln);padding:30px 18px 18px;overflow:hidden}}
.eyebrow{{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--mu);font-weight:700}}
h1{{font-family:"Cormorant",serif;font-weight:600;font-size:clamp(40px,6.4vw,74px);line-height:1;margin:14px 0}}
h1 em,h2 em{{color:var(--ac)}}
.lead{{color:var(--mu);font-size:17px;max-width:36ch}}.btns{{display:flex;gap:10px;margin-top:24px;flex-wrap:wrap}}
section{{padding:36px 0 0}}h2{{font-family:"Cormorant",serif;font-weight:600;font-size:44px;margin-bottom:16px}}
.list{{display:grid;grid-template-columns:1fr 1fr;gap:4px 40px}}
.item{{display:flex;align-items:baseline;gap:10px;padding:14px 0;border-bottom:1px solid var(--ln)}}.item .t{{font-family:"Cormorant",serif;font-size:24px;font-weight:600}}
.dots{{flex:1;border-bottom:1px dotted var(--mu);opacity:.5;transform:translateY(-6px)}}.item .p{{color:var(--ac);font-weight:700}}
.tiles{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}.tile{{aspect-ratio:1;border-radius:18px;border:1px solid var(--ln);display:flex;flex-direction:column;justify-content:space-between;padding:10px 12px 12px;font-size:14px;font-weight:700;overflow:hidden}}.tile svg{{width:100%;height:auto;flex:1;min-height:0}}
.item .t small{{display:block;font-family:"Manrope",sans-serif;font-size:13px;color:var(--mu);font-weight:400;margin-top:2px}}
.rate{{display:inline-flex;gap:6px;align-items:center;font-size:14px;color:var(--mu);margin-top:18px}}.rate b{{color:var(--fg)}}
.contact{{display:grid;grid-template-columns:1fr 1.3fr;gap:14px}}.box{{background:var(--sf);border:1px solid var(--ln);border-radius:24px;padding:22px;display:flex;flex-direction:column;gap:8px}}
@media(max-width:720px){{.hero,.contact,.list{{grid-template-columns:1fr}}.arch{{order:0}}nav{{grid-template-columns:1fr auto}}nav .l{{display:none}}.logo{{white-space:nowrap;font-size:26px}}.tiles{{grid-template-columns:1fr 1fr}}}}
</style></head><body><div class="wrap">
<nav><div class="l"><span>Услуги</span><span>Работы</span><span>Контакты</span></div><div class="logo">{name}</div><div class="r"><span class="cta">{cta}</span></div></nav>
<div class="hero"><div><p class="eyebrow">{html.escape(l["city"])} · запись онлайн</p><h1>{h1}</h1>
<p class="lead">Выберите услугу и удобное время прямо на сайте. Подтверждение придёт в Telegram.</p>
<div class="btns"><span class="cta">{cta}</span><span class="ghost">Услуги и цены</span></div>{rating_chip(l)}</div>
<div class="arch">{art}</div></div>
<section><h2>Услуги <em>и цены</em></h2><div class="list">{items}</div></section>
<section><h2>Наши <em>работы</em></h2><div class="tiles">{tiles}</div></section>
<section><div class="contact"><div class="box"><h2 style="margin:0;font-size:36px">Как нас найти</h2><p>{addr}</p><p class="mu">Telegram · WhatsApp · ВКонтакте</p><span class="cta" style="align-self:flex-start">{cta}</span></div><div class="map"><i>{ICONS["pin"]}</i></div></div></section>
<footer>{name} · {html.escape(l["city"])}</footer></div></body></html>"""

def friendly(l, P, art, name, head, svcs, cta, addr, v):
    ac, ac2, bg, sf, fg, mu, ln, theme = P
    k = kind(l)
    cards = "".join(f'<div class="card"><div class="sw" style="background:linear-gradient(160deg,{c1}38,{c2}18)">{BY_KIND[k](c1, c2, "transparent", fg)}</div><b>{html.escape(n)}</b><span class="mu">{html.escape(d)}</span><b class="pr">{p}</b></div>'
                    for (n, d, p), (c1, c2) in zip(samples(l), [(ac, ac2), (ac2, ac), (ac, "#E8B86A"), ("#8E5A3C", ac2)]))
    return HEAD + f"""<style>{base_css(ac, bg, sf, fg, mu, ln, theme, ac + '1f')}
body{{font-family:"Manrope",system-ui,sans-serif}}
.top{{display:flex;justify-content:space-between;align-items:center;padding:18px 0}}
.logo{{font-family:"Unbounded",sans-serif;font-size:18px}}.logo span{{color:var(--ac)}}
.cta{{border-radius:999px;padding:13px 22px}}.ghost{{border:1.5px solid var(--ln);background:var(--sf);border-radius:999px;padding:12px 20px;font-weight:700}}
.heroc{{background:linear-gradient(135deg,{ac}24,{ac2}22);border:1px solid var(--ln);border-radius:32px;padding:34px;display:grid;grid-template-columns:1.1fr 1fr;gap:20px;align-items:center}}.heroc>*{{min-width:0}}
h1{{font-family:"Unbounded",sans-serif;font-size:clamp(28px,4.6vw,50px);line-height:1.1}}
.lead{{color:var(--mu);font-size:17px;margin-top:14px;max-width:34ch}}.btns{{display:flex;gap:10px;margin-top:22px;flex-wrap:wrap}}
.chips{{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px}}.chips span{{background:var(--sf);border-radius:999px;padding:7px 12px;font-size:13px;font-weight:700;border:1px solid var(--ln)}}
section{{padding:36px 0 0}}h2{{font-family:"Unbounded",sans-serif;font-size:26px;margin-bottom:16px}}
.cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}}
.card{{background:var(--sf);border:1px solid var(--ln);border-radius:22px;padding:14px;display:flex;flex-direction:column;gap:8px}}.sw{{height:120px;border-radius:14px;display:flex;justify-content:center;overflow:hidden}}.sw svg{{height:100%;width:auto}}
.rate{{display:inline-flex;gap:6px;align-items:center;font-size:14px;color:var(--mu);margin-top:14px}}.rate b{{color:var(--fg)}}.pr{{color:var(--ac)}}
.steps{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}}.steps div{{display:flex;flex-direction:column;gap:8px}}
.steps i{{width:44px;height:44px;border-radius:50%;background:var(--ac);color:#fff;display:grid;place-items:center;font-style:normal;font-weight:700;font-family:"Unbounded",sans-serif}}
.contact{{display:grid;grid-template-columns:1fr 1.3fr;gap:14px}}.box{{background:var(--sf);border:1px solid var(--ln);border-radius:24px;padding:22px;display:flex;flex-direction:column;gap:8px}}
@media(max-width:720px){{.heroc,.contact{{grid-template-columns:1fr}}.cards,.steps{{grid-template-columns:1fr 1fr}}.heroc{{padding:22px}}}}
</style></head><body><div class="wrap">
<div class="top"><div class="logo">{name}</div><span class="cta">{cta}</span></div>
<div class="heroc"><div><h1>{html.escape(head)}</h1><p class="lead">Выберите, посчитайте цену и оставьте заявку. {addr}.</p>
<div class="btns"><span class="cta">{cta}</span><span class="ghost">Меню и цены</span></div>
<div class="chips"><span>Заказ онлайн</span><span>Цены на сайте</span><span>Ответ в Telegram</span></div>{rating_chip(l)}</div><div>{art}</div></div>
<section><h2>Меню</h2><div class="cards">{cards}</div></section>
<section><h2>Как заказать</h2><div class="steps"><div><i>1</i><b>Выберите</b><span class="mu">что и сколько</span></div><div><i>2</i><b>Оставьте заявку</b><span class="mu">имя и телефон</span></div><div><i>3</i><b>Подтверждение</b><span class="mu">в Telegram или WhatsApp</span></div><div><i>4</i><b>Заберите</b><span class="mu">или закажите доставку</span></div></div></section>
<section><div class="contact"><div class="box"><h2 style="margin:0">Контакты</h2><p>{addr}</p><p class="mu">Telegram · WhatsApp · ВКонтакте</p><span class="cta" style="align-self:flex-start">{cta}</span></div><div class="map"><i>{ICONS["pin"]}</i></div></div></section>
<footer>{name} · {html.escape(l["city"])}</footer></div></body></html>"""

def page(l):
    P = palette(l)
    ac, ac2, bg, sf, fg, mu, ln, theme = P
    name = html.escape(l["name"].split(",")[0].strip())
    k = kind(l)
    head, svcs, cta = CONTENT[k]
    alt = HEADS.get(k)
    if alt: head = alt[int(hashlib.md5((l["id"] + "h").encode()).hexdigest(), 16) % len(alt)]
    addr = html.escape(f'{l["city"]}, {l["addr"]}')
    v = int(hashlib.md5((l["id"] + "v").encode()).hexdigest(), 16) % 2
    art = BY_KIND[k](ac, ac2, (sf if theme == "dark" else ac + "18"), ("#0b0d10" if theme == "dark" else fg))
    return {"industrial": industrial, "elegant": elegant, "friendly": friendly}[LAYOUT[k]](l, P, art, name, head, svcs, cta, addr, v)

if __name__ == "__main__":
    leads = [json.load(open(f)) | {"id": os.path.basename(f)[:-5]} for f in glob.glob(os.environ.get("LEADS_DIR", DB) + "/*.json")]
    jobs = []
    for l in leads:
        p = f"{TMP}/{l['id']}.html"; open(p, "w").write(page(l))
        jobs += [{"src": p, "out": f"{TMP}/{l['id']}_d.png", "w": 1280, "h": 800, "scale": 2},
                 {"src": p, "out": f"{TMP}/{l['id']}_f.png", "w": 390, "h": 844, "full": True, "scale": 2},
                 {"src": p, "out": f"{TMP}/{l['id']}_m.png", "w": 390, "h": 844, "scale": 2}]
    shoot(jobs)
    for l in leads:
        ac, _, bg, *_ = palette(l)
        dark = bg if palette(l)[7] == 'dark' else '#1A1D22'
        name = l["name"].split(",")[0].strip()
        cover(f"{TMP}/{l['id']}_d.png", f"{TMP}/{l['id']}_f.png", f"{TMP}/{l['id']}_m.png", f"{OUT}/{l['id']}.jpg",
              f"Так может выглядеть сайт: {name}", "Компьютер и телефон, заявки сразу в Telegram", ac, dark,
              note="Концепт: тексты и цены условные, на настоящем сайте будут ваши")
    print("done", len(leads))
