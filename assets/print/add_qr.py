#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
افزودن QR واقعی به کارت چاپی — «یک فرمان تا فایل نهایی»

پیش‌نیاز: ابتدا generate_card.py اجرا شده باشد (تا `print/qr-box.json` ساخته شود).

نمونهٔ اجرا:
    python3 add_qr.py --url "https://<نشانی مورد تأیید شما>"
    python3 add_qr.py --url "https://<...>" --label "mirbolouki.com/midnight"

خروجی (در پوشهٔ print/):
    side-b-final-300dpi.png      (RGB، چاپ دیجیتال)
    side-b-final.pdf             (اندازهٔ واقعی A5 + بلید)
    side-b-final-cmyk.tif        (CMYK برای چاپخانه)

نکات فنی اعمال‌شده:
    • سطح تصحیح خطا: Q (۲۵٪) — مقاوم در برابر خش و بازتاب نور
    • حاشیهٔ سکوت ۴ ماژول، سفید
    • رنگ: مشکی روی سفید (هرگز معکوس)
    • اندازه: مطابق اندازهٔ دقیق جای QR روی کارت (۲۶ میلی‌متر)
    • برچسب اختیاری زیر QR (نشانی خوانا برای کسانی که اسکن نمی‌کنند)
"""

import argparse, io, json, os, sys
from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.constants import ERROR_CORRECT_Q
import arabic_reshaper
from bidi.algorithm import get_display

HERE = os.path.dirname(os.path.abspath(__file__))
PRINT = os.path.join(HERE, "print")
FONTS = os.path.join(HERE, "fonts")
DPI = 300
MM = DPI / 25.4

def fa(t):
    return get_display(arabic_reshaper.reshape(t))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="نشانی نهایی که باید داخل QR برود")
    ap.add_argument("--label", default="", help="برچسب خوانا زیر QR (اختیاری)")
    args = ap.parse_args()

    side_b = os.path.join(PRINT, "side-b-300dpi.png")
    box_f = os.path.join(PRINT, "qr-box.json")
    if not os.path.exists(side_b) or not os.path.exists(box_f):
        sys.exit("ابتدا generate_card.py را اجرا کنید.")

    box = json.load(open(box_f))
    x, y, size = box["x_px"], box["y_px"], box["size_px"]

    # --- تولید QR
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, border=4, box_size=10)
    qr.add_data(args.url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    canvas = Image.open(side_b).convert("RGB")

    # اگر برچسب خوانا لازم است، کمی از پایین قاب را آزاد می‌کنیم
    if args.label:
        pad_bottom = round(4.2 * MM)
        target = Image.new("RGB", (size, size + pad_bottom), "white")
        target.paste(img_qr.resize((size, size), Image.LANCZOS), (0, 0))
        d = ImageDraw.Draw(target)
        f = ImageFont.truetype(os.path.join(FONTS, "Vazirmatn-Medium.ttf"), 30)
        d.text((size // 2, size + round(1.4 * MM)), args.label, font=f,
               fill=(92, 100, 114), anchor="ma")
        canvas.paste(target, (x, y))
    else:
        canvas.paste(img_qr.resize((size, size), Image.LANCZOS), (x, y))

    out_png = os.path.join(PRINT, "side-b-final-300dpi.png")
    canvas.save(out_png, dpi=(DPI, DPI))
    canvas.convert("CMYK").save(os.path.join(PRINT, "side-b-final-cmyk.tif"),
                                dpi=(DPI, DPI), compression="tiff_lzw")
    buf = io.BytesIO(); canvas.save(buf, format="PNG")
    try:
        import img2pdf
        with open(os.path.join(PRINT, "side-b-final.pdf"), "wb") as f:
            f.write(img2pdf.convert(buf.getvalue()))
    except Exception as e:
        print("PDF skipped:", e)

    info = qr.version, len(qr.modules), qr.modules_count if hasattr(qr, "modules_count") else len(qr.modules)
    print(f"QR ساخته شد → نسخهٔ {qr.version}، سطح خطا Q، اندازهٔ {box['mm']:.0f} میلی‌متر")
    print("خروجی‌ها: side-b-final-300dpi.png / .pdf / -cmyk.tif")

if __name__ == "__main__":
    main()
