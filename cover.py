"""Обложка в подаче «кейс»: ноутбук по центру, длинные скриншоты страницы по бокам, телефон поверх."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MANROPE = "/usr/share/fonts/truetype/gf/Manrope[wght].ttf"
BOLD, REG = (MANROPE, 800), (MANROPE, 500)

def _font(spec, size):
    path, w = spec
    try:
        f = ImageFont.truetype(path, size)
        try: f.set_variation_by_axes([w])
        except Exception: pass
        return f
    except Exception:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)

def _round(img, r):
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, *img.size], r, fill=255)
    out = Image.new("RGBA", img.size); out.paste(img, (0, 0), m); return out

def _shadow(canvas, box, r=18, blur=22, alpha=110):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 14, x1, y1 + 14], r, fill=(0, 0, 0, alpha))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))

def _hex(c):
    c = c.lstrip("#"); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

def cover(desktop, full, phone, out, title, sub, accent="#E2457F", bg="#141015", note=None, swatches=None):
    W, H = 1600, 1000
    base = Image.new("RGBA", (W, H), _hex(bg) + (255,))
    # мягкое свечение акцентом
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow); a = _hex(accent)
    gd.ellipse([W * 0.45, -350, W * 1.25, 450], fill=a + (90,)); gd.ellipse([-300, H * 0.6, 500, H + 300], fill=a + (45,))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(base)
    # заголовок
    size = 46
    ft, fs = _font(BOLD, size), _font(REG, 22)
    while d.textlength(title, font=ft) > W - 120 and size > 26:
        size -= 2; ft = _font(BOLD, size)
    tw = d.textlength(title, font=ft)
    d.text(((W - tw) / 2, 40), title, fill="#FFFFFF", font=ft)
    sw = d.textlength(sub, font=fs)
    d.text(((W - sw) / 2, 104), sub, fill=(255, 255, 255, 190), font=fs)
    # длинные скриншоты по бокам
    fp = Image.open(full).convert("RGB")
    sw_, sh_ = 300, 640
    scale = sw_ / fp.width
    def strip(y0):
        tall = fp.resize((sw_, int(fp.height * sw_ / fp.width)), Image.LANCZOS)
        y0 = max(0, min(y0, tall.height - sh_))
        return _round(tall.crop((0, y0, sw_, y0 + sh_)), 14)
    th = int(fp.height * sw_ / fp.width)
    left = strip(int(th * 0.22)); right = strip(th)
    for img, x in ((left, 70), (right, W - 70 - sw_)):
        _shadow(base, (x, 230, x + sw_, 230 + sh_))
        base.alpha_composite(img, (x, 230))
    # ноутбук
    lw, lh = 860, 538
    lx, ly = (W - lw) // 2, 190
    _shadow(base, (lx - 18, ly - 18, lx + lw + 18, ly + lh + 18), r=26, alpha=150)
    d.rounded_rectangle([lx - 18, ly - 18, lx + lw + 18, ly + lh + 18], 26, fill="#0E0E10", outline="#2A2A2E", width=2)
    scr = Image.open(desktop).convert("RGB").resize((lw, lh), Image.LANCZOS)
    base.alpha_composite(_round(scr, 6), (lx, ly))
    # подставка ноутбука
    by = ly + lh + 18
    d.polygon([(lx - 90, by), (lx + lw + 90, by), (lx + lw + 60, by + 26), (lx - 60, by + 26)], fill="#C9CBD0")
    d.rounded_rectangle([W // 2 - 70, by, W // 2 + 70, by + 8], 4, fill="#A9ABB0")
    # телефон
    pw, ph = 250, 540
    px, py = W - 70 - sw_ - 60, H - ph - 50
    _shadow(base, (px - 12, py - 12, px + pw + 12, py + ph + 12), r=40, alpha=160)
    d.rounded_rectangle([px - 12, py - 12, px + pw + 12, py + ph + 12], 42, fill="#0E0E10", outline="#3A3A40", width=2)
    pim = Image.open(phone).convert("RGB")
    pim = pim.resize((pw, int(pim.height * pw / pim.width)), Image.LANCZOS).crop((0, 0, pw, ph))
    base.alpha_composite(_round(pim, 32), (px, py))
    if note:
        fn = _font(REG, 19); nw = d.textlength(note, font=fn)
        sw = swatches or []
        r, gap = 9, 7
        sww = len(sw) * (2 * r + gap) + (14 if sw else 0)
        x0 = (W - nw - sww) / 2
        for i, c in enumerate(sw):
            cx = x0 + r + i * (2 * r + gap); cy = H - 24
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=_hex(c) + (255,), outline=(255, 255, 255, 120), width=2)
        d.text((x0 + sww, H - 36), note, fill=(255, 255, 255, 175), font=fn)
    base.convert("RGB").save(out, "JPEG", quality=92, optimize=True)
