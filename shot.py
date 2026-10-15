"""Скриншоты страниц. Google Fonts в песочнице недоступны, поэтому подменяем их локальными шрифтами."""
import sys, json
from playwright.sync_api import sync_playwright

FONT_CSS = ""  # шрифты Google установлены в систему (/usr/share/fonts/truetype/gf), подмена не нужна

def shoot(jobs):
    """jobs: list of {src (file path or html string), out, w, h, full, dark}"""
    with sync_playwright() as p:
        b = p.chromium.launch()
        for j in jobs:
            ctx = b.new_context(viewport={"width": j.get("w", 1280), "height": j.get("h", 800)},
                                device_scale_factor=j.get("scale", 1),
                                color_scheme="dark" if j.get("dark") else "light")
            ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=FONT_CSS))
            ctx.route("https://fonts.gstatic.com/**", lambda r: r.abort())
            pg = ctx.new_page()
            if j["src"].startswith("<"):
                pg.set_content(j["src"], wait_until="load")
            else:
                pg.goto("file://" + j["src"], wait_until="load")
            if j.get("css"): pg.add_style_tag(content=j["css"])
            pg.wait_for_timeout(j.get("wait", 900))
            pg.screenshot(path=j["out"], full_page=j.get("full", False))
            ctx.close()
        b.close()

if __name__ == "__main__":
    shoot(json.load(open(sys.argv[1])))
