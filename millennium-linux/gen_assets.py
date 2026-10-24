#!/usr/bin/env python3
"""Generates the Millennium Linux wallpaper and xfwm4 window theme (PNG)."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
INC = os.path.join(ROOT, "config/includes.chroot")
XFWM = os.path.join(INC, "usr/share/themes/Millennium/xfwm4")
BG = os.path.join(INC, "usr/share/backgrounds/millennium")
os.makedirs(XFWM, exist_ok=True); os.makedirs(BG, exist_ok=True)

def hexrgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def vgrad(w, h, stops):
    """vertical gradient; stops = [(pos0..1, '#rrggbb'), ...] -> RGBA image"""
    ys = np.linspace(0, 1, h)
    out = np.zeros((h, w, 4), dtype=np.uint8)
    for c in range(3):
        col = np.interp(ys, [s[0] for s in stops], [hexrgb(s[1])[c] for s in stops])
        out[:, :, c] = col[:, None]
    out[:, :, 3] = 255
    return Image.fromarray(out, "RGBA")

# ---------------------------------------------------------------- title bars
H = 28
ACT = [(0, '#bfeaff'), (0.45, '#3aa6e8'), (0.5, '#1479c4'), (1, '#0b5aa0')]
INA = [(0, '#f4f7fa'), (0.45, '#cfd9e3'), (0.5, '#b9c6d3'), (1, '#a3b2c1')]

def titlebar(w, stops, gloss=0.42):
    im = vgrad(w, H, stops)
    g = Image.new("RGBA", (w, H), (255, 255, 255, 0))
    gd = ImageDraw.Draw(g)
    for y in range(H // 2):
        a = int(255 * gloss * (1 - y / (H / 2)) ** 0.8)
        gd.line([(0, y), (w, y)], fill=(255, 255, 255, a))
    im = Image.alpha_composite(im, g)
    d = ImageDraw.Draw(im)
    d.line([(0, 0), (w, 0)], fill=(255, 255, 255, 230))
    return im

def corner(w, stops, right=False):
    S = 8
    base = titlebar(w, stops).resize((w * S, H * S), Image.NEAREST)
    mask = Image.new("L", (w * S, H * S), 0)
    md = ImageDraw.Draw(mask)
    r = 10 * S
    md.rounded_rectangle([0 if not right else -r, 0, w * S + (r if not right else 0) - 1, H * S + r], radius=r, fill=255)
    base.putalpha(mask)
    return base.resize((w, H), Image.LANCZOS)

def save(name, im): im.save(os.path.join(XFWM, name + ".png"))

for state, stops in (("active", ACT), ("inactive", INA)):
    for i in range(1, 6):
        save(f"title-{i}-{state}", titlebar(2 if i != 3 else 2, stops))
    save(f"top-left-{state}", corner(8, stops))
    save(f"top-right-{state}", corner(8, stops, True))
    edge = ('#1a78bf', '#7cc4f0', '#0b5aa0') if state == "active" else ('#8a9aab', '#dfe6ee', '#7c8c9d')
    # side borders (4 px wide)
    side = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
    for x, c in enumerate([edge[0], edge[1], edge[1], edge[2]]):
        for y in range(4): side.putpixel((x, y), hexrgb(c) + (255,))
    save(f"left-{state}", side)
    rs = side.transpose(Image.FLIP_LEFT_RIGHT); save(f"right-{state}", rs)
    bot = Image.new("RGBA", (4, 5), (0, 0, 0, 0))
    for y, c in enumerate([edge[1], edge[1], edge[0], edge[2], edge[2]]):
        for x in range(4): bot.putpixel((x, y), hexrgb(c) + (255,))
    save(f"bottom-{state}", bot)
    for nm, flip in (("bottom-left", False), ("bottom-right", True)):
        S = 8; w, h = 8, 5
        big = Image.new("RGBA", (w * S, h * S), hexrgb(edge[2]) + (255,))
        bd = ImageDraw.Draw(big)
        bd.rectangle([0, 0, 4 * S - 1, h * S], fill=hexrgb(edge[0]) + (255,))
        m = Image.new("L", (w * S, h * S), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, -12 * S, w * S + 8 * S, h * S - 1], radius=6 * S, fill=255)
        big.putalpha(m)
        im = big.resize((w, h), Image.LANCZOS)
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        save(f"{nm}-{state}", im)

# ---------------------------------------------------------------- buttons
BS = 20; SS = 8
PAL = {  # base colours (top, bottom)
    "close":    ('#ffb089', '#e0420f'),
    "maximize": ('#b9f58f', '#2fae3a'),
    "hide":     ('#fff2a0', '#e8a912'),
    "menu":     ('#c9ecff', '#2a8fd8'),
    "shade":    ('#e1d4ff', '#7a55d6'),
    "stick":    ('#ffd0ec', '#d63fa0'),
}
GRAY = ('#f0f3f6', '#98a6b4')

def adjust(hexc, f):
    r, g, b = hexrgb(hexc)
    if f >= 1: return tuple(min(255, int(v + (255 - v) * (f - 1))) for v in (r, g, b))
    return tuple(int(v * f) for v in (r, g, b))

def glyph(d, kind, toggled, S, col):
    c = BS * S / 2; w = int(1.9 * S)
    if kind == "close":
        a = 6.0 * S
        d.line([(c-a/1.0*0.55, c-a*0.55), (c+a*0.55, c+a*0.55)], fill=col, width=w)
        d.line([(c-a*0.55, c+a*0.55), (c+a*0.55, c-a*0.55)], fill=col, width=w)
    elif kind == "maximize":
        if not toggled:
            d.rectangle([c-4*S, c-4*S, c+4*S, c+4*S], outline=col, width=w)
            d.line([(c-4*S, c-4*S+w//2), (c+4*S, c-4*S+w//2)], fill=col, width=int(2.8*S))
        else:
            d.rectangle([c-2*S, c-4.5*S, c+4.5*S, c+2*S], outline=col, width=int(1.5*S))
            d.rectangle([c-4.5*S, c-2*S, c+2*S, c+4.5*S], outline=col, width=int(1.5*S))
    elif kind == "hide":
        d.line([(c-4*S, c+3.5*S), (c+4*S, c+3.5*S)], fill=col, width=int(2.6*S))
    elif kind == "menu":
        d.polygon([(c-4*S, c-2*S), (c+4*S, c-2*S), (c, c+3.5*S)], fill=col)
    elif kind == "shade":
        d.polygon([(c-4*S, c+2.5*S), (c+4*S, c+2.5*S), (c, c-3*S)], fill=col)
    elif kind == "stick":
        d.ellipse([c-3*S, c-3*S, c+3*S, c+3*S], fill=col)

def orb(kind, state, toggled=False, gray=False):
    S = SS; N = BS * S
    top, bot = GRAY if gray else PAL[kind]
    f = {"normal": 1.0, "prelight": 1.25, "pressed": 0.78}[state]
    t, b = adjust(top, f), adjust(bot, f)
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    mask = Image.new("L", (N, N), 0)
    ImageDraw.Draw(mask).ellipse([S, S, N - S, N - S], fill=255)
    grad = vgrad(N, N, [(0, '#%02x%02x%02x' % t), (1, '#%02x%02x%02x' % b)])
    if state == "pressed": grad = grad.transpose(Image.FLIP_TOP_BOTTOM)
    grad.putalpha(mask); im = Image.alpha_composite(im, grad)
    d = ImageDraw.Draw(im)
    dark = adjust(bot, 0.55)
    d.ellipse([S, S, N - S, N - S], outline=dark + (255,), width=int(1.2 * S))
    # inner rim light
    d.ellipse([2.4*S, 2.4*S, N-2.4*S, N-2.4*S], outline=(255, 255, 255, 110), width=int(0.8*S))
    # gloss highlight
    gl = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    gd.ellipse([3.6*S, 2.0*S, N-3.6*S, N*0.52], fill=(255, 255, 255, 150))
    gl = gl.filter(ImageFilter.GaussianBlur(S * 0.5))
    im = Image.alpha_composite(im, gl)
    d = ImageDraw.Draw(im)
    gcol = (255, 255, 255, 255) if not gray else (70, 85, 100, 255)
    # glyph shadow then glyph
    sh = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    glyph(ImageDraw.Draw(sh), kind, toggled, S, (0, 30, 60, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(S * 0.4))
    im = Image.alpha_composite(im, sh.transform(sh.size, Image.AFFINE, (1, 0, 0, 0, 1, -S*0.6)))
    glyph(ImageDraw.Draw(im), kind, toggled, S, gcol)
    return im.resize((BS, BS), Image.LANCZOS)

for kind in PAL:
    toggles = [False, True] if kind == "maximize" else [False]
    for tg in toggles:
        pre = f"{kind}-toggled" if tg else kind
        save(f"{pre}-active", orb(kind, "normal", tg))
        save(f"{pre}-inactive", orb(kind, "normal", tg, gray=True))
        save(f"{pre}-prelight", orb(kind, "prelight", tg))
        save(f"{pre}-pressed", orb(kind, "pressed", tg))
        if kind == "stick":
            pass
# stick-toggled for completeness
for s in ("active", "inactive", "prelight", "pressed"):
    save(f"stick-toggled-{s}", orb("stick", {"active": "normal", "inactive": "normal"}.get(s, s), True, gray=(s == "inactive")))
for s in ("active", "inactive", "prelight", "pressed"):
    save(f"shade-toggled-{s}", orb("shade", {"active": "normal", "inactive": "normal"}.get(s, s), True, gray=(s == "inactive")))

with open(os.path.join(XFWM, "themerc"), "w") as f:
    f.write("""button_layout=O|HMC
button_offset=6
button_spacing=3
full_width_title=true
maximized_offset=0
show_app_icon=false
title_horizontal_offset=4
title_shadow_active=frame
title_shadow_inactive=false
title_vertical_offset_active=0
title_vertical_offset_inactive=0
active_text_color=#ffffff
inactive_text_color=#5d6e80
active_text_shadow_color=#06335c
inactive_text_shadow_color=#ffffff
""")

# ---------------------------------------------------------------- wallpaper
W, HH = 1366, 768
random.seed(2000)
y, x = np.mgrid[0:HH, 0:W]
dist = np.sqrt(((x - W*0.62) / W) ** 2 + ((y - HH*0.35) / HH) ** 2)
t = np.clip(dist * 1.5, 0, 1)
c1 = np.array(hexrgb('#5fe0ff'), float); c2 = np.array(hexrgb('#0a7fd0'), float); c3 = np.array(hexrgb('#05358a'), float)
img = np.where(t[..., None] < 0.5, c1 + (c2 - c1) * (t[..., None] / 0.5), c2 + (c3 - c2) * ((t[..., None] - 0.5) / 0.5))
wp = Image.fromarray(img.astype(np.uint8), "RGB").convert("RGBA")

# swooshes
sw = Image.new("RGBA", (W, HH), (0, 0, 0, 0)); sd = ImageDraw.Draw(sw)
for k, (amp, ph, yy, a) in enumerate([(70, 0.0, 520, 70), (55, 1.2, 560, 55), (90, 2.2, 470, 40), (40, 3.1, 610, 60)]):
    top = [(xx, yy + amp * math.sin(xx / 210 + ph)) for xx in range(-20, W + 40, 8)]
    bottom = [(xx, yy + 90 + amp * 0.6 * math.sin(xx / 170 + ph + 1)) for xx in range(W + 40, -21, -8)]
    sd.polygon(top + bottom, fill=(255, 255, 255, a // 2))
    sd.line(top, fill=(255, 255, 255, a + 60), width=3)
sw = sw.filter(ImageFilter.GaussianBlur(1.2))
wp = Image.alpha_composite(wp, sw)

# perspective grid at the bottom
gr = Image.new("RGBA", (W, HH), (0, 0, 0, 0)); gd = ImageDraw.Draw(gr)
hor = 600
for i in range(14):
    yy = hor + (i / 13) ** 2.0 * (HH - hor)
    gd.line([(0, yy), (W, yy)], fill=(190, 240, 255, 55), width=1)
for i in range(-20, 21):
    gd.line([(W / 2 + i * 12, hor), (W / 2 + i * 140, HH)], fill=(190, 240, 255, 55), width=1)
wp = Image.alpha_composite(wp, gr)

# glossy bubbles
def bubble(cx, cy, r, alpha=90):
    S = 3; n = int(r * 2 * S) + 8 * S
    b = Image.new("RGBA", (n, n), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
    o = 4 * S; R = r * S
    bd.ellipse([o, o, o + 2 * R, o + 2 * R], fill=(255, 255, 255, alpha // 3), outline=(255, 255, 255, alpha + 80), width=max(2, int(S * r / 40)))
    hl = Image.new("RGBA", (n, n), (0, 0, 0, 0)); hd = ImageDraw.Draw(hl)
    hd.ellipse([o + R * 0.28, o + R * 0.1, o + R * 1.72, o + R * 0.9], fill=(255, 255, 255, alpha + 40))
    hl = hl.filter(ImageFilter.GaussianBlur(R * 0.06))
    b = Image.alpha_composite(b, hl)
    return b.resize((n // S, n // S), Image.LANCZOS)
for _ in range(26):
    r = random.choice([12, 18, 26, 34, 48, 70, 110])
    bx, by = random.randint(-20, W), random.randint(-20, HH - 60)
    bb = bubble(bx, by, r, random.randint(50, 110))
    wp.alpha_composite(bb, (max(0, min(W - bb.width, bx)), max(0, min(HH - bb.height, by))))
bg = bubble(0, 0, 150, 120); wp.alpha_composite(bg, (880, 120))

# sparkles
def sparkle(d, cx, cy, r, a=230):
    pts = []
    for i in range(8):
        ang = i * math.pi / 4; rr = r if i % 2 == 0 else r * 0.18
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=(255, 255, 255, a))
spk = Image.new("RGBA", (W, HH), (0, 0, 0, 0)); sd = ImageDraw.Draw(spk)
for cx, cy, r in [(1080, 110, 26), (210, 120, 18), (700, 80, 12), (1250, 330, 20), (420, 300, 10), (1000, 420, 14)]:
    sparkle(sd, cx, cy, r)
wp = Image.alpha_composite(wp, spk.filter(ImageFilter.GaussianBlur(0.6)))

# logo text
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
tl = Image.new("RGBA", (W, HH), (0, 0, 0, 0)); td = ImageDraw.Draw(tl)
f1 = ImageFont.truetype(FB, 64); f2 = ImageFont.truetype(FR, 22)
td.text((62, 56), "Millennium", font=f1, fill=(4, 50, 110, 160))
td.text((58, 52), "Millennium", font=f1, fill=(255, 255, 255, 255))
td.text((60, 126), "L I N U X   ·   v 2 0 0 0 . 1", font=f2, fill=(255, 255, 255, 230))
wp = Image.alpha_composite(wp, tl)
wp.convert("RGB").save(os.path.join(BG, "millennium.png"))
wp.convert("RGB").resize((683, 384)).save("/home/claude/preview_wallpaper.png")
print("assets ok")
