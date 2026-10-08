# -*- coding: utf-8 -*-
"""SIDE B — «حالا نوبت خودت است» — paper-light face of the A5 flyer.
Same identity as Side A, inverted: cream paper, navy ink, warm gold.
Canvas 154x216mm @300dpi; coords mm from trim; MX/MY add bleed.
"""
import numpy as np
from PIL import Image
import typeset as T

# ---------------- tokens (identical to Side A) ----------------
BG_NAVY   = (9, 19, 29)
INK       = (18, 32, 44)
GOLD      = (198, 158, 94)
GOLD_HI   = (226, 190, 128)
GOLD_DEEP = (146, 110, 54)     # gold for text on paper
CREAM     = (240, 233, 220)
CREAM_DIM = (233, 226, 212)
PAPER     = (243, 238, 228)

BLEED = 3.0
W, H = T.mm(148 + 2 * BLEED), T.mm(210 + 2 * BLEED)
def MX(x): return T.mm(BLEED + x)
def MY(y): return T.mm(BLEED + y)
def LM(pt_lead): return pt_lead / 72.0 * 25.4

M_R, M_L = 134.0, 14.0
CW = M_R - M_L

f_black, f_bold = T.Font("Black"), T.Font("Bold")
f_semi, f_med   = T.Font("SemiBold"), T.Font("Medium")
f_reg, f_light  = T.Font("Regular"), T.Font("Light")

def draw_runs(canvas, runs, x_right, y):
    """runs: list of (text, font, size, color, alpha, dir) in logical RTL order."""
    x = x_right
    for text, font, size, color, alpha, d in runs:
        if d == "rtl":
            x = font.draw(canvas, text, size, x, y, color, d, alpha)
        else:
            w = font.measure(text, size, "ltr")
            x -= w
            font.draw(canvas, text, size, x, y, color, "ltr", alpha)
    return x

# ---------------- copy ----------------
TOP_ORN = True
TITLE = "حالا نوبت خودت است..."
PARA = ("شاید کتابخانه نیمه‌شب به ما یاد بدهد که زندگی فقط مجموعه‌ای از انتخاب‌های گذشته نیست. "
        "اما برای تغییر الگوهای تکرارشونده، اول باید آنها را ببینیم. "
        "به همین دلیل، یک هدیه برای تو آماده کرده‌ام.")
BOX_TITLE = "یک تست طرحواره، مهمان من"
BOX_TEXT = ("با استفاده از این تراکت می‌توانی تست طرحواره را به‌صورت رایگان در سایت من انجام بدهی "
            "و یک قدم برای شناخت الگوهای عمیق‌تر خودت برداری.")
FIELD1, FIELD2 = "نام:", "شماره موبایل:"
STEPS = [("۰۱", "تست کن", "تست طرحواره را انجام بده.", None),
         ("۰۲", "خودت را بهتر بشناس", "با الگوهای ذهنی و هیجانی خودت بیشتر آشنا شو.", None),
         ("۰۳", "تمرین دریافت کن", "بر اساس نتیجه، مسیر تمرینی مناسب را دنبال کن.", None),
         ("۰۴", "با JOMA ادامه بده", "تمرین‌ها و مسیر رشد فردی را در پلنر هوشمند روان‌شناسی JOMA دنبال کن.", "mixed")]
JOMA_TAG = "پلنر هوشمند روان‌شناسی برای تبدیل خودشناسی به تمرین و پیگیری روزانه"
QR_CAP = ["دوربین گوشی را روی این کد بگیر", "و وارد تست رایگان شو."]
QR_PLACE = "محل قرارگیری کد QR"
URL = "test.mirbolouki.com"
DR_NAME = "جواد میربلوکی"
DR_TITLE = "روانشناس | متخصص روابط | زوج‌درمانگر"
DR_T1 = "بیش از ده سال فعالیت حرفه‌ای در حوزه روان‌شناسی و روان‌درمانی"
DR_T2 = "عضو انجمن روان‌شناسی آمریکا (APA)"
DR_T3 = "شماره نظام روان‌شناسی: ۲۵۲۴۷"

S_TITLE, S_PARA = 21, 8.6
S_BOXT, S_BOXX, S_LAB = 12.5, 8.2, 8.6
S_NUM, S_STEPT, S_STEPD = 10.5, 9.6, 8.0
S_JOMA, S_TAG = 13, 8.4
S_CAP, S_URL = 9.0, 8.0
S_NAME, S_DT, S_TR, S_TR3 = 14, 8.6, 7.9, 6.9

# ---------------- layout solver ----------------
def solve(extra=None):
    e = dict(orn=13.0, title=7.4, para=4.4, box=4.6, box_t=8.2, box_x=4.4, fld=11.0,
             box_end=4.6, steps=5.0, step=8.7, joma=5.4, qr=5.0, dr=5.2,
             d1=4.6, d2=4.3, d3=3.6)
    if extra:
        e.update({k: e[k] + v for k, v in extra.items()})
    p = {}
    p['orn'] = e['orn']
    p['title'] = p['orn'] + e['title']
    n_para = len(T.wrap_lines(f_reg, PARA, T.pt(S_PARA), T.mm(CW)))
    p['n_para'] = n_para
    p['para0'] = p['title'] + e['para']
    p['para1'] = p['para0'] + (n_para - 1) * LM(S_PARA * 1.62)
    p['by0'] = p['para1'] + e['box']
    p['box_t'] = p['by0'] + e['box_t']
    n_box = len(T.wrap_lines(f_reg, BOX_TEXT, T.pt(S_BOXX), T.mm(CW - 9)))
    p['n_box'] = n_box
    p['box_x0'] = p['box_t'] + e['box_x']
    p['box_x1'] = p['box_x0'] + (n_box - 1) * LM(S_BOXX * 1.6)
    p['f1'] = p['box_x1'] + e['fld']
    p['f2'] = p['f1'] + e['fld']
    p['by1'] = p['f2'] + e['box_end']
    p['s0'] = p['by1'] + e['steps']
    p['st'] = [p['s0'] + i * e['step'] for i in range(4)]
    p['joma0'] = p['st'][-1] + LM(S_STEPD * 1.2) + e['joma']
    p['qr0'] = p['joma0'] + 21.0 + e['qr']
    p['cap0'] = p['qr0'] + 9.0
    p['cap1'] = p['cap0'] + LM(S_CAP * 1.7)
    p['drrule'] = p['cap1'] + 3.6
    p['dr0'] = p['drrule'] + 5.4
    p['dr1'] = p['dr0'] + e['d1']
    p['dr2'] = p['dr1'] + e['d2']
    p['dr2b'] = p['dr2'] + LM(S_TR * 1.55)
    p['dr3'] = p['dr2b'] + e['d3']
    p['end'] = max(p['dr3'], p['qr0'] + 30.0 + 7.0)
    p['_e'] = e
    return p

TARGET = 199.0
weights = dict(orn=0.04, title=0.06, para=0.06, box=0.08, box_t=0.04, box_x=0.05,
               fld=0.16, box_end=0.06, steps=0.08, step=0.14, joma=0.08, qr=0.06,
               dr=0.05, d1=0.02, d2=0.01, d3=0.01)
extra, p = {}, solve()
for _ in range(8):
    s = TARGET - p['end']
    if abs(s) < 0.12:
        break
    extra = {k: extra.get(k, 0) + 0.55 * s * w for k, w in weights.items()}
    p = solve(extra)
e = p['_e']
print("layoutB:", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in p.items() if k != '_e'})

# ---------------- paint ----------------
canvas = T.new_canvas(W, H, PAPER)
# paper grain + faint warm vignette
T.grain(canvas, 1.1, seed=21)
cast = np.array(PAPER, dtype=np.float64)[None, None, :]
n = T.mm(26)
al = np.linspace(0.05, 0.0, n)[None, :, None]
canvas[:, 0:n, :3] = canvas[:, 0:n, :3] * (1 - al) + np.array((226, 216, 198), np.float64)[None, None, :] * al
al = np.linspace(0.0, 0.05, n)[None, :, None]
canvas[:, W - n:W, :3] = canvas[:, W - n:W, :3] * (1 - al) + np.array((226, 216, 198), np.float64)[None, None, :] * al

# keyline frame (same as A)
t = max(1, T.mm(0.35))
T.hline(canvas, MX(6), MX(142), MY(6), GOLD_DEEP, t, 0.5)
T.hline(canvas, MX(6), MX(142), MY(204), GOLD_DEEP, t, 0.5)
T.vline(canvas, MX(6), MY(6), MY(204), GOLD_DEEP, t, 0.5)
T.vline(canvas, MX(142), MY(6), MY(204), GOLD_DEEP, t, 0.5)

# ornament (identity echo of A)
oy = MY(p['orn'])
T.hline(canvas, W / 2 - T.mm(20), W / 2 - T.mm(3), oy, GOLD_DEEP, max(1, T.mm(0.3)), 0.8)
T.hline(canvas, W / 2 + T.mm(3), W / 2 + T.mm(20), oy, GOLD_DEEP, max(1, T.mm(0.3)), 0.8)
T.diamond(canvas, W / 2, oy, T.mm(1.0), GOLD_DEEP, 0.95)

# title + paragraph
f_black.draw(canvas, TITLE, T.pt(S_TITLE), MX(M_R), MY(p['title']), INK, "rtl")
T.paragraph(canvas, f_reg, PARA, T.pt(S_PARA), INK, MX(M_R), MY(p['para0']), T.mm(CW),
            leading=T.pt(S_PARA) * 1.62, align="right", alpha=0.78)

# ---------------- gift box ----------------
by0, by1 = p['by0'], p['by1']
T.rounded_rect(canvas, MX(M_L), MY(by0), MX(M_R), MY(by1), T.mm(2.6), BG_NAVY, 1.0,
               border=max(1, T.mm(0.4)), border_color=GOLD, border_alpha=0.95)
T.rounded_rect(canvas, MX(M_L + 1.3), MY(by0 + 1.3), MX(M_R - 1.3), MY(by1 - 1.3), T.mm(1.8),
               BG_NAVY, 0.0, border=max(1, T.mm(0.25)), border_color=CREAM, border_alpha=0.3)
# tiny gift diamond before box title
T.diamond(canvas, MX(M_R - 4.6), MY(p['box_t']) - T.pt(S_BOXT) * 0.32, T.mm(0.9), GOLD_HI, 0.95)
f_bold.draw(canvas, BOX_TITLE, T.pt(S_BOXT), MX(M_R - 7.0), MY(p['box_t']), GOLD_HI, "rtl")
T.paragraph(canvas, f_reg, BOX_TEXT, T.pt(S_BOXX), CREAM_DIM, MX(M_R - 4.6), MY(p['box_x0']),
            T.mm(CW - 9.2), leading=T.pt(S_BOXX) * 1.6, align="right", alpha=0.85)
# writable fields with pen-friendly dotted leaders
def field(label, ybase):
    lw = f_med.measure(label, T.pt(S_LAB))
    xr = MX(M_R - 4.6)
    f_med.draw(canvas, label, T.pt(S_LAB), xr, MY(ybase), CREAM, "rtl", 0.95)
    x_end = MX(M_L + 4.6)
    x_start = xr - lw - T.mm(3)
    x = x_start
    r = max(1, int(T.mm(0.34)))
    while x > x_end:
        T.circle(canvas, x, MY(ybase) + T.pt(2.2), r, CREAM, 0.8)
        x -= T.mm(1.75)
field(FIELD1, p['f1'])
field(FIELD2, p['f2'])

# ---------------- steps ----------------
for i, (num, title, desc, kind) in enumerate(STEPS):
    yb = MY(p['st'][i])
    T.diamond(canvas, MX(M_R - 1.3), yb - T.pt(S_STEPT) * 0.32, T.mm(0.8), GOLD_DEEP, 0.95)
    xr = MX(M_R - 3.6)
    if kind == "mixed":
        # «با JOMA ادامه بده» : rtl + ltr + rtl runs
        r1 = "با "
        r3 = " ادامه بده"
        w1 = f_bold.measure(r1, T.pt(S_STEPT))
        wj = 0.0
        for ch in "JOMA":
            wj += f_black.measure(ch, T.pt(S_NUM)) + T.mm(0.55)
        wj -= T.mm(0.55)
        w3 = f_bold.measure(r3, T.pt(S_STEPT))
        x = xr
        x = f_bold.draw(canvas, r1, T.pt(S_STEPT), x, yb, INK, "rtl")
        xj = x - wj
        xx = xj
        for ch in "JOMA":
            f_black.draw(canvas, ch, T.pt(S_NUM), xx, yb, GOLD_DEEP, "ltr")
            xx += f_black.measure(ch, T.pt(S_NUM)) + T.mm(0.55)
        f_bold.draw(canvas, r3, T.pt(S_STEPT), xj, yb, INK, "rtl")
    else:
        wn = f_black.measure(num, T.pt(S_NUM))
        f_black.draw(canvas, num, T.pt(S_NUM), xr, yb, GOLD_DEEP, "rtl")
        f_bold.draw(canvas, title, T.pt(S_STEPT), xr - wn - T.mm(2.2), yb, INK, "rtl")
    if kind == "mixed":
        draw_runs(canvas, [("تمرین‌ها و مسیر رشد فردی را در پلنر هوشمند روان‌شناسی ", f_reg, T.pt(S_STEPD), INK, 0.7, "rtl"),
                           ("JOMA", f_reg, T.pt(S_STEPD), INK, 0.7, "ltr"),
                           (" دنبال کن.", f_reg, T.pt(S_STEPD), INK, 0.7, "rtl")],
                  MX(M_R - 3.6), yb + T.mm(4.1))
    else:
        T.paragraph(canvas, f_reg, desc, T.pt(S_STEPD), INK, MX(M_R - 3.6), yb + T.mm(4.1),
                    T.mm(CW - 3.6), leading=T.pt(S_STEPD) * 1.5, align="right", alpha=0.7)
    if i < 3:
        T.vline(canvas, MX(M_R - 1.3), yb + T.mm(1.6), MY(p['st'][i + 1]) - T.mm(2.6),
                GOLD_DEEP, max(1, T.mm(0.28)), 0.45)

# ---------------- JOMA band with owl ----------------
jy = p['joma0']
med_r = 10.0
mcx, mcy = M_R - med_r, jy + med_r - 1.0
T.circle(canvas, MX(mcx), MY(mcy), T.mm(med_r), BG_NAVY, 1.0)
T.circle(canvas, MX(mcx), MY(mcy), T.mm(med_r), BG_NAVY, 0.0, ring=max(1, T.mm(0.35)), ring_color=GOLD_DEEP)
owl = Image.open("assets/owl_joma.png")
ow = int(T.mm(med_r * 2 - 1.2))
owl = owl.resize((ow, int(ow * owl.size[1] / owl.size[0])), Image.LANCZOS)
T.paste_image(canvas, owl, MX(mcx) - owl.size[0] // 2, MY(mcy) - owl.size[1] // 2)
# wordmark JOMA (letterspaced latin) + tagline
tx_r = MX(mcx - med_r - 4.5)
xx = tx_r
for ch in "JOMA":
    wch = f_black.measure(ch, T.pt(S_JOMA))
    xx -= wch + T.mm(0.9)
xx += T.mm(0.9)
for ch in "JOMA":
    f_black.draw(canvas, ch, T.pt(S_JOMA), xx, MY(jy + 4.6), INK, "ltr")
    xx += f_black.measure(ch, T.pt(S_JOMA)) + T.mm(0.9)
T.paragraph(canvas, f_reg, JOMA_TAG, T.pt(S_TAG), INK, tx_r, MY(jy + 9.4),
            T.mm(mcx - med_r - 4.5 - M_L), leading=T.pt(S_TAG) * 1.6, align="right", alpha=0.78)

# ---------------- QR zone ----------------
qy = p['qr0']
qs = 30.0
T.fill_rect(canvas, MX(M_L), MY(qy), MX(M_L + qs), MY(qy + qs), (252, 252, 250), 1.0)
T.hline(canvas, MX(M_L), MX(M_L + qs), MY(qy), INK, max(1, T.mm(0.4)), 0.9)
T.hline(canvas, MX(M_L), MX(M_L + qs), MY(qy + qs), INK, max(1, T.mm(0.4)), 0.9)
T.vline(canvas, MX(M_L), MY(qy), MY(qy + qs), INK, max(1, T.mm(0.4)), 0.9)
T.vline(canvas, MX(M_L + qs), MY(qy), MY(qy + qs), INK, max(1, T.mm(0.4)), 0.9)
# dashed inner guide
dash = T.mm(1.6); gapd = T.mm(1.4); ins = T.mm(2.2)
x0, y0 = MX(M_L) + ins, MY(qy) + ins
x1, y1 = MX(M_L + qs) - ins, MY(qy + qs) - ins
x = x0
while x < x1:
    T.hline(canvas, x, min(x + dash, x1), y0, INK, max(1, T.mm(0.25)), 0.4)
    T.hline(canvas, x, min(x + dash, x1), y1, INK, max(1, T.mm(0.25)), 0.4)
    x += dash + gapd
y = y0
while y < y1:
    T.vline(canvas, x0, y, min(y + dash, y1), INK, max(1, T.mm(0.25)), 0.4)
    T.vline(canvas, x1, y, min(y + dash, y1), INK, max(1, T.mm(0.25)), 0.4)
    y += dash + gapd
wq1 = f_med.measure("محل قرارگیری کد ", T.pt(7.2))
wq2 = f_med.measure("QR", T.pt(7.2), "ltr")
draw_runs(canvas, [("محل قرارگیری کد ", f_med, T.pt(7.2), INK, 0.55, "rtl"),
                   ("QR", f_med, T.pt(7.2), INK, 0.55, "ltr")],
          MX(M_L + qs / 2) + (wq1 + wq2) / 2, MY(qy + qs / 2 + 1.0))
# caption right of QR
col_r = MX(M_R)
f_med.draw(canvas, QR_CAP[0], T.pt(S_CAP), col_r, MY(p['cap0']), INK, "rtl", 0.85)
f_med.draw(canvas, QR_CAP[1], T.pt(S_CAP), col_r, MY(p['cap1']), INK, "rtl", 0.85)
# url under QR (LTR, centered under square)
wu = f_med.measure(URL, T.pt(S_URL), "ltr")
f_med.draw(canvas, URL, T.pt(S_URL), MX(M_L + qs / 2) - wu / 2, MY(qy + qs + 5.0), GOLD_DEEP, "ltr")
T.hline(canvas, MX(M_L + qs / 2) - wu / 2, MX(M_L + qs / 2) + wu / 2, MY(qy + qs + 6.6), GOLD_DEEP, max(1, T.mm(0.3)), 0.7)

# ---------------- doctor / trust (right column of QR zone) ----------------
dy = p['dr0']
T.hline(canvas, MX(M_L + qs + 6), MX(M_R), MY(p['drrule']), GOLD_DEEP, max(1, T.mm(0.3)), 0.55)
f_black.draw(canvas, DR_NAME, T.pt(S_NAME), col_r, MY(dy), INK, "rtl")
f_med.draw(canvas, DR_TITLE, T.pt(S_DT), col_r, MY(p['dr1']), GOLD_DEEP, "rtl")
f_reg.draw(canvas, DR_T1, T.pt(S_TR), col_r, MY(p['dr2']), INK, "rtl", 0.75)
draw_runs(canvas, [("عضو انجمن روان‌شناسی آمریکا ", f_reg, T.pt(S_TR), INK, 0.75, "rtl"),
                   ("(APA)", f_reg, T.pt(S_TR), INK, 0.75, "ltr")], col_r, MY(p['dr2b']))
f_reg.draw(canvas, DR_T3, T.pt(S_TR3), col_r, MY(p['dr3']), INK, "rtl", 0.6)

img = Image.fromarray(T.to_uint8(canvas)[:, :, :3])
img.save("out/sideB_300dpi.png", dpi=(300, 300))
img.resize((760, int(760 * H / W)), Image.LANCZOS).save("out/sideB_preview.png")
print("rendered B", img.size, "end=", round(p['end'], 1))
