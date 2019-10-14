# Montage PY

一个简单的蒙特图（彩色文字组成图形）生成器，使用 Python3 编写（需要 `lambda` 特性简化语法）

使用了 Pillow、Numpy 来进行矩阵运算（诸如互相关）、瞎 `pip3 list` 找的 `joblib` 来执行矩阵（或序列集）运算的并行化

灵感来自另一个 [简易文字蒙太奇](https://github.com/FerryYoungFan/SimpleTextMontage)

至于为什么又起名叫做蒙特图，只是个名字而已……

## 蒙特图的大致处理过程

+ 读取输入图像，预处理
+ 分配输出图像，其大小默认是预处理图像的大小
+ 根据文本排版布局开始，文本流意味着每次使用不同的文本开始排字（这样可以实现 N 字一色而不是单个 `-txt` 只有一种颜色、必须等重复）
  + 区块意味着 `(文字X, 文字Y)-(文字X+Width+textspH*2, 文字Y+Height+textspV*2)`，即文字覆盖区域 （公式已经作为 `lambda` 参数方便修改）
  + 取文本后的图像色区块计算其平均色和背景flag
  + 如果是背景，不要生成文字
  + 否则画上（自动变色）的文字
  + 默认情况下， `foreach x. y=...` 一行的文字排版会作为一个 job 并行计算
+ 重复处理直到表示完整个图像

## 支持特性

+ 要嵌入的文本： `textBlend`. `--text, -txt`
+ 把文本视作文本流： `textIsSequence`. `--text-isseq, -tseq!` （以 `,` 切分，实际上后端 sep 是参数，前端不是）（啊实际上是直接在前端切分…… 后端看情况是从流取还是 `repeat(x,n)` ）
+ 指定文本颜色而不使用自动根据背景变换： `textColor`. `--text-color, -txtcr` （在仅仅只用此工具生成辅助图像处理的图层时有用）
+ 生成图像的字体（大小）： `font, fontSize`. `--font, -fnt`. `--font-size, -fntsz`
+ 文本文字间隔/行间距： `spaceTextH, spaceTextV`. `--text-space, -textsp H V`
+ 源图像左右/上下生成间隔： `paddingLR, paddingUB`. `--padding, -pad LR UB`
+ 分配生成图像的大小： `outputScale`. `--draw-size, -size`

+ 支持蒙特自动（当然是按照文字布局）裁切图像，主体（不同于背景色的部分）使用相应文字表示：
  + `backgroundColor`. `--background-color, -bgcolor` 背景色，默认 `#FFFFFF`
  + `backgroundCrDiffMax`. `--background-diffmax, -bgdiffLT` 最大限度的色值『不同』程度，默认 `#0a0a0a`
  + `backgroundCrDiffAlgor`. `--background-diffalg, -bgdiff` 色差算法，可以选择 `lum` （低精度灰度） 或 `identity` （直接求差）。结果会通过 `abs(...)`
  + `textTintThres`. `--text-tint-thres, -bgtintGT% N` 当请求色区拥有 N% 个（模糊）背景色块时，跳过此块生成 `(tintGT/100)>(bgpxs/blkpxs)`
+ 蒙特还允许使用变换矩阵进行『互相关』预处理（就是 GIMP 的蒙板），以方便特殊图像的处理需求
  + `preprocessMatrix`. `--kernel, -kern` 在开始求当前色区块的主体色/填充flag 之前，可以先利用矩阵进行互相关变换，矩阵作为 `Image` 递交
  + `preprocessMatrixIsDiffOnly`. `--kernel-diffonly, -kern-diff` 如果为真，则只在判断是否显字时使用互相关运算，求色区块平均色则不使用

+ 同时构造并且输出渲染文本的结构（文字+换行序列，包括背景色的部分，可以用来生成 ASCII Art），这个部分由前端辅助 `emitFrameSource`, `-emit-frame fmt`

以下是无关生成算法的参数

+ 输入图像们： `image [image ...]`
+ 图像编码格式： `saveFormat`. `--output-format, -oe`
+ 输入/输出的色彩模式： `colorspace, colorspaceInput`. `--convert, -ic`, `--output-crspace, -oc`
+ 并行处理任务数： `--jobs, -j`
+ 安静模式： `--quiet, -q!`
+ 批处理的输出文件名格式字符串： `ofnameFmtstr`. `--output-fmtstr, -ofstr`
+ 生成图像将被缩放到的大小： `postScale`. `--post-scale, -size-o` （这个版本很简陋，不支持自动计算文字间距）
+ 直接与原图像进行 Alpha 混合成： `--alpha-composite, -ac` 混成方式是 `（蒙特图 >> 原图）`
+ 直接与原图像进行混合： `--blend, -bl mon_alpha` 混合方法是 `(原图*(100%-mon_alpha) + 蒙特图*mon_alpha)`
+ 直接预览，不要输出（使用命令行）： `--preview cmd`
+ 直接预览，不要输出： `-view!`

### 关于输入的 Alpha （透明度）

因为透明度参数对蒙特图生成的影响实在是太小了，而且同时支持不同的 `(r,g,b,???,...)` 元组长度比较困难，所以暂时不打算支持

不过只是不保证可以用，Pillow 还是有一定兼容性的，可以利用 `--convert` 参数覆盖默认的 `RGB` 颜色系统

输出的 Alpha 由于默认 `--colorspace` 为 `ARGB`，不存在此问题

### 文本大小的计算

SimpleTextMontage 使用了 `fontSize*ratio` （输出画布和 font 都乘比例）的方式保证文本和画布比例相同，调整文本像素即可变动容字数

不过 MontagePY 没有使用，而是分离了输出画布和文字大小参数，这样很大的比例输出图也可以放许多很小的字（当然是说配置上方便一些，等价的）。

如果要使用自动配置的 `fontSize`, `outputScale`, `spaceText H/V`，提供 `--draw-ratio, -size%` 即可，不过它会被单独的配置覆盖。

### 关于 JSON Rpc API

参数 `--start-service, -serv`

使用 `--accept-filename`, `--accept-listing, -serv-list` 来支持使用文件名（而不是 fileno）/文件列表

Montage.py 支持使用 HTTP 接口访问来生成文本，并且接口和参数风格遵循一般的 Web 应用规范

利用 HTTP API，可以编写生成图片的 HTML 单/多页应用

生成接口暂时只提供解析执行命令行：

+ `GET /cmd?(command args)`, `POST /gen?args=(command args)`

+ `GET /fileno/(fileno)` 拿指定 fd 的图像
+ `DELETE /fileno/(fileno)` 删除指定 fd 的图像
+ `GET /file/(name)` 拿指定名字的图像
+ `DELETE /file/(name)` 删除指定名字的图像

不存在 `OPTIONS`

返回为 Json array `[ { name, fileno }, ... ]`

没错，暂时只能做单机……

## 使用 API

```python
from PIL import Image
from PIL import ImageDraw, ImageFont
from PIL import ImageChop

from joblib import Parallel
from joblib import delayed as makeJob

import numpy as np
from numpy import arange, asarray

(ImageFont.truetype, ImageFont.FreeTypeFont, ImageFont.load_path) # Fonts

(Image.width, Image.height) # Box2D
(Image.getpixel, Image.putpixel) # Color I/0
Image.resize # average resample???

(Image.open, Image.new) # Create
(Image.save, Image.show, Image.close) # Post ops
(Image.crop, Image.offset) # Crop
Image.alpha_composite # Composite with original image
Image.blend # Image blend

(arange, asarray, Image.fromarray) # Matrix processing
(Parallel, makeJob) # Parallel computing

(Image.seek) # Video processing???
(Image.getbbox) # For pre-processing blackbox???
Image.histogram # Use histogram-diff method???
```

## 排版公式

MontagePY 的排版复杂很多（单位的长度可能是不确定的），也不能在循环外直接计算 cols, rows

大致可以，但实际上，只有文本不是序列或序列长度一致 `--text-chars!, -tchars!` 的时候才能使用优化版公式

```python
global spaceTextH, spaceTextV
global paddingLR, paddingUB
global font
global currentText
global selectionW, selectionH

def idiv(b, a): return int(b / a)

textW, textH = font.getsize(currentText)
unitW, unitH = int(textW+ spaceTextH), int(textH+ spaceTextV)
cols, rows = (idiv(selectionW, unitW), idiv(selectionH, unitH))

gapLR, gapUB = (selectionW- (cols*unitw)), (selectionH- (rows*unith))
padLR, padUB = idiv(gapLR+spaceTextH,2), idiv(gapUB+spaceTextV,2)
```

然后可以如此循环来执行计算

```python
for ty in range(padUB, selectionH-padUB, unitH):
  for tx in range(padLR, selectionW-padLR, unitW):
    txt = next(text_seq)
    txtregion = toImageRegion(range(ty, ty+unitH), range(tx, tx+unitW))
    draw, backtint = colorAverage(txtregion)
    if not draw: continue
    color = textColor or backtint
    draw.text((tx,ty), txt, font=font, fill=color)
```

与隔壁的算法大致上等价（为了可读性重写了部分）

```python
usePreconfColor = len(textColor) > 0

for n in range(0, secRows):
    textx = leftPadding
    for m in range(0, secCols):
        tempsec = ims.crop((textx, texty, textx + secWidth, texty + secHeight))
        (ac, flg) = getAvgColor(tempsec)
        avgColor = RGB2hexColor(ac[0], ac[1], ac[2]) # 其实这里可以删掉，fill 不一定得是字符串
        #if flg is True and textp < len(text): # 这里 and 的第二个表达式可以删除
        if not flg: continue
        dr.text((textx, texty), text[textp],
            font=font, fill=textColor if usePreconfColor else avgColor)
        textp = (textp+1) % textp # 修改，也可改为 `max(lastIdx, textp)`?
        textx += secWidth #col
    texty += secHeight #row
```

## 许可证

懒得写，WTFPL

有点良心是不会瞎抄的、
没有良心是不会用其他语言和库改写算法的

## なに？你逗我？？？

虽然说了这么多，可其实现的只是一点点，连 CLI 都没有

只是因为太懒而且没时间的缘故，不要想太多，不喜也别喷（逃）😂

## ImgConvolve 的玩法

```python
import ImgConvolve
q=ImgConvolve.open('/home/DuangSUSE/Projects/Share/Others/avatar.webp')
p=ImgConvolve.open('/home/DuangSUSE/Projects/Share/Others/avatar.jpg')
r=p.convolve(q.img)
r.show()

p.filter_convolve([[1, 0, -0.2], [1, 0, -1], [0.1, 0, -1.8]]).show()
```

什么的，当然最重要的是我要拿它去算卷积…… 虽然很慢，大概只能对少部分大图像使用

