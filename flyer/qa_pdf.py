# -*- coding: utf-8 -*-
"""QA: verify the press PDF from the outside — structure, page geometry,
and pixel integrity of the embedded CMYK JPEG pages vs the source TIFFs."""
import re, sys, io
import numpy as np
from PIL import Image

pdf_path = sys.argv[1] if len(sys.argv) > 1 else "out/press/midnight_library_A5_flyer_press.pdf"
data = open(pdf_path, "rb").read()
print("file:", pdf_path, len(data), "bytes")
print("header:", data[:8], "| startxref present:", b"startxref" in data[-1024:])
boxes = set(re.findall(rb"/MediaBox \[([^\]]+)\]", data))
print("MediaBox:", boxes, " (436.56x612.24 pt = 154x216 mm)")
print("pages (/Type /Page):", len(re.findall(rb"/Type\s*/Page[^s]", data)))
print("colorspace of images:", set(re.findall(rb"/ColorSpace\s*/(\w+)", data)))
print("filters:", set(re.findall(rb"/Filter\s*/(\w+)", data)))

# extract embedded JPEG streams and compare with source TIFFs
streams = []
for m in re.finditer(rb"(?<!end)stream\r?\n", data):
    start = m.end()
    end = data.index(b"endstream", start)
    chunk = data[start:end]
    if chunk[:2] == b"\xff\xd8":
        streams.append(chunk)
print("jpeg streams found:", len(streams))
ok = True
for i, (chunk, side) in enumerate(zip(streams, ["sideA", "sideB"])):
    im = Image.open(io.BytesIO(chunk))
    arr = np.asarray(im).astype(np.int16)
    ref = np.asarray(Image.open(f"out/press/{side}_cmyk_300dpi.tif")).astype(np.int16)
    if arr.shape != ref.shape:
        print(side, "SHAPE MISMATCH", arr.shape, ref.shape); ok = False; continue
    mad = np.abs(arr - ref).mean()
    inv = np.abs((255 - arr) - ref).mean()
    tag = "direct" if mad < inv else "adobe-inverted"
    diff = min(mad, inv)
    print(f"page {i+1} ({side}): mode={im.mode} size={im.size} marker={tag} meanAbsDiff={diff:.2f}/255")
    if diff > 6:
        ok = False
print("PDF PIXEL INTEGRITY:", "PASS" if ok else "FAIL")
