#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
«کارت کتابخانهٔ نیمه‌شب» — تولیدکنندهٔ تراکت A5 دوطرفه (پیش‌نمایش + بستهٔ چاپ)

وضعیت: **پیش‌نمایش برای تأیید شما**. این فایل‌ها «چاپ نهایی» نیستند.
جای‌های تأییدنشده صریحاً علامت‌گذاری شده‌اند:
  • QR Code  → قاب خط‌چین با برچسب «جای QR» (هیچ نشانی جعلی ساخته نمی‌شود)
  • نشان برند → از فایل JPG موجود مخزن (برای چاپ، فایل وکتور لازم است)
  • متن‌ها → پیش‌نویس؛ پس از تأیید شما تثبیت می‌شود
  • پرتره → استفاده نشده (اجازهٔ شما دریافت نشده)

اجرا:  python3 generate_card.py
خروجی: ./preview/  و  ./print/
"""

import io, math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

# ---------------------------------------------------------------- مسیرها
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FONT_DIR = os.path.join(HERE, "fonts")
LOGO_JPG = os.path.join(REPO, "logo.jpg")
OUT_PREVIEW = os.path.join(HERE, "preview")
OUT_PRINT = os.path.join(HERE, "print")
os.makedirs(OUT_PREVIEW, exist_ok=True)
os.makedirs(OUT_PRINT, exist_ok=True)

QR_URL = os.environ.get("QR_URL", "").strip()   # اگر خالی باشد، جای‌نگهدار می‌ماند
QR_BOX_MM = None

# ---------------------------------------------------------------- واحدها
DPI = 300
MM = DPI / 25.4
PAGE_W, PAGE_H = round(148 * MM), round(210 * MM)     # A5
BLEED_MM, MARGIN_MM = 3, 16
BLEED, MARGIN = round(BLEED_MM * MM), round(MARGIN_MM * MM)
CANVAS_W, CANVAS_H = PAGE_W + 2 * BLEED, PAGE_H + 2 * BLEED
CONTENT_W, CONTENT_H = PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN   # 116 × 178 mm
CONTENT_L, CONTENT_R = BLEED + MARGIN, BLEED + PAGE_W - MARGIN
CX = (CONTENT_L + CONTENT_R) // 2

def X(mm):  # مختصات افقی نسبت به لبهٔ چپ محتوا
    return CONTENT_L + round(mm * MM)
def Y(mm):  # مختصات عمودی نسبت به بالای محتوا
    return BLEED + MARGIN + round(mm * MM)

# ---------------------------------------------------------------- رنگ‌ها
NAVY        = (5, 16, 33)
NAVY_SOFT   = (12, 28, 50)
GOLD        = (200, 164, 106)
GOLD_BRIGHT = (228, 201, 148)
CREAM       = (251, 247, 241)
INK         = (26, 33, 46)
INK_SOFT    = (100, 110, 126)
PURPLE      = (124, 92, 214)
LINE_LIGHT  = (208, 201, 190)
LINE_FAINT  = (233, 228, 220)

# ---------------------------------------------------------------- فونت‌ها
def font(w, s):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"Vazirmatn-{w}.ttf"), s)
F, M, SB, B = (lambda s: font("Regular", s), lambda s: font("Medium", s),
               lambda s: font("SemiBold", s), lambda s: font("Bold", s))

# ---------------------------------------------------------------- متن
def fa(t):
    return get_display(arabic_reshaper.reshape(t))

def tw(t, fnt):
    return ImageDraw.Draw(Image.new("RGB", (4, 4))).textlength(fa(t), font=fnt)

def text(d, xy, t, fnt, fill, anchor="ra"):
    d.text(xy, fa(t), font=fnt, fill=fill, anchor=anchor)

def wrap(d, y, t, fnt, fill, max_w=None, line_ratio=1.58, anchor_mid=True):
    max_w = max_w or CONTENT_W
    lines, cur = [], ""
    for w in t.split(" "):
        trial = (cur + " " + w).strip()
        if tw(trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    lh = int(fnt.size * line_ratio)
    for i, ln in enumerate(lines):
        x = CX if anchor_mid else CONTENT_R
        d.text((x, y + i * lh), fa(ln), font=fnt, fill=fill,
               anchor="ma" if anchor_mid else "ra")
    return len(lines) * lh

def dashed_rect(d, box, color, width=3, dash=20, gap=15):
    x0, y0, x1, y1 = box
    def run(p0, p1):
        (ax, ay), (bx, by) = p0, p1
        total = math.hypot(bx - ax, by - ay)
        ux, uy = ((bx - ax) / total, (by - ay) / total) if total else (0, 0)
        p = 0
        while p < total:
            e = min(p + dash, total)
            d.line([(ax + ux * p, ay + uy * p), (ax + ux * e, ay + uy * e)], fill=color, width=width)
            p = e + gap
    run((x0, y0), (x1, y0)); run((x1, y1), (x0, y1))
    run((x0, y1), (x0, y0)); run((x1, y0), (x1, y1))

def dotted(d, x_from, x_to, y, color, dot=7, gap=11, width=3):
    x = x_from
    while x - dot >= x_to:
        d.line([(x, y), (x - dot, y)], fill=color, width=width)
        x -= dot + gap

def round_portrait(path, size, crop_box=None):
    """پرترهٔ گرد برای نوار امضا."""
    src = Image.open(path).convert("RGB")
    if crop_box:
        src = src.crop(crop_box)
    side = min(src.size)
    left = (src.width - side) // 2
    top = int((src.height - side) * 0.35)
    src = src.crop((left, top, left + side, top + side)).resize((size * 3, size * 3), Image.LANCZOS)
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).ellipse((4, 4, src.size[0] - 4, src.size[1] - 4), fill=255)
    im = Image.new("RGBA", src.size, (0, 0, 0, 0))
    im.paste(src, (0, 0), mask)
    im = im.resize((size, size), Image.LANCZOS)
    ImageDraw.Draw(im).ellipse((1, 1, size - 2, size - 2), outline=GOLD + (235,), width=max(3, size // 70))
    return im

def emblem(size, outer=GOLD, ring=True):
    src = Image.open(LOGO_JPG).convert("RGB").resize((size * 2, size * 2), Image.LANCZOS)
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).ellipse((10, 10, src.size[0] - 10, src.size[1] - 10), fill=255)
    im = Image.new("RGBA", src.size, (0, 0, 0, 0))
    im.paste(src, (0, 0), mask)
    im = im.resize((size, size), Image.LANCZOS)
    if ring:
        d, w = ImageDraw.Draw(im), max(3, size // 80)
        d.ellipse((2, 2, size - 3, size - 3), outline=outer + (240,), width=w)
    return im

def glow(img, center, radius, color, alpha=60):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(30, 0, -1):
        r = radius * i / 30
        a = int(alpha * (1 - i / 30) ** 1.6)
        d.ellipse((center[0] - r, center[1] - r, center[0] + r, center[1] + r), fill=color + (a,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 0.08)))

def vignette(img, strength=200, scale=1.0):
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.rectangle((0, 0, w, h), fill=strength)
    d.ellipse((-w * 0.30, -h * 0.35 * scale, w * 1.30, h * 1.05), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(150))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.putalpha(m)
    img.alpha_composite(layer)

# ================================================================ SIDE A
def build_side_a():
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), NAVY + (255,))
    d = ImageDraw.Draw(img)

    # کادر محتوا فقط برای کنترل کیفیت (در چاپ دیده نمی‌شود)
    y = 0

    # --- نشان
    es = round(26 * MM)
    img.alpha_composite(emblem(es), (CX - es // 2, Y(0)))
    y += 26 + 5

    # --- خط بالای عنوان
    text(d, (CX, Y(y)), "مجموعهٔ تحلیل‌های روان‌شناختی  ·  جلسهٔ ۰۱", M(30), GOLD + (240,), anchor="ma")
    y += 6 + 6

    # --- هوک (متن خودِ شما، ویرایش‌شده از نظر نیم‌فاصله)
    y += wrap(d, Y(y), "فکر می‌کنی چه چیزی در نورا", B(58), CREAM + (255,)) / MM
    y += wrap(d, Y(y), "باعث می‌شد در یک چرخهٔ معیوب", B(58), CREAM + (255,)) / MM
    y += wrap(d, Y(y), "گیر بیفتد؟", B(64), GOLD_BRIGHT + (255,)) / MM
    y += 4

    # --- کتاب
    y += wrap(d, Y(y), "کتابخانهٔ نیمه‌شب — مت هیگ", F(40), CREAM + (180,)) / MM
    y += 7

    # --- سه الگو
    chips = ["شکست", "نقص و شرم", "اطاعت"]
    cf, pad, ch, gap = M(42), round(9 * MM), round(12 * MM), round(4 * MM)
    widths = [tw(c, cf) + 2 * pad for c in chips]
    total = sum(widths) + gap * (len(chips) - 1)
    x = CX + total / 2
    for w, c in zip(widths, chips):
        d.rounded_rectangle((x - w, Y(y), x, Y(y) + ch), radius=ch // 2, outline=GOLD + (205,), width=3)
        text(d, (x - w / 2, Y(y) + ch / 2 - cf.size * 0.36), c, cf, CREAM + (250,), anchor="ma")
        x -= w + gap
    y += 12 + 3
    y += wrap(d, Y(y), "سه الگویی که نورا با خودش برد", F(36), CREAM + (140,)) / MM
    y += 6

    # --- قفسه‌ها (بصری غالب؛ کاملاً تولیدی و بدون تصویر بیرونی)
    shelf_band_top = Y(y)
    shelf_band_bottom = Y(152)
    rows, row_h = 3, (Y(152) - Y(y)) / 3
    rnd = random.Random(23)
    book_area_l, book_area_r = CONTENT_L - round(9 * MM), CONTENT_R + round(9 * MM)
    warm_spine = [(26, 46, 74), (34, 58, 88), (44, 70, 100), (30, 52, 80)]
    dim_spine  = [(16, 33, 56), (22, 42, 68), (12, 27, 47)]

    def draw_spine(x_r, w, base, h, fill, accent=None):
        d.rounded_rectangle((x_r - w, base - h, x_r, base), radius=round(0.8 * MM),
                            fill=fill + (246,))
        d.line([(x_r - w + 2, base - h + round(2 * MM)), (x_r - w + 2, base - round(2 * MM))],
               fill=(255, 255, 255, 26), width=max(2, round(0.35 * MM)))
        if accent:
            d.line([(x_r - round(1.4 * MM), base - h + round(3 * MM)),
                    (x_r - round(1.4 * MM), base - round(3 * MM))], fill=accent + (150,), width=3)

    for r in range(rows):
        top = shelf_band_top + r * row_h
        base = top + row_h - round(3.5 * MM)
        max_h = row_h - round(7 * MM)
        xb = book_area_r
        i = 0
        while xb > book_area_l:
            w = round(rnd.uniform(4.2, 9.6) * MM)
            h = max_h * rnd.uniform(0.66, 1.0)
            warm = (r == rows - 1) and rnd.random() < 0.42      # قفسهٔ پایین کمی گرم‌تر
            fill = rnd.choice(warm_spine if warm else dim_spine)
            draw_spine(xb, w, base, h, fill, accent=GOLD if (rnd.random() < 0.16) else None)
            xb -= w + round(rnd.uniform(0.4, 1.2) * MM)
            i += 1
        d.line([(book_area_l, base + 2), (book_area_r, base + 2)], fill=GOLD + (105,), width=4)
        d.line([(book_area_l, base + round(1.6 * MM)), (book_area_r, base + round(1.6 * MM))],
               fill=(0, 0, 0, 90), width=3)

    # نور گرم از سمت راست (چراغ مطالعه) + کتابِ طلایی روی قفسهٔ پایین
    base = shelf_band_top + rows * row_h - round(3.5 * MM) - (rows - 1) * row_h
    base_last = shelf_band_top + 2 * row_h + row_h - round(3.5 * MM)
    gh = (row_h - round(7 * MM))
    gx = X(70)
    glow(img, (gx, base_last - gh * 0.5), gh * 2.3, GOLD_BRIGHT, alpha=40)
    draw_spine(gx + round(2.7 * MM), round(5.4 * MM), base_last, gh, GOLD_BRIGHT)
    d.rounded_rectangle((gx - round(1.7 * MM), base_last - gh + round(2.4 * MM),
                         gx + round(1.7 * MM), base_last - round(4 * MM)),
                        radius=round(0.7 * MM), fill=NAVY + (255,))
    # ذرات نور
    for _ in range(54):
        px = int(rnd.uniform(book_area_l, book_area_r))
        py = int(rnd.uniform(shelf_band_top, shelf_band_bottom + round(6 * MM)))
        rr = rnd.uniform(1.6, 4.4)
        a = int(rnd.uniform(18, 70))
        d.ellipse((px - rr, py - rr, px + rr, py + rr), fill=GOLD_BRIGHT + (a,))
    vignette(img, 165, scale=0.9)

    # --- پایین: امضا + پرترهٔ گرد
    yb = CANVAS_H - BLEED - MARGIN
    d.line([(CX - round(24 * MM), yb - round(21 * MM)), (CX + round(24 * MM), yb - round(21 * MM))],
           fill=GOLD + (110,), width=3)
    portrait = None
    pp = os.path.join(REPO, "assets", "images", "dr1.jpg")
    if os.path.exists(pp):
        ps = round(19 * MM)
        portrait = round_portrait(pp, ps, (200, 10, 460, 300))
        img.alpha_composite(portrait, (CX - ps // 2, yb - round(42 * MM)))
    text(d, (CX, yb - round(17 * MM)), "تحلیل روان‌شناختی: جواد میربلوکی", SB(42), CREAM + (245,), anchor="ma")
    text(d, (CX, yb - round(9 * MM)), "mirbolouki.com", F(32), GOLD + (200,), anchor="ma")
    text(d, (CX, yb - round(3 * MM)), "این خوانش، تحلیل داستانی است؛ نه تشخیص روان‌شناختی.",
         F(30), CREAM + (130,), anchor="ma")
    return img

# ================================================================ SIDE B
def build_side_b():
    global QR_BOX_MM
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), CREAM + (255,))
    d = ImageDraw.Draw(img)

    # --- سرصفحه
    text(d, (CONTENT_R, Y(0)), "کارت کتابخانهٔ نیمه‌شب  ·  جلسهٔ ۰۱", M(32), INK_SOFT, anchor="ra")
    y = 5

    # --- عنوان
    d.text((CONTENT_R, Y(y)), fa("هفت شب"), font=B(78), fill=NAVY, anchor="ra")
    y += 14
    text(d, (CONTENT_R, Y(y)), "هر شب، سه چیز کوتاه: یک کار، یک حال، یک واژه.", F(36), INK + (218,), anchor="ra")
    y += 11

    # --- ستون‌ها (میلی‌متر، از لبهٔ راست محتوا)
    W_TOTAL = 116
    w_week, w_task, w_state, w_word = 11, 40, 33, 23
    gap = 3
    r_week_1 = W_TOTAL - w_week
    r_task_0, r_task_1 = r_week_1 - gap - w_task, r_week_1 - gap
    r_state_0, r_state_1 = r_task_0 - gap - w_state, r_task_0 - gap
    r_word_0, r_word_1 = r_state_0 - gap - w_word, r_state_0 - gap
    assert abs(r_word_0) < 0.5, r_word_0

    # ---------- کی‌لاین‌های ثابت (میلی‌متر) ----------
    y_head   = 39.0          # نوار سرستون
    y_rows   = 48.4          # شروع ردیف‌ها
    ROW_H    = 8.5
    y_after  = y_rows + 7 * ROW_H          # ۱۰۷٫۹
    y_pact   = y_after + 4.6               # «قرار من»
    y_night7 = y_pact + 6.2                # جملهٔ شب هفتم
    y_panel  = 128.0
    PANEL_H  = 34.0
    y_foot   = 166.0

    # نوار سرستون
    d.rounded_rectangle((X(0), Y(y_head), X(W_TOTAL), Y(y_head + 8)), radius=8, fill=(245, 241, 234))
    d.line([(X(0), Y(y_head + 8)), (X(W_TOTAL), Y(y_head + 8))], fill=LINE_LIGHT, width=3)
    hf = M(32)
    yh = y_head + 1.6
    text(d, (X((W_TOTAL - w_week + W_TOTAL) / 2), Y(yh)), "شب", hf, INK_SOFT, anchor="ma")
    text(d, (X(r_task_1), Y(yh)), "کارِ کوچکِ آن روز", hf, INK_SOFT, anchor="ra")
    text(d, (X((r_state_0 + r_state_1) / 2), Y(yh)), "حال (۱ تا ۵)", hf, INK_SOFT, anchor="ma")
    text(d, (X(r_word_0), Y(yh)), "یک واژه", hf, INK_SOFT, anchor="la")

    # ردیف‌ها
    num_f, digit = M(36), "۱۲۳۴۵۶۷"
    for i in range(7):
        ry = Y(y_rows + i * ROW_H)
        base_line = ry + round(ROW_H * MM) - round(2.4 * MM)
        text(d, (X((W_TOTAL - w_week + W_TOTAL) / 2), ry + round(2.4 * MM)), digit[i], num_f,
             GOLD if i == 6 else INK, anchor="ma")
        dotted(d, X(r_task_1), X(r_task_0) + round(2 * MM), base_line, LINE_LIGHT)
        cw = (w_state - 2) / 5
        for k in range(5):
            cx = X(r_state_1) - round((k + 0.5) * cw * MM)
            rr = round(1.5 * MM)
            d.ellipse((cx - rr, base_line - rr, cx + rr, base_line + rr), outline=LINE_LIGHT, width=3)
        dotted(d, X(r_word_1), X(r_word_0), base_line, LINE_LIGHT)
        if i < 6:
            d.line([(X(0), Y(y_rows + (i + 1) * ROW_H)), (X(W_TOTAL), Y(y_rows + (i + 1) * ROW_H))],
                   fill=LINE_FAINT, width=2)

    # یادآور شب هفتم
    text(d, (CONTENT_R, Y(y_pact)), "قرار من: شب هفتم، ساعت ........", M(34), INK + (205,), anchor="ra")
    wrap(d, Y(y_night7), "شب هفتم، هفت خط را کنار هم بگذار. کدام شب شبیه شب‌های دیگر بود؟", SB(34), NAVY)

    # --- قاب QR (جای‌نگهدار)
    d.rounded_rectangle((X(0), Y(y_panel), X(W_TOTAL), Y(y_panel + PANEL_H)), radius=16,
                        fill=(255, 255, 255), outline=LINE_LIGHT, width=3)
    qs = 26
    qx0 = X(5)
    qy0 = Y(y_panel + (PANEL_H - qs) / 2)
    qbox = (qx0, qy0, qx0 + round(qs * MM), qy0 + round(qs * MM))
    d.rounded_rectangle(qbox, radius=10, fill=(250, 249, 246), outline=(226, 221, 212), width=2)
    if not QR_URL:
        text(d, ((qbox[0] + qbox[2]) / 2, qbox[1] + round(qs * 0.44 * MM)), "جای QR",
             SB(30), (186, 180, 170), anchor="ma")
    QR_BOX_MM = (qbox[0], qbox[1], qs)
    div_x = qbox[2] + round(6 * MM)
    d.line([(div_x, Y(y_panel + 5)), (div_x, Y(y_panel + PANEL_H - 5))], fill=LINE_FAINT, width=3)
    text(d, (X(W_TOTAL - 5), Y(y_panel + 5.4)), "دروازهٔ ورود", SB(38), NAVY, anchor="ra")
    text(d, (X(W_TOTAL - 5), Y(y_panel + 12.4)), "۷ دقیقه تحلیل صوتی", F(34), INK + (215,), anchor="ra")
    text(d, (X(W_TOTAL - 5), Y(y_panel + 19.2)), "نورا، سه الگو، یک تمرین هفت‌شبه", F(29), INK_SOFT, anchor="ra")
    text(d, (X(W_TOTAL - 5), Y(y_panel + 26.2)), "از کتابخانه، تا زندگی روزمره", M(30), PURPLE + (240,), anchor="ra")

    # --- پای صفحه
    d.line([(CONTENT_L, Y(y_foot)), (CONTENT_R, Y(y_foot))], fill=LINE_LIGHT, width=3)
    em_s = round(14 * MM)
    img.alpha_composite(emblem(em_s), (CONTENT_L, Y(y_foot + 3)))
    yb = Y(y_foot + 3.4)
    text(d, (CONTENT_R, yb), "جوما — برنامه‌ریزی، اجرا، فهم", M(32), INK + (215,), anchor="ra")
    text(d, (CONTENT_R, yb + round(6.4 * MM)), "جواد میربلوکی  ·  mirbolouki.com", F(29), INK_SOFT, anchor="ra")
    text(d, (CONTENT_R, yb + round(12.4 * MM)), "این کارت ابزار خودشناسی است؛ نه تشخیص یا درمان.",
         F(27), INK_SOFT, anchor="ra")
    return img

# ================================================================ خروجی
def main():
    a, b = build_side_a(), build_side_b()
    for nm, im in (("side-a", a), ("side-b", b)):
        im.convert("RGB").resize((PAGE_W // 2, PAGE_H // 2), Image.LANCZOS).save(
            os.path.join(OUT_PREVIEW, f"{nm}.png"))
        rgb = im.convert("RGB")
        rgb.save(os.path.join(OUT_PRINT, f"{nm}-300dpi.png"), dpi=(DPI, DPI))
        rgb.convert("CMYK").save(os.path.join(OUT_PRINT, f"{nm}-cmyk.tif"),
                                 dpi=(DPI, DPI), compression="tiff_lzw")
        buf = io.BytesIO(); rgb.save(buf, format="PNG")
        try:
            import img2pdf
            with open(os.path.join(OUT_PRINT, f"{nm}.pdf"), "wb") as f:
                f.write(img2pdf.convert(buf.getvalue()))
        except Exception as e:
            print("PDF skipped:", e)

    # مختصات جای QR برای اسکریپت افزودن QR
    import json
    if QR_BOX_MM:
        json.dump({"x_px": QR_BOX_MM[0], "y_px": QR_BOX_MM[1], "size_px": round(QR_BOX_MM[2] * MM),
                   "dpi": DPI, "mm": QR_BOX_MM[2]},
                  open(os.path.join(OUT_PRINT, "qr-box.json"), "w"))

    pair = Image.new("RGB", (PAGE_W, PAGE_H // 2 + 30), (233, 229, 222))
    pair.paste(Image.open(os.path.join(OUT_PREVIEW, "side-a.png")), (0, 15))
    pair.paste(Image.open(os.path.join(OUT_PREVIEW, "side-b.png")), (PAGE_W // 2, 15))
    pair.save(os.path.join(OUT_PREVIEW, "preview-both.png"))
    print("preview →", OUT_PREVIEW, "\nprint   →", OUT_PRINT)

if __name__ == "__main__":
    main()
