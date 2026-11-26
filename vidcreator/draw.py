"""Simple 2D character + scene drawing with Pillow (no external assets)."""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FONT_REG = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size,
                              layout_engine=ImageFont.Layout.RAQM)


def draw_background(d, bg):
    d.rectangle([0, 0, W, H], fill=bg.get("sky", "#bfe3ff"))
    d.rectangle([0, 520, W, H], fill=bg.get("floor", "#d9b98c"))
    if bg.get("label"):
        d.text((30, 20), bg["label"], font=font(34, True), fill="#00000066")


def draw_character(d, x, y, t, speaking, style, mood="happy"):
    """x,y = feet position. t = time in seconds (for idle bob / mouth flap)."""
    skin = style.get("skin", "#f1c27d")
    shirt = style.get("shirt", "#e63946")
    hair = style.get("hair", "#222222")
    bob = math.sin(t * 3) * 5
    y = y + bob
    # legs
    d.rectangle([x - 40, y - 100, x - 8, y], fill="#2b2d42")
    d.rectangle([x + 8, y - 100, x + 40, y], fill="#2b2d42")
    # body
    d.rounded_rectangle([x - 60, y - 260, x + 60, y - 90], 25, fill=shirt)
    # arms (wave while speaking)
    wave = math.sin(t * 8) * 25 if speaking else 0
    d.line([x - 60, y - 235, x - 100, y - 160 + wave], fill=skin, width=22)
    d.line([x + 60, y - 235, x + 100, y - 160 - wave], fill=skin, width=22)
    # head
    hx, hy = x, y - 330
    d.ellipse([hx - 65, hy - 65, hx + 65, hy + 65], fill=skin)
    d.pieslice([hx - 68, hy - 72, hx + 68, hy + 40], 180, 360, fill=hair)
    # eyes (blink every ~3s)
    blink = (t % 3.0) < 0.12
    for ex in (-24, 24):
        if blink:
            d.line([hx + ex - 9, hy - 8, hx + ex + 9, hy - 8], fill="black", width=3)
        else:
            d.ellipse([hx + ex - 8, hy - 16, hx + ex + 8, hy], fill="white", outline="black")
            d.ellipse([hx + ex - 4, hy - 12, hx + ex + 4, hy - 4], fill="black")
    # mouth
    if speaking:
        open_h = 6 + abs(math.sin(t * 14)) * 16
        d.ellipse([hx - 16, hy + 22, hx + 16, hy + 22 + open_h], fill="#7a1f1f")
    elif mood == "sad":
        d.arc([hx - 18, hy + 28, hx + 18, hy + 52], 200, 340, fill="black", width=4)
    else:
        d.arc([hx - 20, hy + 14, hx + 20, hy + 44], 20, 160, fill="black", width=4)


def draw_label(d, x, y, name):
    f = font(26, True)
    w = d.textlength(name, font=f)
    d.rounded_rectangle([x - w / 2 - 12, y, x + w / 2 + 12, y + 40], 12, fill="#ffffffcc")
    d.text((x - w / 2, y + 3), name, font=f, fill="#222")


def draw_subtitle(d, text):
    f = font(40, True)
    # simple word wrap
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f) > W - 160 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    lines.append(cur)
    box_h = 56 * len(lines) + 24
    d.rounded_rectangle([60, H - box_h - 30, W - 60, H - 30], 20, fill="#000000bb")
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=f)
        d.text(((W - tw) / 2, H - box_h - 18 + i * 56), ln, font=f, fill="white")


def draw_title_card(title, subtitle=""):
    img = Image.new("RGB", (W, H), "#14213d")
    d = ImageDraw.Draw(img)
    f = font(84, True)
    tw = d.textlength(title, font=f)
    d.text(((W - tw) / 2, 260), title, font=f, fill="#fca311")
    if subtitle:
        f2 = font(44)
        sw = d.textlength(subtitle, font=f2)
        d.text(((W - sw) / 2, 390), subtitle, font=f2, fill="white")
    return img
