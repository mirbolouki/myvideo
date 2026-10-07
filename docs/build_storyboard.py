#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""برد استوری «نقشهٔ نورا» — پیش‌نمایش فاز ۱ (قبل از طراحی نهایی)
خروجی: docs/03-storyboard-preview.png
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
FD = "assets/print/fonts"
def F(w, s): return ImageFont.truetype(f"{FD}/Vazirmatn-{w}.ttf", s)
def fa(t): return get_display(arabic_reshaper.reshape(t))

W, H = 1800, 1620
bg, ink, soft, gold, navy = (246, 243, 238), (26, 33, 46), (104, 113, 127), (163, 127, 72), (5, 16, 33)
im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)

# --- سرصفحه (هر بخش جداگانه، راست‌چین) ---
d.text((W // 2, 40), fa("برد استوری — «نقشهٔ نورا»"), font=F("Bold", 52), fill=navy, anchor="ma")
d.text((W // 2, 100), fa("سمت A: شش صحنه با یک «نخ طلایی» · سمت B: قصهٔ برند و محصول"),
       font=F("Regular", 29), fill=soft, anchor="ma")
d.text((W // 2, 140), fa("تصاویر زیر پیش‌نمایش تولیدشده‌اند؛ نسخهٔ نهایی در ۳۰۰dpi و CMYK تحویل می‌شود."),
       font=F("Regular", 24), fill=gold, anchor="ma")

# --- نخ طلایی روی صحنهٔ اول (نمایش استعاره) ---
def gold_thread(img, pts, w=5, glow=26):
    base = img.convert("RGBA")
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    dd.line(pts, fill=(228, 201, 148, 235), width=w, joint="curve")
    base = Image.alpha_composite(base, ov.filter(ImageFilter.GaussianBlur(glow // 2)))
    ov2 = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov2).line(pts, fill=(238, 214, 160, 255), width=max(2, w // 2), joint="curve")
    return Image.alpha_composite(base, ov2).convert("RGB")

scenes = [("assets/nora/nora-reference.png", "۱ · فهرستِ ای‌کاش‌ها", "نورا، پیش از کتابخانه", True),
          ("assets/nora/scene-library.png", "۲ · کتابخانه", "میلیون‌ها زندگی، یک کتابِ روشن", False),
          ("assets/nora/scene-choices.png", "۳ · سه در", "کدام زندگی؟", False),
          ("assets/nora/scene-pattern.png", "۴ · تکرار", "نورا باز هم نوراست", False),
          ("assets/nora/scene-return.png", "۵ · یک پنجرهٔ روشن", "زندگی خودش", False),
          ("PLATE", "۶ · مهرِ کتابخانه", "دروازهٔ ورود — جای طراحی‌شدهٔ QR", False)]

cw, ch, cols, gx, gy = 560, 300, 3, 30, 30
x0 = (W - (cw * cols + gx * (cols - 1))) // 2
y0 = 200
for i, (p, title, cap, thread) in enumerate(scenes):
    x = x0 + (i % cols) * (cw + gx); y = y0 + (i // cols) * (ch + gy + 92)
    if p == "PLATE":
        panel = Image.new("RGB", (cw, ch), (251, 248, 243)); dp = ImageDraw.Draw(panel)
        cx, cy, R = cw // 2, ch // 2 + 6, 104
        dp.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(190, 156, 96), width=3)
        for a in range(0, 360, 12):  # قاب خط‌چین طلایی
            import math
            a1, a2 = math.radians(a), math.radians(a + 6)
            dp.line((cx + (R - 12) * math.cos(a1), cy + (R - 12) * math.sin(a1),
                     cx + (R - 12) * math.cos(a2), cy + (R - 12) * math.sin(a2)), fill=(190, 156, 96), width=2)
        s = 60
        dp.rectangle((cx - s, cy - s, cx + s, cy + s), outline=(120, 128, 140), width=2)
        dp.text((cx, cy - 6), fa("جای QR"), font=F("Bold", 26), fill=(90, 98, 112), anchor="ma")
        dp.text((cx, cy + 26), fa("تا دریافت نشانی"), font=F("Regular", 19), fill=(150, 156, 166), anchor="ma")
        dp.text((cx, cy + R + 14), fa("دروازهٔ ورود · تحلیل صوتی ۷ دقیقه‌ای"), font=F("Regular", 21), fill=gold, anchor="ma")
        im.paste(panel, (x, y))
    else:
        src = Image.open(p).convert("RGB"); r = cw / ch; w, h = src.size
        if w / h > r:
            nw = int(h * r); src = src.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w / r); src = src.crop((0, int((h - nh) * 0.25), w, int((h - nh) * 0.25) + nh))
        src = src.resize((cw, ch), Image.LANCZOS)
        if thread:  # نخ طلایی نمونه روی صحنهٔ ۱
            src = gold_thread(src, [(6, ch - 26), (170, ch - 58), (330, ch - 34), (470, ch - 66), (cw - 6, ch - 40)], w=4, glow=18)
        im.paste(src, (x, y))
    d.rectangle((x - 2, y - 2, x + cw + 2, y + ch + 2), outline=(205, 197, 185), width=2)
    d.text((x + cw, y + ch + 14), fa(title), font=F("Bold", 30), fill=navy, anchor="ra")
    d.text((x + cw, y + ch + 52), fa(cap), font=F("Regular", 25), fill=soft, anchor="ra")

# --- سمت B ---
yB = y0 + 2 * (ch + gy + 92) + 26
d.line([(60, yB - 16), (W - 60, yB - 16)], fill=(216, 209, 198), width=3)
d.text((W // 2, yB + 6), fa("سمت B — دارایی‌های واقعی برند و محصول"), font=F("Bold", 36), fill=navy, anchor="ma")
bb = [("drmirbolouki.jpg", "پرترهٔ حرفه‌ای شما (۱۲۵۴px) — منطقهٔ B1"),
      ("assets/images/drwithowl.jpg", "شما + جغد (۷۲۰px)"),
      ("assets/joma/joma-hero.png", "جوما — رابط واقعی صفحهٔ ورود"),
      ("logo.jpg", "نشان رسمی: جغد دانا / جوما")]
bw, bh = 390, 220
xb = (W - (bw * 4 + 30 * 3)) // 2
for i, (p, cap) in enumerate(bb):
    src = Image.open(p).convert("RGB"); r = bw / bh; w, h = src.size
    if w / h > r:
        nw = int(h * r); src = src.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / r); src = src.crop((0, int((h - nh) * 0.3), w, int((h - nh) * 0.3) + nh))
    src = src.resize((bw, bh), Image.LANCZOS)
    x = xb + i * (bw + 30)
    im.paste(src, (x, yB + 56))
    d.rectangle((x - 2, yB + 54, x + bw + 2, yB + 58 + bh), outline=(205, 197, 185), width=2)
    d.text((x + bw // 2, yB + 58 + bh + 10), fa(cap), font=F("Regular", 23), fill=soft, anchor="ma")

im.save("docs/03-storyboard-preview.png", quality=94)
print("storyboard:", im.size)
