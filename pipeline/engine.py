"""Contentmotor: carrousels (PNG + PDF) en shorts (MP4) uit specificaties, in de huisstijl van zorg of Novins."""
import asyncio, base64, pathlib, re, shutil, subprocess
from PIL import Image
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).parent
B = ROOT / "brand"

def b64(p): return base64.b64encode((B / p).read_bytes()).decode()

FONTS = f"""@font-face{{font-family:Figtree;font-weight:400;src:url(data:font/ttf;base64,{b64('Figtree-Regular.ttf')})}}
@font-face{{font-family:Figtree;font-weight:700 800;src:url(data:font/ttf;base64,{b64('Figtree-Bold.ttf')})}}
@font-face{{font-family:Figtree;font-style:italic;font-weight:400;src:url(data:font/ttf;base64,{b64('Figtree-Italic.ttf')})}}"""
TILE = b64("circuit-navy-tile.png")
LOGO_W = b64("novins-logo-horizontal-tagline-white.png")
LOGO_C = b64("novins-logo-horizontal-tagline.png")

# ---------- iconen (lijntekening, 24 raster) ----------
I = {
 "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6l8-3z"/>',
 "check": '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6l8-3z"/><path d="M9 12l2 2 4-4"/>',
 "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
 "laptop": '<rect x="4" y="5" width="16" height="10" rx="1.5"/><path d="M2 19h20"/>',
 "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
 "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M15 8l2 2"/>',
 "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 "book": '<path d="M4 4h11a3 3 0 0 1 3 3v13H7a3 3 0 0 1-3-3z"/><path d="M8 8h6M8 12h6"/>',
 "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/>',
 "users": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14c3 0 5 2.2 5 5"/>',
 "userx": '<circle cx="10" cy="8" r="4"/><path d="M2 21c0-4.4 3.6-8 8-8 1.5 0 2.9.4 4 1.1"/><path d="M17 16l4 4M21 16l-4 4"/>',
 "phone": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
 "call": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
 "wifi": '<path d="M2 9a15 15 0 0 1 20 0M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0"/><circle cx="12" cy="19.5" r="1"/>',
 "usb": '<rect x="8" y="10" width="8" height="12" rx="1.5"/><path d="M9 10V3h6v7M11 6h.01M13 6h.01"/>',
 "doc": '<path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6M9 13h8M9 17h6"/>',
 "euro": '<path d="M18 6a7 7 0 1 0 0 12"/><path d="M4 10h9M4 14h9"/>',
 "cloud": '<path d="M7 18a5 5 0 1 1 1-9.9A6 6 0 0 1 19.6 10 4 4 0 0 1 18 18z"/>',
 "server": '<rect x="4" y="3" width="16" height="7" rx="1.5"/><rect x="4" y="14" width="16" height="7" rx="1.5"/><path d="M8 6.5h.01M8 17.5h.01"/>',
 "refresh": '<path d="M20 11a8 8 0 0 0-14.6-4.4L4 8M4 13a8 8 0 0 0 14.6 4.4L20 16"/><path d="M4 3v5h5M20 21v-5h-5"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "bell": '<path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4z"/><path d="M10 21h4"/>',
 "list": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/>',
 "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
 "printer": '<path d="M7 9V3h10v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M7 14h10v7H7z"/>',
 "qr": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><path d="M14 14h3v3M21 14v7h-4M17 21v-2"/>',
 "home": '<path d="M3 11l9-8 9 8"/><path d="M5 10v11h14V10"/>',
 "car": '<path d="M5 16l1.5-6h11L19 16"/><rect x="3" y="16" width="18" height="4" rx="1"/><circle cx="7" cy="20" r="1.5"/><circle cx="17" cy="20" r="1.5"/>',
 "trash": '<path d="M4 7h16M9 7V4h6v3M6 7l1 14h10l1-14"/>',
 "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
 "chart": '<path d="M4 20V4M4 20h16"/><path d="M8 16v-4M12 16V8M16 16v-6"/>',
 "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
 "link": '<path d="M10 14a4 4 0 0 0 5.6 0l3-3a4 4 0 0 0-5.6-5.6l-1 1"/><path d="M14 10a4 4 0 0 0-5.6 0l-3 3a4 4 0 0 0 5.6 5.6l1-1"/>',
 "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
 "flag": '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
 "award": '<circle cx="12" cy="9" r="6"/><path d="M8.5 14L7 22l5-3 5 3-1.5-8"/>',
}
def ico(name, size=64, color="currentColor", sw=1.8):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" class="ln">{I[name]}</svg>')

# ---------- huisstijl ----------
COMMON = """*{box-sizing:border-box;margin:0}body{font-family:Figtree,sans-serif}
.s{position:relative;overflow:hidden;background:var(--bg);color:var(--body)}
.top{display:flex;align-items:center;gap:20px;position:relative}
.eyebrow{font-weight:800;text-transform:uppercase;letter-spacing:.13em;color:var(--acc)}
h1,h2{font-weight:800;color:var(--head);letter-spacing:-.018em;position:relative}
p{line-height:1.42;position:relative}
.dark{--bg:var(--dbg);--head:#fff;--body:var(--dbody);--acc:var(--dacc)}
.alt{--bg:var(--abg)}
.row{display:flex;align-items:center;border-top:2px solid var(--line);position:relative}
.row:last-child{border-bottom:2px solid var(--line)}
.ic{flex:none;display:grid;place-items:center;background:var(--chip);color:var(--acc)}
.dark .ic{background:rgba(255,255,255,.1)}
.row p{color:var(--head);font-weight:400}
.step{display:flex;position:relative}
.num{flex:none;display:grid;place-items:center;font-weight:800;color:var(--acc)}
.step h3{font-weight:800;color:var(--head)}
.big{font-weight:800;line-height:.92;color:var(--bigc);letter-spacing:-.04em;white-space:nowrap;position:relative}
.src{color:var(--muted);position:relative}
.btn{display:inline-block;background:var(--btn);color:#fff;font-weight:800;position:relative}
.url{font-weight:800;color:var(--urlc);position:relative}
.art{color:var(--acc)}
.foot{position:absolute;display:flex;justify-content:space-between;align-items:center;color:var(--muted)}
.dots{display:flex;gap:10px}.dots i{width:12px;height:12px;border-radius:50%;background:var(--line)}.dots i.on{background:var(--acc);width:36px;border-radius:6px}
.dark .dots i{background:rgba(255,255,255,.28)}
.circuit{position:absolute;inset:0;background-image:url(data:image/png;base64,""" + TILE + """);background-size:760px auto;background-position:center}
.scrim{position:absolute;inset:0;background:linear-gradient(to top,#0b2355 0%,rgba(11,35,85,.93) 48%,rgba(11,35,85,.4) 100%)}
.rule{width:72px;height:6px;background:var(--acc);margin-top:30px;position:relative}
"""
BRANDS = {
 "zorg": dict(css=""":root{--bg:#fff;--abg:#E6F2F0;--dbg:#0B2355;--head:#0B2355;--body:#2E3A4A;--dbody:#C9D2E3;--acc:#0E7C70;--dacc:#9FD8CF;
   --line:#E2E6EC;--chip:#E6F2F0;--muted:#5A6575;--bigc:#0E7C70;--btn:#0E7C70;--urlc:#0E7C70}
   .dark{--bigc:#9FD8CF;--urlc:#9FD8CF;--muted:#C9D2E3}
   .mark{width:64px;height:64px;border-radius:14px;background:#0E7C70;display:grid;place-items:center}
   .name{font-weight:800;font-size:30px;color:#0B2355}.name b{color:#0E7C70}.dark .name{color:#fff}.dark .name b{color:#9FD8CF}
   .sub{font-size:20px;color:#5A6575}.dark .sub{color:#C9D2E3}.rule{display:none}
   .num{border:4px solid var(--acc);border-radius:50%}.ic{border-radius:24px}.btn{border-radius:14px}""",
   url="informatiebeveiligingindezorg.nl", cta_btn="Doe de gratis zelfcheck"),
 "novins": dict(css=""":root{--bg:#fff;--abg:#eeeff3;--dbg:#172e63;--head:#0b2355;--body:#333a4a;--dbody:#a7b4cf;--acc:#e84e0f;--dacc:#fff;
   --line:#dfe2e9;--chip:#fdf0ea;--muted:#6f778a;--bigc:#e84e0f;--btn:#e84e0f;--urlc:#e84e0f}
   .dark{--bigc:#fff;--urlc:#fff;--muted:#a7b4cf}.dark .rule{background:#e84e0f}
   .logo{height:84px;position:relative}.num{border:0}.num{color:#e84e0f}.ic{border-radius:8px}.btn{border-radius:6px}
   .dark .ic{color:#fff}""",
   url="novins.nl/contact", cta_btn="Neem contact op"),
}

def header(brand, dark):
    if brand == "zorg":
        return f"""<div class="top"><div class="mark">{ico('shield',36,'#fff',2.2).replace('</svg>','<path d="M12 9v6M9 12h6"/></svg>')}</div>
        <div><div class="name">informatiebeveiliging <b>in de zorg</b></div><div class="sub">een <em>Novins</em> initiatief</div></div></div>"""
    return f'<img class="logo" src="data:image/png;base64,{LOGO_W if dark else LOGO_C}">'

def bg_layers(brand, dark):
    return '<div class="circuit"></div><div class="scrim"></div>' if (brand == "novins" and dark) else ""

# ---------- carrousel (1080x1350) ----------
CAR = """.s{width:1080px;height:1350px;padding:96px 96px 0}
.eyebrow{font-size:28px}h1{font-size:88px;line-height:1.04}h2{font-size:68px;line-height:1.08}p{font-size:36px}
.row{gap:36px;padding:32px 0}.row .ic{width:104px;height:104px}.row p{font-size:38px}
.step{gap:36px;padding:28px 0}.num{width:92px;height:92px;font-size:44px}.step h3{font-size:42px;margin-bottom:8px}.step p{font-size:32px}
.big{font-size:300px}.src{font-size:24px;margin-top:36px}.btn{font-size:38px;padding:30px 48px}.url{font-size:40px;margin-top:30px}
.foot{left:96px;right:96px;bottom:72px;font-size:24px}.swipe{font-weight:800;color:var(--acc)}"""

def dots(i, n): return '<div class="dots">' + ''.join(f'<i class="{"on" if k==i else ""}"></i>' for k in range(n)) + '</div>'

def car_slide(brand, s, i, n):
    t = s["t"]; dark = s.get("dark", t in ("stat",) or (brand == "novins" and t in ("hook", "cta")))
    cls = "s" + (" dark" if dark else "") + (" alt" if s.get("alt") else "")
    foot = f'<div class="foot"><span class="swipe">{"Swipe &rarr;" if i == 0 else ""}</span>{dots(i, n)}</div>'
    h = header(brand, dark)
    if t == "hook":
        art = "" if brand == "novins" else f'<div class="art" style="position:absolute;right:80px;bottom:150px">{ico(s.get("icon","shield"),380,sw=1.1)}</div>'
        pos = 'style="position:absolute;left:96px;right:96px;bottom:220px"' if brand == "novins" else 'style="margin-top:110px"'
        inner = f'<div {pos}><div class="eyebrow">{s["eyebrow"]}</div><h1 style="margin-top:24px">{s["title"]}</h1><div class="rule"></div></div>'
        body = inner + art
    elif t == "list":
        body = f'<h2 style="margin:96px 0 48px">{s["title"]}</h2><div class="rule" style="margin:-24px 0 48px"></div>' + \
            ''.join(f'<div class="row"><div class="ic">{ico(ic,56)}</div><p>{tx}</p></div>' for ic, tx in s["items"])
    elif t == "steps":
        body = f'<h2 style="margin:96px 0 40px">{s["title"]}</h2><div class="rule" style="margin:-16px 0 36px"></div>' + \
            ''.join(f'<div class="step"><div class="num">{k+1}</div><div><h3>{hh}</h3><p>{pp}</p></div></div>' for k, (hh, pp) in enumerate(s["items"]))
    elif t == "stat":
        body = f'<div class="big" style="margin-top:170px;font-size:{s.get("size",300)}px">{s["big"]}</div>' \
               f'<p style="margin-top:56px;font-size:44px;line-height:1.34;color:#fff">{s["text"]}</p>' + \
               (f'<p style="margin-top:26px">{s["sub"]}</p>' if s.get("sub") else "") + \
               (f'<div class="src">Bron: {s["src"]}</div>' if s.get("src") else "")
    elif t == "text":
        body = f'<div class="art" style="margin-top:110px;position:relative">{ico(s.get("icon","book"),150,sw=1.3)}</div>' \
               f'<h2 style="margin-top:40px">{s["title"]}</h2><div class="rule"></div><p style="margin-top:36px">{s["body"]}</p>' + \
               (f'<div class="src">Bron: {s["src"]}</div>' if s.get("src") else "")
    elif t == "cta":
        B_ = BRANDS[brand]
        body = f'<div style="margin-top:{150 if brand=="zorg" else 330}px"><h2>{s["title"]}</h2><div class="rule"></div>' \
               f'<p style="margin-top:36px">{s["body"]}</p><div class="btn" style="margin-top:60px">{s.get("button", B_["cta_btn"])}</div>' \
               f'<div class="url">{B_["url"]}</div></div>' + \
               (f'<div class="art" style="position:absolute;right:96px;bottom:150px">{ico("check",200,sw=1.3)}</div>' if brand == "zorg" else "")
    return f'<div class="{cls}">{bg_layers(brand,dark)}{h}{body}{foot}</div>'

# ---------- short (1080x1920) ----------
SHORT = """.s{width:1080px;height:1920px;padding:150px 96px 0}
.eyebrow{font-size:32px}h1{font-size:104px;line-height:1.03}h2{font-size:86px;line-height:1.07}p{font-size:46px}
.row{gap:40px;padding:40px 0}.row .ic{width:120px;height:120px}.row p{font-size:48px}
.step{gap:40px;padding:42px 0}.num{width:112px;height:112px;font-size:52px}.step h3{font-size:54px;margin-bottom:10px}.step p{font-size:40px}
.big{font-size:300px}.src{font-size:30px;margin-top:40px}.btn{font-size:46px;padding:34px 56px}.url{font-size:44px;margin-top:34px}
.bar{position:absolute;left:0;bottom:0;height:12px;background:var(--acc);animation:bar var(--d) linear forwards;width:0}
@keyframes bar{to{width:100%}}
.in{opacity:0;animation:in .7s cubic-bezier(.2,.7,.2,1) forwards}@keyframes in{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:none}}
.pop{opacity:0;animation:pop .6s cubic-bezier(.2,.8,.2,1.2) forwards}@keyframes pop{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:none}}
.draw .ln *{stroke-dasharray:160;stroke-dashoffset:160;animation:draw 1.6s ease forwards}@keyframes draw{to{stroke-dashoffset:0}}
.circuit{animation:drift 6s linear forwards}@keyframes drift{to{background-position:60px 120px}}"""

def D(x): return f"animation-delay:{x}s"

def short_scene(brand, s, dur):
    t = s["t"]; dark = s.get("dark", t in ("stat",) or (brand == "novins" and t in ("hook", "cta")))
    cls = "s" + (" dark" if dark else "") + (" alt" if s.get("alt") else "")
    h = header(brand, dark)
    if t == "hook":
        art = "" if brand == "novins" else f'<div class="art draw" style="position:absolute;left:50%;bottom:300px;transform:translateX(-50%)">{ico(s.get("icon","shield"),460,sw=1.0)}</div>'
        top = 900 if brand == "novins" else 190
        body = f'<div style="margin-top:{top}px"><div class="eyebrow in" style="{D(.2)}">{s["eyebrow"]}</div>' \
               f'<h1 class="in" style="margin-top:28px;{D(.4)}">{s["title"]}</h1>' + \
               (f'<h2 class="in" style="margin-top:30px;color:var(--acc);font-size:64px;{D(1.2)}">{s["sub"]}</h2>' if s.get("sub") else "") + \
               f'<div class="rule in" style="{D(1.4)}"></div></div>' + art
    elif t == "list":
        body = f'<h2 class="in" style="margin:170px 0 60px;{D(.1)}">{s["title"]}</h2>' + \
            ''.join(f'<div class="row in" style="{D(.6+k*.5)}"><div class="ic">{ico(ic,64)}</div><p>{tx}</p></div>' for k, (ic, tx) in enumerate(s["items"]))
    elif t == "steps":
        body = f'<h2 class="in" style="margin:170px 0 50px;{D(.1)}">{s["title"]}</h2>' + \
            ''.join(f'<div class="step in" style="{D(.7+k*.7)}"><div class="num">{k+1}</div><div><h3>{hh}</h3><p>{pp}</p></div></div>' for k, (hh, pp) in enumerate(s["items"]))
    elif t == "stat":
        body = f'<div class="big pop" style="margin-top:360px;font-size:{s.get("ssize",280)}px;{D(.2)}">{s["big"]}</div>' \
               f'<p class="in" style="margin-top:70px;font-size:54px;line-height:1.3;color:#fff;{D(1.0)}">{s["text"]}</p>' + \
               (f'<p class="in" style="margin-top:34px;font-size:42px;{D(1.8)}">{s["sub"]}</p>' if s.get("sub") else "") + \
               (f'<div class="src in" style="position:absolute;left:96px;bottom:110px;{D(2.2)}">Bron: {s["src"]}</div>' if s.get("src") else "")
    elif t == "text":
        body = f'<div class="art draw" style="margin-top:200px;position:relative">{ico(s.get("icon","book"),200,sw=1.3)}</div>' \
               f'<h2 class="in" style="margin-top:50px;{D(.5)}">{s["title"]}</h2><p class="in" style="margin-top:44px;{D(1.2)}">{s["body"]}</p>' + \
               (f'<div class="src in" style="position:absolute;left:96px;bottom:110px;{D(1.8)}">Bron: {s["src"]}</div>' if s.get("src") else "")
    elif t == "cta":
        B_ = BRANDS[brand]
        body = f'<div style="margin-top:{260 if brand=="zorg" else 760}px"><h2 class="in" style="{D(.1)}">{s["title"]}</h2>' \
               f'<p class="in" style="margin-top:44px;{D(.8)}">{s["body"]}</p>' \
               f'<div class="btn pop" style="margin-top:70px;{D(1.5)}">{s.get("button", B_["cta_btn"])}</div>' \
               f'<div class="url in" style="{D(2.0)}">{B_["url"]}</div></div>'
    return f'<div class="{cls}">{bg_layers(brand,dark)}{h}{body}<div class="bar" style="--d:{dur}s"></div></div>'

def page(brand, extra, body, w, h):
    return f"<!doctype html><html><head><meta charset=utf-8><style>{FONTS}{COMMON}{BRANDS[brand]['css']}{extra}</style></head><body style='width:{w}px;height:{h}px'>{body}</body></html>"

FIT = """for(const el of document.querySelectorAll('h1,h2,.row p,.step h3')){let fs=parseFloat(getComputedStyle(el).fontSize);const box=el.parentElement.getBoundingClientRect();let n=0;while(n<40&&(el.scrollWidth>el.clientWidth+1||el.getBoundingClientRect().right>1080-80)){fs-=2;el.style.fontSize=fs+'px';n++}}"""

def scene_dur(s):
    return {"hook": 3.6, "list": 4.6, "steps": 5.0, "stat": 4.4, "text": 4.4, "cta": 4.0}[s["t"]]

async def render_all(items, out, fps=30):
    out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        import os
        b = await (pw.chromium.launch(executable_path="/usr/bin/google-chrome") if os.path.exists("/usr/bin/google-chrome") else pw.chromium.launch())
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        for it in items:
            if it["kind"] != "carousel": continue
            d = out / it["id"]; d.mkdir(exist_ok=True)
            n = len(it["slides"])
            for i, s in enumerate(it["slides"]):
                await pg.set_content(page(it["brand"], CAR, car_slide(it["brand"], s, i, n), 1080, 1350), wait_until="load")
                await pg.evaluate("document.fonts.ready")
                await pg.evaluate(FIT)
                await pg.screenshot(path=str(d / f"slide-{i+1:02d}.png"))
            ims = [Image.open(d / f"slide-{i+1:02d}.png").convert("RGB") for i in range(n)]
            ims[0].save(out / f"{it['id']}.pdf", save_all=True, append_images=ims[1:], resolution=150)
        await pg.set_viewport_size({"width": 1080, "height": 1920})
        for it in items:
            if it["kind"] != "short": continue
            fr = out / (it["id"] + "_frames")
            if fr.exists(): shutil.rmtree(fr)
            fr.mkdir()
            k = 0
            for s in it["scenes"]:
                dur = scene_dur(s)
                await pg.set_content(page(it["brand"], SHORT, short_scene(it["brand"], s, dur), 1080, 1920), wait_until="load")
                await pg.evaluate("document.fonts.ready")
                await pg.evaluate(FIT)
                for f in range(int(dur * fps)):
                    await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={f*1000/fps}}})")
                    await pg.screenshot(path=str(fr / f"f{k:05d}.jpg"), type="jpeg", quality=90)
                    k += 1
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(fr / "f%05d.jpg"),
                            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "libx264",
                            "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "64k",
                            "-movflags", "+faststart", str(out / f"{it['id']}.mp4")], check=True)
            shutil.rmtree(fr)
            print("short", it["id"], flush=True)
        await b.close()
