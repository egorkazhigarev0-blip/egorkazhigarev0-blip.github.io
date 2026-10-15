"""Иллюстрации для первого экрана: объём за счёт градиентов, бликов и мягких теней.
Цвета: a — акцент, b — второй тон, s — подложка, k — тёмный контур/тень."""
import itertools
_n = itertools.count()

def _shade(hexc, f):
    hexc = hexc.lstrip("#")[:6]
    r, g, b = (int(hexc[i:i + 2], 16) for i in (0, 2, 4))
    if f >= 0: r, g, b = (int(c + (255 - c) * f) for c in (r, g, b))
    else: r, g, b = (int(c * (1 + f)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"

class Svg:
    def __init__(self):
        self.p = f"i{next(_n)}"; self.defs = []
    def lin(self, c1, c2, x2="0", y2="1"):
        gid = f"{self.p}l{len(self.defs)}"
        self.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')
        return f"url(#{gid})"
    def rad(self, c, o=1):
        gid = f"{self.p}r{len(self.defs)}"
        self.defs.append(f'<radialGradient id="{gid}" cx="50%" cy="45%" r="55%"><stop offset="0" stop-color="{c}" stop-opacity="{o}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')
        return f"url(#{gid})"
    def blur(self, sd=10):
        gid = f"{self.p}f{len(self.defs)}"
        self.defs.append(f'<filter id="{gid}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
        return f"url(#{gid})"
    def wrap(self, inner, s):
        glow = self.rad(s)
        sh = self.blur(9)
        return (f'<svg class="illus" viewBox="0 0 480 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs>{"".join(self.defs)}</defs>'
                f'<circle cx="240" cy="200" r="195" fill="{glow}"/>{inner.replace("SHADOW", sh)}</svg>')

def spark(x, y, r, c, o=1):
    return f'<path d="M{x} {y-r}l{r*.28} {r*.72} {r*.72} {r*.28}-{r*.72} {r*.28}-{r*.28} {r*.72}-{r*.28}-{r*.72}-{r*.72}-{r*.28} {r*.72}-{r*.28}z" fill="{c}" opacity="{o}"/>'

def shadow(cx, cy, rx, ry, k, o=.28):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{k}" opacity="{o}" filter="SHADOW"/>'

def cake(a, b, s, k, cream="#FFF6F0", choc="#5A3426"):
    S = Svg()
    top = S.lin(_shade(a, .15), _shade(a, -.15)); cr = S.lin(cream, _shade(cream, -.08)); ch = S.lin(_shade(choc, .1), choc)
    berries = "".join(f'<circle cx="{x}" cy="{y}" r="11" fill="{S.lin(_shade(a,.2), _shade(a,-.25))}"/><circle cx="{x-4}" cy="{y-4}" r="3" fill="#fff" opacity=".7"/>' for x, y in [(196, 112), (226, 102), (256, 102), (286, 112)])
    candles = "".join(f'<rect x="{x}" y="58" width="9" height="40" rx="3" fill="{S.lin(_shade(b,.3), b)}"/><path d="M{x+1} 66l7-4M{x+1} 78l7-4M{x+1} 90l7-4" stroke="#fff" stroke-width="2" opacity=".6"/><path d="M{x+4.5} 40c8 8 5 15 0 17c-5-2-8-9 0-17z" fill="#FFC35A"/><circle cx="{x+4.5}" cy="50" r="12" fill="#FFC35A" opacity=".18"/>' for x in (218, 254))
    return S.wrap(f'''{shadow(240, 340, 160, 14, k)}
<ellipse cx="240" cy="326" rx="160" ry="20" fill="{_shade(s,-.05) if s.startswith('#') and len(s)==7 else '#EDE4E0'}"/><ellipse cx="240" cy="320" rx="150" ry="16" fill="#FFFFFF"/>
<rect x="112" y="222" width="256" height="96" rx="18" fill="{cr}"/>
<rect x="112" y="290" width="256" height="28" rx="10" fill="{top}"/>
<path d="M112 236q21 30 42 0t43 0t43 0t43 0t43 0t42 0v-14h-256z" fill="{ch}"/>
<rect x="148" y="146" width="184" height="86" rx="16" fill="{top}"/>
<rect x="160" y="160" width="10" height="56" rx="5" fill="#fff" opacity=".18"/>
<path d="M148 158q18 24 37 0t37 0t37 0t37 0t36 0v-12h-184z" fill="{ch}"/>
<rect x="184" y="100" width="112" height="56" rx="14" fill="{cr}"/>
{berries}{candles}
{spark(396, 120, 16, b)}{spark(88, 176, 11, a, .7)}{spark(372, 250, 8, a, .6)}''', s)

def bread(a, b, s, k):
    S = Svg()
    crust = S.lin("#E6A85E", "#B86F2C"); light = S.lin("#F2C88A", "#D99A52"); cup = S.lin(_shade(a, .2), _shade(a, -.2))
    return S.wrap(f'''{shadow(240, 336, 170, 14, k)}
<rect x="80" y="304" width="320" height="24" rx="12" fill="{S.lin('#E3CDB0','#C9AE8C')}"/>
<path d="M104 304c0-76 56-128 136-128s136 52 136 128z" fill="{crust}"/>
<path d="M150 236c22-14 44-14 66 0M206 212c22-14 44-14 66 0M262 236c22-14 44-14 66 0" stroke="#F6D7A6" stroke-width="9" fill="none" stroke-linecap="round"/>
<path d="M130 290c20-50 60-80 110-84" stroke="#fff" stroke-width="6" opacity=".18" fill="none" stroke-linecap="round"/>
<path d="M296 168c34-46 104-36 110 12c-36 12-70 22-110-12z" fill="{light}"/><path d="M314 164c16-14 42-16 58-4M330 176c12-8 30-8 40 0" stroke="#FBE3B8" stroke-width="5" fill="none" stroke-linecap="round"/>
<rect x="90" y="148" width="76" height="86" rx="12" fill="{cup}"/><rect x="98" y="156" width="10" height="66" rx="5" fill="#fff" opacity=".22"/>
<path d="M166 168h16a16 16 0 010 32h-16" stroke="{_shade(a,-.1)}" stroke-width="9" fill="none"/>
<path d="M114 130c-7-13 7-18 0-31M140 130c-7-13 7-18 0-31" stroke="{b}" stroke-width="5" fill="none" stroke-linecap="round" opacity=".8"/>
{spark(410, 250, 10, b, .7)}''', s)

def nails(a, b, s, k):
    S = Svg()
    def bottle(x, c, h):
        body = S.lin(_shade(c, .25), _shade(c, -.2), "1", "0")
        cap = S.lin(_shade(k, .3), k, "1", "0")
        return f'''<rect x="{x+18}" y="{300-h-56}" width="30" height="58" rx="7" fill="{cap}"/>
<path d="M{x} {300-h+14}q0-16 16-16h34q16 0 16 16v{h-28}q0 14-14 14h-38q-14 0-14-14z" fill="{body}"/>
<rect x="{x+10}" y="{300-h+20}" width="9" height="{h-46}" rx="4.5" fill="#fff" opacity=".4"/>
<rect x="{x+12}" y="{300-h*0.55}" width="42" height="{h*0.32}" rx="6" fill="#fff" opacity=".9"/><rect x="{x+18}" y="{300-h*0.55+10}" width="30" height="5" rx="2.5" fill="{c}" opacity=".7"/>'''
    drops = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{S.lin(_shade(c,.3), _shade(c,-.15))}"/><circle cx="{x-r*.35}" cy="{y-r*.35}" r="{r*.25}" fill="#fff" opacity=".6"/>' for x, y, r, c in [(380, 146, 28, a), (404, 200, 19, b), (366, 232, 13, "#D9A79B")])
    return S.wrap(f'''{shadow(236, 312, 160, 14, k)}
{bottle(96, a, 152)}{bottle(188, b, 186)}{bottle(280, "#D9A79B", 140)}{drops}
<g transform="rotate(-38 120 120)"><rect x="70" y="112" width="110" height="10" rx="5" fill="{S.lin(_shade(k,.3), k, '1','0')}"/><path d="M180 112l26 5-26 5z" fill="{a}"/></g>
{spark(84, 214, 13, b)}{spark(420, 90, 9, a, .7)}''', s)

def salon(a, b, s, k):
    S = Svg()
    blade = S.lin("#F4F4F6", "#A9ADB6", "1", "1"); ring = S.lin(_shade(a, .25), _shade(a, -.2)); comb = S.lin(_shade(b, .2), _shade(b, -.2))
    return S.wrap(f'''{shadow(240, 336, 150, 14, k)}
<path d="M176 46L246 206" stroke="{blade}" stroke-width="16" stroke-linecap="round"/>
<path d="M304 46L234 206" stroke="{blade}" stroke-width="16" stroke-linecap="round"/>
<path d="M240 200L206 252M240 200L274 252" stroke="{ring}" stroke-width="13" stroke-linecap="round"/>
<circle cx="196" cy="280" r="32" fill="none" stroke="{ring}" stroke-width="14"/><circle cx="284" cy="280" r="32" fill="none" stroke="{ring}" stroke-width="14"/>
<circle cx="240" cy="200" r="10" fill="{k}"/><circle cx="237" cy="197" r="3" fill="#fff" opacity=".7"/>
<rect x="334" y="96" width="34" height="190" rx="12" fill="{comb}"/>
{''.join(f'<rect x="322" y="{108+i*15}" width="16" height="5" rx="2.5" fill="{comb}"/>' for i in range(11))}
<path d="M90 120c30 10 40 40 30 70" stroke="{b}" stroke-width="5" fill="none" stroke-linecap="round" opacity=".6"/>
{spark(110, 250, 14, a)}{spark(410, 320, 9, b, .7)}''', s)

def tan(a, b, s, k):
    S = Svg()
    sun = S.lin(_shade(a, .3), _shade(a, -.1)); bot = S.lin(_shade(b, .25), _shade(b, -.2), "1", "0")
    rays = "".join(f'<rect x="236" y="30" width="8" height="34" rx="4" fill="{_shade(a,.2)}" opacity=".85" transform="rotate({i*30} 240 140)"/>' for i in range(12))
    return S.wrap(f'''{rays}<circle cx="240" cy="140" r="72" fill="{sun}"/><circle cx="214" cy="114" r="18" fill="#fff" opacity=".3"/>
{shadow(240, 340, 150, 14, k)}
<rect x="130" y="230" width="78" height="100" rx="18" fill="{bot}"/><rect x="152" y="206" width="34" height="28" rx="7" fill="{k}"/><rect x="142" y="244" width="10" height="70" rx="5" fill="#fff" opacity=".3"/>
<rect x="226" y="246" width="132" height="84" rx="20" fill="#fff" opacity=".95"/><path d="M248 280h86M248 300h56" stroke="{a}" stroke-width="9" stroke-linecap="round"/>
{spark(388, 220, 12, b)}''', s)

def watch(a, b, s, k):
    S = Svg()
    case = S.lin(_shade(a, .35), _shade(a, -.25), "1", "1"); strap = S.lin(_shade(b, .1), _shade(b, -.25)); face = S.rad("#FFFFFF")
    ticks = "".join(f'<rect x="238" y="{116 if i%3 else 112}" width="4" height="{14 if i%3 else 20}" rx="2" fill="{k}" transform="rotate({i*30} 240 200)"/>' for i in range(12))
    return S.wrap(f'''{shadow(240, 350, 130, 14, k)}
<path d="M196 28h88l-6 92h-76z" fill="{strap}"/><path d="M202 280h76l6 92h-88z" fill="{strap}"/>
{''.join(f'<rect x="206" y="{44+i*18}" width="68" height="3" rx="1.5" fill="#000" opacity=".12"/>' for i in range(4))}
<circle cx="240" cy="200" r="104" fill="{case}"/><circle cx="240" cy="200" r="88" fill="#FBFAF6"/><circle cx="240" cy="200" r="88" fill="{face}" opacity=".6"/>
{ticks}
<path d="M240 200V140" stroke="{k}" stroke-width="7" stroke-linecap="round"/><path d="M240 200l40 26" stroke="{k}" stroke-width="5" stroke-linecap="round"/>
<path d="M240 200l-30 52" stroke="{_shade(a,-.1)}" stroke-width="2.5" stroke-linecap="round"/>
<circle cx="240" cy="200" r="8" fill="{k}"/><rect x="340" y="186" width="20" height="28" rx="6" fill="{case}"/>
<path d="M170 140a90 90 0 0140-36" stroke="#fff" stroke-width="10" opacity=".5" fill="none" stroke-linecap="round"/>
{spark(92, 150, 14, a)}{spark(404, 300, 9, b, .7)}''', s)

def shoe(a, b, s, k):
    S = Svg()
    leather = S.lin(_shade(a, .2), _shade(a, -.25)); sole = S.lin(_shade(k, .25), k)
    return S.wrap(f'''{shadow(240, 330, 175, 14, k)}
<path d="M74 290c0-44 10-124 42-156h74c10 52 52 84 114 94c64 10 104 22 104 62z" fill="{leather}"/>
<path d="M116 134h74c4 22 12 40 24 54c-40-4-80-24-98-54z" fill="#000" opacity=".12"/>
<path d="M74 290h334v20q0 10-10 10H84q-10 0-10-10z" fill="{sole}"/>
<path d="M84 304h314" stroke="#fff" stroke-width="2" stroke-dasharray="6 6" opacity=".35"/>
<path d="M110 130h84" stroke="{_shade(a,-.35)}" stroke-width="12" stroke-linecap="round"/>
{''.join(f'<circle cx="{148+i*21}" cy="{172+i*13}" r="6" fill="#F5F1EA"/><circle cx="{148+i*21}" cy="{172+i*13}" r="2.5" fill="{k}"/>' for i in range(4))}
<path d="M150 168l80 50M170 162l70 48" stroke="#F5F1EA" stroke-width="3" opacity=".8"/>
<path d="M296 234c34 6 66 12 88 30" stroke="#fff" stroke-width="7" opacity=".28" fill="none" stroke-linecap="round"/>
<g transform="rotate(35 368 116)"><rect x="358" y="56" width="20" height="112" rx="7" fill="{S.lin(_shade(b,.2), _shade(b,-.2), '1','0')}"/><rect x="350" y="34" width="36" height="32" rx="7" fill="{k}"/></g>
{spark(96, 100, 12, b, .8)}''', s)

def phone(a, b, s, k):
    S = Svg()
    body = S.lin(_shade(k, .35), k, "1", "1"); scr = S.lin(_shade(a, .25), _shade(a, -.3))
    return S.wrap(f'''{shadow(240, 350, 120, 14, k)}
<rect x="156" y="34" width="168" height="310" rx="30" fill="{body}"/>
<rect x="169" y="50" width="142" height="278" rx="20" fill="{scr}"/>
<path d="M188 118l42 42-32 42 54 64" stroke="#fff" stroke-width="5" fill="none" opacity=".75" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M230 160l40-12M198 202l-14 30" stroke="#fff" stroke-width="3" opacity=".55" stroke-linecap="round"/>
<rect x="214" y="58" width="52" height="10" rx="5" fill="{k}"/><path d="M182 70l40 220" stroke="#fff" stroke-width="16" opacity=".08"/>
<g transform="rotate(-32 372 220)"><rect x="364" y="132" width="16" height="140" rx="6" fill="{S.lin(_shade(b,.2), _shade(b,-.2), '1','0')}"/><path d="M364 132l8-30 8 30z" fill="#C9CCD2"/></g>
{spark(96, 150, 14, b)}{spark(110, 290, 9, a, .7)}''', s)

def tools(a, b, s, k):
    S = Svg()
    leather = S.lin(_shade(a, .2), _shade(a, -.25)); case = S.lin(_shade(b, .3), _shade(b, -.2), "1", "1"); key = S.lin(_shade(b, .35), _shade(b, -.1), "1", "1")
    return S.wrap(f'''{shadow(230, 338, 185, 14, k)}
<path d="M66 300c0-34 8-96 32-120h56c8 38 38 62 84 70c46 8 78 16 78 50z" fill="{leather}"/>
<path d="M66 300h250v16q0 8-8 8H74q-8 0-8-8z" fill="{S.lin(_shade(k,.25), k)}"/>
{''.join(f'<circle cx="{120+i*18}" cy="{204+i*11}" r="5" fill="#F5F1EA"/>' for i in range(3))}
<circle cx="352" cy="148" r="70" fill="{case}"/><circle cx="352" cy="148" r="56" fill="#FBFAF6"/>
{''.join(f'<rect x="350" y="98" width="4" height="10" rx="2" fill="{k}" transform="rotate({i*30} 352 148)"/>' for i in range(12))}
<path d="M352 148v-36M352 148l26 16" stroke="{k}" stroke-width="6" stroke-linecap="round"/><circle cx="352" cy="148" r="6" fill="{k}"/>
<g transform="rotate(-38 150 104)"><circle cx="150" cy="104" r="28" fill="none" stroke="{key}" stroke-width="13"/><rect x="174" y="98" width="96" height="13" rx="6.5" fill="{key}"/>
<rect x="238" y="108" width="11" height="18" rx="3" fill="{key}"/><rect x="256" y="108" width="11" height="13" rx="3" fill="{key}"/></g>
{spark(420, 270, 11, a, .8)}''', s)

BY_KIND = {"cake": cake, "bakery": bread, "nails": nails, "salon": salon, "tan": tan,
           "watch": watch, "shoe": shoe, "phone": phone, "other": tools, "barber": salon}
