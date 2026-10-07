# -*- coding: utf-8 -*-
"""سازندهٔ دفترچهٔ تصویری «گزارش ۱۴بندی» — پروژهٔ نقشهٔ نورا
خروجی: docs/06-approval-deck/board-XX.png  +  report-14pt.pdf
هیچ طراحی نهایی اینجا تولید نمی‌شود؛ این دفترچه، سند تأیید است.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display
import img2pdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs/06-approval-deck')
os.makedirs(OUT, exist_ok=True)
FD = os.path.join(ROOT, 'assets/print/fonts')

W, H = 1600, 1131
BG = (247, 244, 239)
NAVY = (7, 20, 38)
INK = (28, 34, 46)
SOFT = (108, 116, 130)
GOLD = (170, 130, 66)
LINE = (222, 215, 204)
CARD = (255, 255, 255)
GREEN = (38, 110, 62)
RED = (150, 52, 52)
AMBER = (150, 110, 20)

_cache = {}
def F(w, s):
    k = (w, s)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(f'{FD}/Vazirmatn-{w}.ttf', s)
    return _cache[k]

def fa(t):
    return get_display(arabic_reshaper.reshape(t))

def T(d, xy, t, f, fill, anchor='ra'):
    d.text(xy, fa(t), font=f, fill=fill, anchor=anchor)

def line_h(t, f):
    return f.getbbox(fa(t))[3] - f.getbbox(fa(t))[1]

# ---------- صفحه ----------
class Board:
    def __init__(self, num, total, kicker, title, subtitle=''):
        self.im = Image.new('RGB', (W, H), BG)
        self.d = ImageDraw.Draw(self.im)
        d = self.d
        d.rectangle((0, 0, W, 96), fill=NAVY)
        T(d, (W - 44, 26), title, F('Bold', 40), (255, 255, 255), 'ra')
        T(d, (40, 34), kicker, F('Medium', 26), (196, 172, 120), 'la')
        T(d, (40, 66), f'۱۴ / {num}', F('Regular', 22), (150, 160, 175), 'la')
        if subtitle:
            T(d, (W - 44, 112), subtitle, F('Regular', 25), SOFT, 'ra')
        # پاصفحه
        d.line((40, H - 52, W - 40, H - 52), fill=LINE, width=2)
        T(d, (W // 2, H - 44), 'این دفترچه سند تأیید است — تا امضای شما، هیچ طراحی نهایی تولید نمی‌شود', F('Regular', 20), SOFT)
    def save(self, name):
        p = os.path.join(OUT, name)
        self.im.save(p)
        return p

def panel(b, box, fill=CARD, outline=LINE, r=16):
    b.d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=2)

def img_fit(path, w, h):
    im = Image.open(path).convert('RGB')
    im.thumbnail((w, h), Image.LANCZOS)
    return im

def place_img(b, path, x, y, w, h, frame=True, radius=10):
    im = img_fit(path, w, h)
    px = x + (w - im.width) // 2
    py = y + (h - im.height) // 2
    if frame:
        b.d.rounded_rectangle((px - 4, py - 4, px + im.width + 4, py + im.height + 4), radius=radius, outline=LINE, width=2, fill=(255, 255, 255))
    b.im.paste(im, (px, py))
    return (px, py, im.width, im.height)

def wrap_lines(text, f, max_w):
    """شکست متن فارسی به سطرها بر پایهٔ پهنای واقعی."""
    words, lines, cur = text.split(' '), [], ''
    for wd in words:
        cand = (cur + ' ' + wd).strip()
        if f.getlength(fa(cand)) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines

def Tw(b, x_right, y, text, f, fill, max_w, gap=8):
    """متن RTL با شکست خودکار؛ y جدید را برمی‌گرداند."""
    for ln in wrap_lines(text, f, max_w):
        T(b.d, (x_right, y), ln, f, fill, 'ra')
        y += f.size + gap
    return y

def bullets(b, items, x_right, y, w, fbody=24, gap=14, tag_w=None, size=None):
    """فهرست RTL با نشانگر نقطه‌ای طلایی و شکست خودکار."""
    d = b.d
    for it in items:
        mark, text, color = (it if len(it) == 3 else (it[0], it[1], INK))
        f = F('Medium', size or fbody)
        d.ellipse((x_right + 8, y + (f.size * 0.42), x_right + 16, y + (f.size * 0.42) + 8), fill=GOLD)
        y = Tw(b, x_right - 10, y, text, f, color, max(w, 200)) + gap
    return y

def kv_table(b, rows, x_right, y, w, key_w, fk=23, fv=23, gap=12):
    d = b.d
    for k, v, c in rows:
        T(d, (x_right, y), k, F('Bold', fk), NAVY, 'ra')
        T(d, (x_right - key_w, y), v, F('Regular', fv), c, 'ra')
        y += fk + gap
    return y

# ---------- شماتیک A5 (نمودار جای‌گذاری، نه طراحی) ----------
def a5_schematic(b, x, y, h=560, eye_path=False, qr=False):
    d = b.d
    w = int(h * 148 / 210)
    d.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=(255, 255, 255), outline=(190, 184, 172), width=2)
    d.rounded_rectangle((x + 12, y + 12, x + w - 12, y + h - 12), radius=6, outline=(216, 208, 196), width=2)  # حاشیهٔ امن
    zones = [(0.06, 0.05, 0.60), (0.68, 0.24, 0.30), (0.06, 0.30, 0.34)]
    return (x, y, w, h)

def zone(b, x, y, w, h, label, fill=(238, 234, 227), fs=20, tc=(120, 126, 138)):
    b.d.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=fill, outline=(214, 208, 197), width=2)
    if label:
        T(b.d, (x + w - 10, y + h - 30), label, F('Medium', fs), tc)

def arrow(b, p1, p2, color=GOLD, width=4):
    b.d.line((p1, p2), fill=color, width=width)

def badge(b, x, y, n, r=19, fill=GOLD, tc=(255, 255, 255)):
    b.d.ellipse((x - r, y - r, x + r, y + r), fill=fill)
    T(b.d, (x, y - r + 5), str(n), F('Bold', 24), tc)

def swatch_row(b, x, y, colors, w=74, h=74, gap=10, labels=None):
    for i, c in enumerate(colors):
        xx = x + i * (w + gap)
        b.d.rounded_rectangle((xx, y, xx + w, y + h), radius=10, fill=c, outline=LINE, width=2)
        if labels:
            T(b.d, (xx + w // 2, y + h + 8), labels[i], F('Regular', 17), SOFT)
