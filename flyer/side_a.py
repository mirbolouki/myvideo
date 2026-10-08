# -*- coding: utf-8 -*-
"""SIDE A — «کتابخانه نیمه‌شب» — dark cinematic face of the A5 flyer.
Canvas: 154 x 216 mm (A5 148x210 + 3mm bleed) @ 300 DPI = 1819 x 2551 px.
Two-pass layout: positions solved from gap weights, slack auto-distributed,
then painted. Coordinates in mm from TRIM edge; MX/MY add bleed offset.
"""
import numpy as np
from PIL import Image
import typeset as T

# ---------------- design tokens (shared identity A+B) ----------------
BG_NAVY   = (9, 19, 29)
INK       = (16, 30, 42)
GOLD      = (198, 158, 94)
GOLD_HI   = (226, 190, 128)
CREAM     = (240, 233, 220)
CREAM_DIM = (233, 226, 212)
PAPER     = (243, 238, 228)

BLEED = 3.0
W, H = T.mm(148 + 2 * BLEED), T.mm(210 + 2 * BLEED)
def MX(x): return T.mm(BLEED + x)
def MY(y): return T.mm(BLEED + y)
def LM(leading_pt): return leading_pt / 72.0 * 25.4   # pt leading -> mm

M_R, M_L = 134.0, 14.0
CW = M_R - M_L

f_black, f_bold = T.Font("Black"), T.Font("Bold")
f_semi, f_med   = T.Font("SemiBold"), T.Font("Medium")
f_reg, f_light  = T.Font("Regular"), T.Font("Light")

# ---------------- copy ----------------
TITLE = "کتابخانه نیمه‌شب"
DECK  = "اگر می‌توانستی یک زندگی دیگر را انتخاب کنی، کدام را انتخاب می‌کردی؟"
SUB   = ["تحلیل روان‌شناختی انتخاب‌ها، حسرت‌ها و الگوهایی که گاهی",
         "بی‌آنکه بفهمیم، زندگی ما را هدایت می‌کنند."]
QUOTE = ["گاهی مشکل ما این نیست که انتخاب اشتباهی کرده‌ایم...",
         "مشکل این است که سال‌ها بعد، هنوز داریم خودمان را بابت آن انتخاب قضاوت می‌کنیم."]
NORA_H = "شاید تو هم نورا را بشناسی..."
NORA_I = "اگر بارها با خودت گفته‌ای:"
IFS = ["اگر آن روز جور دیگری تصمیم می‌گرفتم...",
       "اگر این رابطه را انتخاب نمی‌کردم...",
       "اگر زودتر شروع می‌کردم...",
       "اگر شکست نمی‌خوردم...",
       "اگر دیگران بیشتر من را می‌فهمیدند..."]
FAM = "احتمالاً بخشی از این داستان برایت آشناست."
SCH_H = "سه طرحواره که می‌توان ردپایشان را در زندگی نورا دید"
CARDS = [("شکست", "آن‌قدر به خودم شک دارم که موفقیت‌های خودم را هم جدی نمی‌گیرم."),
         ("معیارهای سخت‌گیرانه", "همیشه فکر می‌کنم باید بیشتر، بهتر و کامل‌تر باشم تا بالاخره از خودم راضی شوم."),
         ("منفی‌گرایی / بدبینی", "ذهنم بیشتر از اینکه ببیند چه چیزهایی می‌تواند خوب پیش برود، دنبال این است که چه چیزی ممکن است خراب شود.")]
CLOSING = ("در این ایونت، نورا را فقط به‌عنوان یک شخصیت داستانی نمی‌بینیم؛ با هم بررسی می‌کنیم پشت انتخاب‌ها، "
           "حسرت‌ها و واکنش‌های او چه الگوهای روان‌شناختی‌ای قرار گرفته‌اند... و مهم‌تر از آن:")
GOLD_LINE = "کدام بخش این داستان ممکن است درباره خود ما باشد؟"
FOOT_R = "۱۶ مهر، ساعت ۱۸:۰۰  |  تسهیل‌گر: دکتر جواد میربلوکی"
FOOT_L = "ادامهٔ این مسیر، در پشت همین صفحه است"

# type sizes (pt)
S_MICRO, S_TITLE, S_DECK, S_SUB = 7.2, 33, 11.5, 8.3
S_QUOTE, S_NORAH, S_NORAI, S_IF, S_FAM, S_SCHH = 9.8, 12, 8.3, 9.0, 9.3, 11
S_CNAME, S_CQUOTE, S_CLOSE, S_GOLD, S_FOOT = 9.3, 7.2, 8.1, 8.8, 6.9

CARD_GAP, CARD_PAD = 4.0, 3.4
COLW = (CW - 2 * CARD_GAP) / 3.0

def card_quote_lines(quote):
    return T.wrap_lines(f_reg, quote, T.pt(S_CQUOTE), T.mm(COLW - 2 * CARD_PAD))

def solve(extra=None):
    """Return dict of y positions (mm). extra: dict gap->added mm."""
    e = dict(quote_step=4.55, orn=3.6, nora=5.4, intro=4.9, ifs_step=4.35,
             fam=3.8, sch=5.2, cards=2.6, card_ch=25.6, close=3.6,
             close_lead=LM(S_CLOSE * 1.62), gold=1.6, rule=2.9, foot=3.2)
    if extra:
        e.update({k: e[k] + v for k, v in extra.items()})
    p = {}
    p['title'] = 67.6
    p['deck'] = p['title'] + LM(S_TITLE * 0.30) + LM(S_DECK * 1.5)
    p['sub0'] = p['deck'] + LM(S_DECK * 0.42) + LM(S_SUB * 1.55)
    p['sub1'] = p['sub0'] + LM(S_SUB * 1.55)
    p['q0'] = p['sub1'] + LM(S_SUB * 0.55) + LM(S_QUOTE * 1.5)
    p['q1'] = p['q0'] + e['quote_step']
    p['orn'] = p['q1'] + e['orn']
    p['nora'] = p['orn'] + e['nora']
    p['intro'] = p['nora'] + e['intro']
    p['ifs'] = [p['intro'] + LM(S_NORAI * 0.9) + e['ifs_step'] * (i + 1) for i in range(5)]
    p['fam'] = p['ifs'][-1] + e['fam']
    p['sch'] = p['fam'] + e['sch']
    p['cy0'] = p['sch'] + e['cards']
    p['cy1'] = p['cy0'] + e['card_ch']
    p['cl0'] = p['cy1'] + e['close']
    n_cl = len(T.wrap_lines(f_reg, CLOSING, T.pt(S_CLOSE), T.mm(CW)))
    p['n_cl'] = n_cl
    p['gold'] = p['cl0'] + (n_cl - 1) * e['close_lead'] + e['close_lead'] * 0.35 + e['gold'] + LM(S_CLOSE)
    p['rule'] = p['gold'] + e['rule']
    p['foot'] = p['rule'] + e['foot']
    p['_e'] = e
    return p

TARGET_FOOT = 200.4
weights = dict(quote_step=0.08, orn=0.10, nora=0.10, intro=0.05, ifs_step=0.032,
               fam=0.08, sch=0.08, cards=0.05, card_ch=0.14, close=0.06, gold=0.04,
               rule=0.03, foot=0.03)
extra = {}
p = solve()
for _ in range(8):
    s = TARGET_FOOT - p['foot']
    if abs(s) < 0.12:
        break
    extra = {k: extra.get(k, 0) + 0.55 * s * w for k, w in weights.items()}
    p = solve(extra)
e = p['_e']
print("layout:", {k: (round(v, 1) if isinstance(v, float) else
                      ([round(x, 1) for x in v] if isinstance(v, list) else v))
                  for k, v in p.items() if k != '_e'})

# ================= paint =================
canvas = T.new_canvas(W, H, BG_NAVY)

# ---- artwork ----
art = Image.open("assets/art_library_night.png").convert("RGB")
aw, ah = art.size
cr = int(min(aw, ah) * 0.03)
art = art.crop((cr, cr, aw - cr, ah - cr))
aw, ah = art.size
new_h = int(ah * (W / aw))
art = art.resize((W, new_h), Image.LANCZOS)
focal_px = int(new_h * 0.30)
y_off = MY(0) + T.mm(38.0) - focal_px
arr = np.asarray(art, dtype=np.float64)
y0, y1 = max(0, y_off), min(H, y_off + new_h)
canvas[y0:y1, :, :3] = arr[y0 - y_off:y1 - y_off, :, :3]
canvas[:, :, 3] = 255
canvas[:, :, :3] *= 0.92
cast = np.array(BG_NAVY, dtype=np.float64)[None, None, :]
canvas[:, :, :3] = canvas[:, :, :3] * 0.82 + cast * 0.18
n = T.mm(26)
yA, yB = MY(48), MY(48) + n
al = np.linspace(0.0, 1.0, yB - yA)[:, None, None] ** 1.35
canvas[yA:yB, :, :3] = canvas[yA:yB, :, :3] * (1 - al) + cast * al
n = T.mm(14)
al = np.linspace(0.55, 0.0, n)[:, None, None]
canvas[0:n, :, :3] = canvas[0:n, :, :3] * (1 - al) + cast * al
n = T.mm(20)
al = np.linspace(0.30, 0.0, n)[None, :, None]
canvas[:, 0:n, :3] = canvas[:, 0:n, :3] * (1 - al) + cast * al
al = np.linspace(0.0, 0.30, n)[None, :, None]
canvas[:, W - n:W, :3] = canvas[:, W - n:W, :3] * (1 - al) + cast * al

# ---- keyline frame ----
t = max(1, T.mm(0.35))
T.hline(canvas, MX(6), MX(142), MY(6), GOLD, t, 0.42)
T.hline(canvas, MX(6), MX(142), MY(204), GOLD, t, 0.42)
T.vline(canvas, MX(6), MY(6), MY(204), GOLD, t, 0.42)
T.vline(canvas, MX(142), MY(6), MY(204), GOLD, t, 0.42)

# ---- micro label ----
lab = "نشست تحلیل روان‌شناختی کتاب"
lsz = T.pt(S_MICRO)
lw = f_med.measure(lab, lsz)
cx = W / 2.0
f_med.draw(canvas, lab, lsz, cx + lw / 2, MY(13.6), GOLD_HI, "rtl", 0.95)
ry = MY(13.6) - lsz * 0.32
T.hline(canvas, cx - lw / 2 - T.mm(16), cx - lw / 2 - T.mm(4), ry, GOLD, max(1, T.mm(0.3)), 0.75)
T.hline(canvas, cx + lw / 2 + T.mm(4), cx + lw / 2 + T.mm(16), ry, GOLD, max(1, T.mm(0.3)), 0.75)
T.diamond(canvas, cx - lw / 2 - T.mm(17.4), ry, T.mm(0.7), GOLD, 0.85)
T.diamond(canvas, cx + lw / 2 + T.mm(17.4), ry, T.mm(0.7), GOLD, 0.85)

# ---- hero ----
def centered(font, lines, size, y_mm, color, alpha=1.0, lead_mm=None):
    if isinstance(lines, str):
        lines = [lines]
    lm = lead_mm or (size / T.PX_PER_PT * 1.55 / 72.0 * 25.4)
    y = y_mm
    for ln in lines:
        w = font.measure(ln, size)
        font.draw(canvas, ln, size, W / 2.0 + w / 2.0, MY(y), color, "rtl", alpha)
        y += lm
    return y

centered(f_black, TITLE, T.pt(S_TITLE), p['title'], CREAM)
centered(f_med, DECK, T.pt(S_DECK), p['deck'], GOLD_HI)
centered(f_reg, SUB, T.pt(S_SUB), p['sub0'], CREAM, 0.74)

# ---- pull quote ----
for i, ln in enumerate(QUOTE):
    w = f_light.measure(ln, T.pt(S_QUOTE))
    f_light.draw(canvas, ln, T.pt(S_QUOTE), W / 2.0 + w / 2.0, MY(p['q0'] + i * e['quote_step']), CREAM, "rtl", 0.92)
qw = max(f_light.measure(l, T.pt(S_QUOTE)) for l in QUOTE)
T.vline(canvas, W / 2 - qw / 2 - T.mm(4), MY(p['q0'] - 3.0), MY(p['q1'] - 1.4), GOLD, max(1, T.mm(0.3)), 0.5)
T.vline(canvas, W / 2 + qw / 2 + T.mm(4), MY(p['q0'] - 3.0), MY(p['q1'] - 1.4), GOLD, max(1, T.mm(0.3)), 0.5)

# ---- ornament ----
oy = MY(p['orn'])
T.hline(canvas, W / 2 - T.mm(20), W / 2 - T.mm(3), oy, GOLD, max(1, T.mm(0.3)), 0.7)
T.hline(canvas, W / 2 + T.mm(3), W / 2 + T.mm(20), oy, GOLD, max(1, T.mm(0.3)), 0.7)
T.diamond(canvas, W / 2, oy, T.mm(1.0), GOLD_HI, 0.95)

# ---- nora ----
f_bold.draw(canvas, NORA_H, T.pt(S_NORAH), MX(M_R), MY(p['nora']), CREAM, "rtl")
f_reg.draw(canvas, NORA_I, T.pt(S_NORAI), MX(M_R), MY(p['intro']), CREAM, "rtl", 0.72)
for i, s in enumerate(IFS):
    yy = MY(p['ifs'][i])
    f_med.draw(canvas, s, T.pt(S_IF), MX(M_R - 3.2), yy, CREAM_DIM, "rtl", 0.9)
    T.diamond(canvas, MX(M_R - 1.4), yy - T.pt(S_IF) * 0.30, T.mm(0.75), GOLD, 0.9)
f_semi.draw(canvas, FAM, T.pt(S_FAM), MX(M_R), MY(p['fam']), GOLD_HI, "rtl")

# ---- schema cards (RTL order) ----
f_bold.draw(canvas, SCH_H, T.pt(S_SCHH), MX(M_R), MY(p['sch']), CREAM, "rtl")
cy0, ch = p['cy0'], p['cy1'] - p['cy0']
for i, (name, quote) in enumerate(CARDS):
    x1 = M_L + (2 - i) * (COLW + CARD_GAP)
    x0 = x1 + COLW
    T.rounded_rect(canvas, MX(x1), MY(cy0), MX(x0), MY(cy0 + ch), T.mm(2.0),
                   CREAM, 0.05, border=max(1, T.mm(0.28)), border_color=GOLD, border_alpha=0.5)
    T.hline(canvas, MX(x1 + CARD_PAD), MX(x0 - CARD_PAD), MY(cy0 + 3.0), GOLD, max(1, T.mm(0.3)), 0.55)
    f_bold.draw(canvas, name, T.pt(S_CNAME), MX(x0 - CARD_PAD), MY(cy0 + 7.4), GOLD_HI, "rtl")
    T.paragraph(canvas, f_reg, quote, T.pt(S_CQUOTE), CREAM_DIM, MX(x0 - CARD_PAD), MY(cy0 + 9.6),
                T.mm(COLW - 2 * CARD_PAD), leading=T.pt(S_CQUOTE) * 1.6, align="right", alpha=0.8)

# ---- closing ----
T.paragraph(canvas, f_reg, CLOSING, T.pt(S_CLOSE), CREAM, MX(M_R), MY(p['cl0']), T.mm(CW),
            leading=T.pt(S_CLOSE) * 1.62, align="right", alpha=0.85)
f_med.draw(canvas, GOLD_LINE, T.pt(S_GOLD), MX(M_R), MY(p['gold']), GOLD_HI, "rtl")

# ---- footer ----
T.hline(canvas, MX(M_L), MX(M_R), MY(p['rule']), GOLD, max(1, T.mm(0.3)), 0.5)
f_reg.draw(canvas, FOOT_R, T.pt(S_FOOT), MX(M_R), MY(p['foot']), CREAM, "rtl", 0.66)
fw = f_med.measure(FOOT_L, T.pt(S_FOOT))
f_med.draw(canvas, FOOT_L, T.pt(S_FOOT), MX(M_L) + fw, MY(p['foot']), GOLD_HI, "rtl", 0.85)

T.grain(canvas, 1.6, seed=11)
img = Image.fromarray(T.to_uint8(canvas)[:, :, :3])
img.save("out/sideA_300dpi.png", dpi=(300, 300))
img.resize((760, int(760 * H / W)), Image.LANCZOS).save("out/sideA_preview.png")
print("rendered", img.size, "foot=", round(p['foot'], 1))
