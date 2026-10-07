# -*- coding: utf-8 -*-
"""تختهٔ مرور کل دفترچه — از خود PNGهای تولیدشده"""
import os, sys, glob
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
ROOT='/home/user/myvideo'; D=f'{ROOT}/docs/06-approval-deck'
FD=f'{ROOT}/assets/print/fonts'
def F(w,s): return ImageFont.truetype(f'{FD}/Vazirmatn-{w}.ttf', s)
def fa(t): return get_display(arabic_reshaper.reshape(t))
files=sorted(glob.glob(f'{D}/board-*.png'), key=lambda p:int(p.split('board-')[1][:2]))
cell=(430,304); cols=4
import math; rows=math.ceil(len(files)/cols)
PAD=36; HEAD=110
W=cols*cell[0]+PAD*2; H=HEAD+rows*(cell[1]+40)+PAD
im=Image.new('RGB',(W,H),(246,243,238)); d=ImageDraw.Draw(im)
d.text((W//2,26), fa('دفترچهٔ گزارش ۱۴بندی — مرور کل'), font=F('Bold',44), fill=(7,20,38), anchor='ma')
fa_digits = lambda t: t.translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))
d.text((W//2,80), fa(f'{fa_digits(str(len(files)))} تختهٔ تصویری · مسیر: docs/06-approval-deck/report-14pt.pdf · تختهٔ ۰۱ تا {fa_digits(f"{len(files):02d}")}'), font=F('Regular',26), fill=(108,116,130), anchor='ma')
for i,p in enumerate(files):
    n=int(p.split('board-')[1][:2])
    t=Image.open(p).convert('RGB'); t.thumbnail(cell)
    x=PAD+(i%cols)*cell[0]+(cell[0]-t.width)//2
    y=HEAD+(i//cols)*(cell[1]+40)
    d.rectangle((x-3,y-3,x+t.width+3,y+t.height+3), fill=(255,255,255), outline=(222,215,204), width=2)
    im.paste(t,(x,y))
    d.text((x+t.width//2, y+t.height+8), fa(f'تختهٔ {n:02d}'), font=F('Medium',22), fill=(90,98,110), anchor='ma')
im.save(f'{D}/overview.png', optimize=True)
print('overview ok', im.size, len(files),'boards')
