# -*- coding: utf-8 -*-
"""Imposition guide sheets (A4, screen-RGB — NOT a press file):
each press page centered on A4 with crop marks at trim corners + job ticket.
Also prints the exact QR swap-in rectangle (px @300dpi, bleed-based)."""
import numpy as np
from PIL import Image
import typeset as T

MM = T.PX_PER_MM
A4W, A4H = int(round(210 * MM)), int(round(297 * MM))   # 2480 x 3508
INK = (30, 30, 32)
f_b, f_m, f_r = T.Font("Bold"), T.Font("Medium"), T.Font("Regular")

def draw_runs(c, runs, x_right, y):
    x = x_right
    for text, font, size, color, alpha, d in runs:
        if d == "rtl":
            x = font.draw(c, text, size, x, y, color, d, alpha)
        else:
            w = font.measure(text, size, "ltr")
            x -= w
            font.draw(c, text, size, x, y, color, "ltr", alpha)
    return x

sheets = []
for side, label in [("sideA", "روی A"), ("sideB", "روی B")]:
    art = Image.open(f"out/{side}_300dpi.png").convert("RGB")
    c = T.new_canvas(A4W, A4H, (250, 250, 249))
    ox, oy = (A4W - art.width) // 2, (A4H - art.height) // 2
    T.paste_image(c, art.convert("RGBA"), ox, oy)
    # trim rect in sheet coords
    tx0, ty0 = ox + int(3 * MM), oy + int(3 * MM)
    tx1, ty1 = ox + art.width - int(3 * MM), oy + art.height - int(3 * MM)
    L, gap = int(8 * MM), int(1.2 * MM)
    tk = max(1, int(0.3 * MM))
    for (cx, cy, sx, sy) in [(tx0, ty0, -1, -1), (tx1, ty0, 1, -1),
                             (tx0, ty1, -1, 1), (tx1, ty1, 1, 1)]:
        x_out = cx + sx * (int(3 * MM) + gap)
        T.hline(c, min(x_out, x_out + sx * L), max(x_out, x_out + sx * L), cy, INK, tk, 0.9)
        y_out = cy + sy * (int(3 * MM) + gap)
        T.vline(c, cx, min(y_out, y_out + sy * L), max(y_out, y_out + sy * L), INK, tk, 0.9)
    # labels + job ticket
    f_b.draw(c, label, T.pt(13), tx1, ty1 + int(14 * MM), INK, "rtl")
    ty = ty1 + int(22 * MM)
    draw_runs(c, [("تراکت A5 دورو — تحلیل روان‌شناختی کتابِ کتابخانه نیمه‌شب", f_b, T.pt(11), INK, 1, "rtl")],
              A4W - int(20 * MM), ty)
    tick = "Trim: 148×210 mm   |   Bleed: 3 mm   |   300 DPI   |   CMYK: ISO Coated v2 (FOGRA39)   |   TAC ≤ 300%"
    wt = f_m.measure(tick, T.pt(9), "ltr")
    f_m.draw(c, tick, T.pt(9), A4W - int(20 * MM) - wt, ty + int(6 * MM), INK, "ltr", 0.8)
    draw_runs(c, [("فایل چاپ: ", f_r, T.pt(8.5), INK, .7, "rtl"),
                  ("midnight_library_A5_flyer_press.pdf", f_r, T.pt(8.5), INK, .7, "ltr"),
                  ("  —  این برگه فقط راهنمای برش/کنترل است، فایل چاپ نیست.", f_r, T.pt(8.5), INK, .7, "rtl")],
              A4W - int(20 * MM), ty + int(11.5 * MM))
    img = Image.fromarray(T.to_uint8(c)[:, :, :3])
    sheets.append(img)
    img.resize((A4W // 3, A4H // 3), Image.LANCZOS).save(f"out/press/imposition_{side}.png")

sheets[0].save("out/press/imposition_A4_guide.pdf", resolution=300.0, save_all=True,
               append_images=sheets[1:], title="Midnight Library A5 Flyer - Imposition Guide",
               author="JOMA Studio", producer="Arena print pipeline")
print("imposition sheets done")

# QR swap-in rectangle (bleed-based px @300dpi) for side B
import io, re
src = io.open("side_b.py", encoding="utf-8").read()
m = re.search(r"p\['qr0'\] = p\['joma0'\] \+ 21\.0 \+ e\['qr'\]", src)
lay = {}
exec(compile(io.open("side_b.py", encoding="utf-8").read().split("# ---------------- paint")[0], "side_b", "exec"), lay)
q = lay["p"]["qr0"]
x0 = int(round((14 + 3) * MM)); y0 = int(round((q + 3) * MM)); s = int(round(30 * MM))
print(f"QR swap-in rect on sideB_300dpi.png: x={x0}..{x0+s}, y={y0}..{y0+s}  ({s}px = 30mm)")
io.open("out/press/QR_SWAP_IN.txt", "w", encoding="utf-8").write(
    f"sideB_300dpi.png / sideB page of press PDF:\nQR rectangle (bleed-based px @300dpi): "
    f"x {x0}..{x0+s}, y {y0}..{y0+s}  ({s}x{s}px = 30x30mm)\n"
    f"mm from trim: x 14..44, y {q:.1f}..{q+30:.1f}\n")
print("QR spec written")
