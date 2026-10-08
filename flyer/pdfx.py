# -*- coding: utf-8 -*-
"""Add PDF/X-3:2002 conformance to the press PDF via a standard PDF
incremental update: embeds the ISO Coated v2 (FOGRA39) ICC as
/DestOutputProfile in an /OutputIntent and tags the catalog with
/GTS_PDFXVersion. Original bytes are untouched; readers see the update."""
import re, sys

SRC = "out/press/midnight_library_A5_flyer_press.pdf"
DST = "out/press/midnight_library_A5_flyer_press_PDFX3.pdf"
ICC = "/home/user/tools/icc/ISOcoated_v2_300_eci.icc"

data = bytearray(open(SRC, "rb").read())
m = re.search(rb"trailer\s*<<\s*/Root (\d+) 0 R\s*/Size (\d+)(\s*/Info (\d+) 0 R)?\s*>>\s*startxref\s*(\d+)", data)
root, size, _, info, old_xref = int(m.group(1)), int(m.group(2)), m.group(3), m.group(4), int(m.group(5))
pages = int(re.search(rb"%d 0 obj<<\s*/Type /Catalog\s*/Pages (\d+) 0 R" % root, data).group(1))

icc = open(ICC, "rb").read()
n_icc, n_oi, n_cat = size, size + 1, size + 2
off = {}
out = bytes(data)
base = len(out)

def obj(num, body_bytes, stream=None):
    global out
    off[num] = len(out)
    chunk = b"%d 0 obj\n" % num + body_bytes
    if stream is not None:
        chunk += b"stream\n" + stream + b"\nendstream\n"
    chunk += b"endobj\n"
    out += chunk if isinstance(out, bytes) else chunk
    # rebuild via bytearray concat
    return chunk

# assemble appended part
app = b""
off[n_icc] = base + len(app)
app += b"%d 0 obj\n<< /N 4 /Length %d >>\nstream\n" % (n_icc, len(icc)) + icc + b"\nendstream\nendobj\n"
off[n_oi] = base + len(app)
app += (b"%d 0 obj\n<< /Type /OutputIntent /S /GTS_PDFX "
        b"/OutputConditionIdentifier (ISO Coated v2 \\(ECI\\)) "
        b"/RegistryName (http://www.color.org) "
        b"/Info (ISO Coated v2 (ECI) / FOGRA39 / TAC 300%%) "
        b"/DestOutputProfile %d 0 R >>\nendobj\n" % (n_oi, n_icc))
off[n_cat] = base + len(app)
app += (b"%d 0 obj\n<< /Type /Catalog /Pages %d 0 R "
        b"/GTS_PDFXVersion (PDF/X-3:2002) /GTS_PDFXConformance (PDF/X-3:2002) "
        b"/OutputIntents [%d 0 R] >>\nendobj\n" % (n_cat, pages, n_oi))
xref_off = base + len(app)
app += b"xref\n%d 3\n" % n_icc
for num in (n_icc, n_oi, n_cat):
    app += b"%010d 00000 n \n" % off[num]
app += (b"trailer\n<< /Root %d 0 R /Size %d%s /Prev %d >>\nstartxref\n%d\n%%%%EOF\n"
        % (n_cat, size + 3, (b" /Info %d 0 R" % int(info)) if info else b"", old_xref, xref_off))
open(DST, "wb").write(out + app)
print("wrote", DST, len(out) + len(app), "bytes; new objs", (n_icc, n_oi, n_cat), "root->", n_cat)
