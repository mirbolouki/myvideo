# -*- coding: utf-8 -*-
"""Print production: sRGB 300dpi masters -> ISO Coated v2 (FOGRA39, 300% TAC)
CMYK TIFFs + combined press PDF at bleed size, plus RGB proof sheets with
trim / safe guides.   Usage: python press.py sideA [sideB ...]"""
import sys, os
from PIL import Image, ImageDraw, ImageCms
import numpy as np

ICC_SRGB = "/home/user/tools/icc/sRGB_v4_ICC_preference.icc"
ICC_CMYK = "/home/user/tools/icc/ISOcoated_v2_300_eci.icc"
os.makedirs("out/press", exist_ok=True)
MM = 300 / 25.4
BLEED_MM = 3.0

sides = sys.argv[1:] or ["sideA"]
prof_in = ImageCms.getOpenProfile(ICC_SRGB)
prof_out = ImageCms.getOpenProfile(ICC_CMYK)
tiffs, pdfs = [], []

for s in sides:
    src = f"out/{s}_300dpi.png"
    rgb = Image.open(src).convert("RGB")
    cmyk = ImageCms.profileToProfile(rgb, prof_in, prof_out,
                                     renderingIntent=ImageCms.Intent.PERCEPTUAL,
                                     outputMode="CMYK")
    tif = f"out/press/{s}_cmyk_300dpi.tif"
    cmyk.save(tif, dpi=(300, 300), compression="tiff_lzw")
    tiffs.append((s, cmyk))
    a = np.asarray(cmyk).astype(np.uint16)
    tac = a.sum(axis=2) / 100.0
    print(f"{s}: mode={cmyk.mode} size={cmyk.size} maxTAC={tac.max():.0f}% meanTAC={tac.mean():.0f}% "
          f"K_max={a[:,:,3].max()}")
    # proof sheet
    d = ImageDraw.Draw(rgb, "RGBA")
    b = BLEED_MM * MM
    d.rectangle((b, b, rgb.width - b, rgb.height - b), outline=(255, 0, 120, 230), width=2)
    d.rectangle((10 * MM, 10 * MM, rgb.width - 10 * MM, rgb.height - 10 * MM),
                outline=(0, 200, 255, 210), width=2)
    L = 6 * MM
    for cx, cy, sx, sy in [(b, b, 1, 1), (rgb.width - b, b, -1, 1),
                           (b, rgb.height - b, 1, -1), (rgb.width - b, rgb.height - b, -1, -1)]:
        d.line([(cx - sx * L, cy), (cx - sx * (b - 2), cy)], fill=(255, 255, 255, 255), width=2)
        d.line([(cx, cy - sy * L), (cx, cy - sy * (b - 2))], fill=(255, 255, 255, 255), width=2)
    rgb.resize((rgb.width // 2, rgb.height // 2), Image.LANCZOS).save(f"out/press/proof_{s}.png")

pdf = "out/press/midnight_library_A5_flyer_press.pdf"
imgs = [c for _, c in tiffs]
imgs[0].save(pdf, resolution=300.0, save_all=True, append_images=imgs[1:])
print("press pdf:", pdf, os.path.getsize(pdf), "bytes, pages:", len(imgs))
