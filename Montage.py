#!/usr/bin/env python3
# -*- coding: utf8 -*-

# 抄袭的 Montage 图生成

from PIL import Image
from PIL import ImageDraw, ImageFont

from Helper import idiv, iplus, percentage, repeat, colorDistance
from Helper import parseHexColor as color
from Helper import showHexColor as showColor

def cfg_read_font(fnt: str, sz: int) -> ImageFont:
  if fnt is None:
    return ImageFont.load_default()
  elif len(fnt) !=0 and fnt[0] == ':':
    return ImageFont.load_path(fnt)
  else:
    try:
      return ImageFont.truetype(fnt[1:], sz)
    except OSError:
      return ImageFont.FreeTypeFont(fnt[1:], size=sz)

def coordinate(img: Image) -> (int, int):
  return (img.width, img.height)

global font # 文字字体
global spaceTextH, spaceTextV # 文字间隔/行间隔
global paddingLR, paddingUB # 顶部底部的间距

global texts # 文本流
global textColor # 文字颜色覆盖

global backgroundColor # 背景色
global backgroundDiffMax # 最大色差
global colorDistance # 差值算法
global backgroundThres # 区块里有 N% 时认为是背景色块

global outColorSpace

font = cfg_read_font(None, 14)
spaceTextH, spaceTextV = (0, 0)
paddingLR, paddingUB = (0, 0)
texts = repeat('#', float('Infinity'))
textColor = None

backgroundColor = color('#FFFFFF')
backgroundDiffMax = 10
backgroundThres = percentage(50)

outColorSpace = 'RGBA'
RGBA_0 = (0x00, 0x00, 0x00, 0x00)

def montage(img: Image, dstsize: (int, int)) -> Image:
  inW, inH = coordinate(img)
  dest = Image.new(outColorSpace, dstsize, RGBA_0)
  for txt in texts:
    textW, textH = font.getsize(txt)
    unitW, unitH = iplus(textW, spaceTextH), iplus(textH, spaceTextV)
    cols, rows = (idiv(inW, unitW), idiv(inH, unitH))
    gapLR, gapUB = (inW- (cols*unitW)), (inH- (rows*unitH))
    padLR, padUB = idiv(gapLR+spaceTextH, 2), idiv(gapUB+spaceTextV, 2)
    
    for ty in range(padUB, inH-padUB, unitH):
      for tx in range(padLR, inW-padLR, unitW):
        txtregion = (tx, ty, tx+unitW, ty+unitH)
        textback = img.crop(txtregion)

#
filename = 'p.png'
savename = 'Mon_'+filename
with Image.open(filename) as pic:
  out = montage(pic)
  out.save(savename)
  out.show('Montage: '+savename)

