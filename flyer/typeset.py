# -*- coding: utf-8 -*-
"""
Minimal professional Persian typesetting engine for print.
HarfBuzz (complex shaping, liga/calt/kern) + FreeType (glyph rasterization),
manual bidi-safe run layout (runs are authored explicitly), ZWNJ-aware wrapping.
All units: pixels at the target DPI (mm/pt helpers provided).
"""
import functools
import numpy as np
import freetype as ft
import uharfbuzz as hb

DPI = 300.0
PX_PER_MM = DPI / 25.4
PX_PER_PT = DPI / 72.0

def mm(v):  return int(round(v * PX_PER_MM))
def pt(v):  return v * PX_PER_PT          # float px
def fmm(v): return v * PX_PER_MM          # float px

FONT_DIR = "/home/user/tools/fonts/ttf/"

class Font:
    _cache = {}
    def __init__(self, weight="Regular"):
        key = weight
        if key in Font._cache:
            self.__dict__.update(Font._cache[key].__dict__); return
        path = FONT_DIR + "Vazirmatn-%s.ttf" % weight
        self.path = path
        self.face = ft.Face(path)
        with open(path, "rb") as fh:
            self.hbface = hb.Face(fh.read())
        self.hbfont = hb.Font(self.hbface)
        self.upem = self.face.units_per_EM
        Font._cache[key] = self

    def _set_size(self, size_px):
        self.face.set_char_size(int(round(size_px * 64)), 0, 72, 72)
        self.hbfont.scale = (int(round(size_px * 64)), int(round(size_px * 64)))

    def metrics(self, size_px):
        self._set_size(size_px)
        asc = self.face.size.ascender / 64.0
        desc = self.face.size.descender / 64.0   # negative
        h = self.face.size.height / 64.0
        return asc, desc, h

    @functools.lru_cache(maxsize=None)
    def _glyph_bitmap(self, gid, size_key):
        size_px = size_key
        self._set_size(size_px)
        self.face.load_glyph(gid, ft.FT_LOAD_RENDER | ft.FT_LOAD_NO_HINTING)
        slot = self.face.glyph
        bmp = slot.bitmap
        w, rows = bmp.width, bmp.rows
        if w == 0 or rows == 0:
            return None, 0, 0
        buf = np.array(bmp.buffer, dtype=np.uint8).reshape(rows, bmp.pitch)[:, :w].copy()
        return buf, slot.bitmap_left, slot.bitmap_top

    def shape(self, text, size_px, direction="rtl"):
        self._set_size(size_px)
        buf = hb.Buffer()
        buf.add_str(text)
        buf.direction = "RTL" if direction == "rtl" else "LTR"
        buf.script = "arab" if direction == "rtl" else "latn"
        buf.language = "fa" if direction == "rtl" else "en"
        hb.shape(self.hbfont, buf, {"liga": True, "clig": True, "calt": True,
                                    "kern": True, "rlig": True})
        infos = buf.glyph_infos
        pos = buf.glyph_positions
        s = 1.0 / 64.0
        glyphs = []
        adv = 0.0
        for i, g in enumerate(infos):
            glyphs.append((g.codepoint, pos[i].x_advance * s, pos[i].x_offset * s, pos[i].y_offset * s))
            adv += pos[i].x_advance * s
        return glyphs, adv

    def measure(self, text, size_px, direction="rtl"):
        return self.shape(text, size_px, direction)[1]

    def draw(self, canvas, text, size_px, x_pen, y_baseline, color, direction="rtl", alpha=1.0):
        """Draw one run. x_pen = RIGHT edge for rtl, LEFT edge for ltr.
        Returns the opposite edge x (left for rtl, right for ltr)."""
        glyphs, adv = self.shape(text, size_px, direction)
        col = np.array(color[:3], dtype=np.float64)
        size_key = round(size_px, 3)
        if direction == "rtl":
            x = x_pen - adv
            for gid, xadv, xoff, yoff in glyphs:
                self._blit(canvas, gid, size_key, x + xoff, y_baseline + yoff, col, alpha)
                x += xadv
            return x_pen - adv
        else:
            x = x_pen
            for gid, xadv, xoff, yoff in glyphs:
                self._blit(canvas, gid, size_key, x + xoff, y_baseline + yoff, col, alpha)
                x += xadv
            return x_pen + adv

    def _blit(self, canvas, gid, size_key, gx, y_baseline, col, alpha):
        bmp, bl, bt = self._glyph_bitmap(gid, size_key)
        if bmp is None:
            return
        x0 = int(round(gx)) + bl
        y0 = int(round(y_baseline)) - bt
        h, w = bmp.shape
        H, W = canvas.shape[0], canvas.shape[1]
        cx0, cy0 = max(0, x0), max(0, y0)
        cx1, cy1 = min(W, x0 + w), min(H, y0 + h)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        a = (bmp[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0].astype(np.float64) / 255.0) * alpha
        a3 = a[:, :, None]
        region = canvas[cy0:cy1, cx0:cx1, :3]
        canvas[cy0:cy1, cx0:cx1, :3] = region * (1 - a3) + col * a3
        if canvas.shape[2] == 4:
            canvas[cy0:cy1, cx0:cx1, 3] = np.maximum(canvas[cy0:cy1, cx0:cx1, 3], a * 255)


# ---------- layout helpers ----------

def wrap_lines(font, text, size_px, max_width, direction="rtl"):
    """Greedy wrap on spaces (never breaks ZWNJ-joined words)."""
    words = text.split(" ")
    lines = []
    cur = ""
    sp = font.measure(" ", size_px, direction)
    for w in words:
        trial = w if not cur else cur + " " + w
        if font.measure(trial, size_px, direction) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def paragraph(canvas, font, text, size_px, color, x_right, y_top, width,
              leading=None, align="right", alpha=1.0, direction="rtl", line_scale=1.0):
    """align: 'right' (rtl start), 'center', 'left'. Returns y after last baseline."""
    asc, desc, h = font.metrics(size_px)
    if leading is None:
        leading = h * 1.0
    lines = wrap_lines(font, text, size_px, width, direction)
    y = y_top + asc * line_scale
    for ln in lines:
        w = font.measure(ln, size_px, direction)
        if align == "right":
            xr = x_right
        elif align == "center":
            xr = x_right - width / 2.0 + w / 2.0
        else:
            xr = x_right - width + w
        font.draw(canvas, ln, size_px, xr, y, color, direction, alpha)
        y += leading
    return y - leading + desc, lines


def line_count(font, text, size_px, width, direction="rtl"):
    return len(wrap_lines(font, text, size_px, width, direction))


# ---------- vector / graphic helpers ----------

def new_canvas(w, h, bg):
    c = np.zeros((h, w, 4), dtype=np.float64)
    c[:, :, 0] = bg[0]; c[:, :, 1] = bg[1]; c[:, :, 2] = bg[2]; c[:, :, 3] = 255
    return c


def fill_rect(canvas, x0, y0, x1, y1, color, alpha=1.0):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    if x1 <= x0 or y1 <= y0: return
    a = alpha
    col = np.array(color[:3], dtype=np.float64)
    r = canvas[y0:y1, x0:x1, :3]
    canvas[y0:y1, x0:x1, :3] = r * (1 - a) + col * a


def hline(canvas, x0, x1, y, color, thickness=1.0, alpha=1.0):
    t = max(1, int(round(thickness)))
    fill_rect(canvas, x0, y - t / 2.0, x1, y + t / 2.0, color, alpha)


def vline(canvas, x, y0, y1, color, thickness=1.0, alpha=1.0):
    t = max(1, int(round(thickness)))
    fill_rect(canvas, x - t / 2.0, y0, x + t / 2.0, y1, color, alpha)


def diamond(canvas, cx, cy, r, color, alpha=1.0):
    ys, xs = np.mgrid[0:canvas.shape[0], 0:canvas.shape[1]]
    # local window only
    x0, x1 = int(cx - r - 2), int(cx + r + 3)
    y0, y1 = int(cy - r - 2), int(cy + r + 3)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(canvas.shape[1], x1), min(canvas.shape[0], y1)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = (np.abs(xx - cx) + np.abs(yy - cy))
    a = np.clip(r - d, 0, 1) * alpha
    col = np.array(color[:3], dtype=np.float64)
    a3 = a[:, :, None]
    reg = canvas[y0:y1, x0:x1, :3]
    canvas[y0:y1, x0:x1, :3] = reg * (1 - a3) + col * a3


def circle(canvas, cx, cy, r, color, alpha=1.0, ring=0.0, ring_color=None):
    x0, x1 = int(cx - r - ring - 3), int(cx + r + ring + 4)
    y0, y1 = int(cy - r - ring - 3), int(cy + r + ring + 4)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(canvas.shape[1], x1), min(canvas.shape[0], y1)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    if ring > 0:
        rc = np.array((ring_color or color)[:3], dtype=np.float64)
        ar = np.clip((ring / 2.0 + 0.5) - np.abs(d - r), 0, 1) * alpha
        a3 = ar[:, :, None]
        reg = canvas[y0:y1, x0:x1, :3]
        canvas[y0:y1, x0:x1, :3] = reg * (1 - a3) + rc * a3
    a = np.clip(r - d, 0, 1) * alpha
    if ring > 0:
        a = np.clip(a - np.clip((ring / 2.0 + 0.5) - np.abs(d - r), 0, 1), 0, 1) * alpha if False else a
    col = np.array(color[:3], dtype=np.float64)
    a3 = a[:, :, None]
    reg = canvas[y0:y1, x0:x1, :3]
    canvas[y0:y1, x0:x1, :3] = reg * (1 - a3) + col * a3


def rounded_rect(canvas, x0, y0, x1, y1, r, color, alpha=1.0, border=0.0,
                 border_color=None, border_alpha=None):
    """Proper signed-distance rounded rectangle fill + edge border."""
    x0, y0, x1, y1 = float(x0), float(y0), float(x1), float(y1)
    ix0, iy0 = max(0, int(x0) - 2), max(0, int(y0) - 2)
    ix1, iy1 = min(canvas.shape[1], int(x1) + 3), min(canvas.shape[0], int(y1) + 3)
    yy, xx = np.mgrid[iy0:iy1, ix0:ix1]
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    qx = np.abs(xx - cx) - (x1 - x0) / 2.0 + r
    qy = np.abs(yy - cy) - (y1 - y0) / 2.0 + r
    d = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    a = np.clip(0.5 - d, 0, 1) * alpha
    col = np.array(color[:3], dtype=np.float64)
    reg = canvas[iy0:iy1, ix0:ix1, :3]
    out = reg * (1 - a[:, :, None]) + col * a[:, :, None]
    if border > 0 and border_color is not None:
        ba = alpha if border_alpha is None else border_alpha
        bc = np.array(border_color[:3], dtype=np.float64)
        ab = np.clip((border / 2.0 + 0.5) - np.abs(d), 0, 1) * ba
        out = out * (1 - ab[:, :, None]) + bc * ab[:, :, None]
    canvas[iy0:iy1, ix0:ix1, :3] = out


def vgradient(canvas, y0, y1, color, a0, a1):
    """vertical alpha gradient of color from a0 at y0 to a1 at y1"""
    y0, y1 = int(y0), int(y1)
    if y1 <= y0: return
    n = y1 - y0
    al = np.linspace(a0, a1, n)[:, None, None]
    col = np.array(color[:3], dtype=np.float64)[None, None, :]
    reg = canvas[y0:y1, :, :3]
    canvas[y0:y1, :, :3] = reg * (1 - al) + col * al


def paste_image(canvas, img_rgba, x, y, w=None, h=None, alpha=1.0):
    """img_rgba: PIL RGBA image; paste with alpha compositing at (x,y) top-left."""
    from PIL import Image
    if w or h:
        iw, ih = img_rgba.size
        nw = w or int(iw * (h / ih))
        nh = h or int(ih * (w / iw))
        img_rgba = img_rgba.resize((int(nw), int(nh)), Image.LANCZOS)
    arr = np.asarray(img_rgba, dtype=np.float64)
    ih, iw = arr.shape[0], arr.shape[1]
    x, y = int(x), int(y)
    cx0, cy0 = max(0, x), max(0, y)
    cx1, cy1 = min(canvas.shape[1], x + iw), min(canvas.shape[0], y + ih)
    if cx1 <= cx0 or cy1 <= cy0: return
    sa = arr[cy0 - y:cy1 - y, cx0 - x:cx1 - x, 3:4] / 255.0 * alpha
    sc = arr[cy0 - y:cy1 - y, cx0 - x:cx1 - x, :3]
    reg = canvas[cy0:cy1, cx0:cx1, :3]
    canvas[cy0:cy1, cx0:cx1, :3] = reg * (1 - sa) + sc * sa


def grain(canvas, amount=2.2, seed=7):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amount, (canvas.shape[0], canvas.shape[1], 1))
    canvas[:, :, :3] = np.clip(canvas[:, :, :3] + n, 0, 255)


def to_uint8(canvas):
    return np.clip(canvas, 0, 255).astype(np.uint8)
