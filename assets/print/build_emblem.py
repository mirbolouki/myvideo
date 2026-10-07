#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ساخت «نشان سادهٔ چاپ‌پذیر» از فایل JPG موجود.

چرا؟ نشان فعلی، متنی ریز روی رینگ دارد که در قطر ۲۶ میلی‌متر ناخوانا و
لکه‌مانند چاپ می‌شود. این نسخه: فقط جغد + حلقهٔ طلایی + زمینهٔ سرمه‌ای.
خروجی برای بازبینی شماست؛ تا تأیید نکنید در کارت استفاده نمی‌شود.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(REPO, "logo.jpg")
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)

NAVY = (5, 16, 33)
GOLD = (200, 164, 106)

def build(size=1200):
    src = Image.open(SRC).convert("RGB")
    # جغد در مرکز تصویر است؛ برش مربعی اطراف آن (بدون متن رینگ)
    w, h = src.size
    side = int(min(w, h) * 0.74)
    left = (w - side) // 2
    top = int((h - side) * 0.36)
    owl = src.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)

    # ماسک دایره‌ای + زمینهٔ سرمه‌ای
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)

    canvas = Image.new("RGB", (size, size), NAVY)
    canvas.paste(owl, (0, 0), mask)

    # حلقهٔ طلایی (دو خط)
    d = ImageDraw.Draw(canvas)
    w1 = max(6, size // 62)
    d.ellipse((w1, w1, size - w1, size - w1), outline=GOLD, width=w1)
    d.ellipse((int(w1 * 2.1), int(w1 * 2.1), size - int(w1 * 2.1), size - int(w1 * 2.1)),
              outline=(GOLD[0], GOLD[1], GOLD[2], 255), width=max(2, w1 // 3))
    canvas.save(os.path.join(OUT, "emblem-simple.png"), dpi=(300, 300))
    canvas.resize((size // 2, size // 2), Image.LANCZOS).save(os.path.join(OUT, "emblem-simple-preview.png"))
    print("→", os.path.join(OUT, "emblem-simple.png"), canvas.size)

if __name__ == "__main__":
    build()
