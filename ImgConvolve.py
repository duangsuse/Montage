#!/usr/bin/env python3
# -*- coding: utf8 -*-

from PIL import Image
from PIL import ImageDraw, ImageFont
from PIL import ImageChops

import numpy as np
from PIL.ImageFilter import Kernel

from os import cpu_count
from joblib import Parallel
from joblib import delayed as makeJob

from Helper import notEmpty, timed, coerce

def convline(mode,xss,yss, ln): return [calconv(xys, mode) for xys in zip(xss[ln], yss[ln])]
def calconv(a_b_, mode): return np.convolve(a_b_[0], a_b_[1], mode)

# A class for abstractions processing image with Pillow
# author: duangsuse, date: Oct 14, 2019
class Convol:
  def __init__(self, image: Image):
    self.img = image
  # Create new instance, changing only the target image
  def wrap(self, other: Image):
    return Convol(image=other)
  # Numpy Array [v][h]
  def array(self) -> np.array:
    return np.asarray(self.img)

  # `Direct` convolve with array
  @timed('Array convolve')
  def array_convolve(self, other: np.array, mode='same', jobs=cpu_count(), **kwargs) -> np.array:
    xss, yss = self.array(), other
    convolution = Parallel(n_jobs=jobs, backend='loky', **kwargs) (
      [makeJob(convline)(mode,xss,yss, ln) for ln in range(0, minLen(xss, yss))]  )
    return np.array(convolution)
  # Kernel convolve
  @timed('Filter convolve')
  def filter_convolve(self, matrix: Kernel, **kwargs):
    kern = coerce(Kernel, matrix, lambda m: make_kernel(m, **kwargs))
    return self.img.filter(kern)

  # `Direct` (pixel-to-pixel) convolve with other image
  def convolve_array(self, other: Image, **kwargs) -> np.array:
    other = coerce(np.array, other, lambda o: self.wrap(o).array())
    return self.array_convolve(other, **kwargs)
  # `Direct` convolve to image
  def convolve(self, other: Image, **kwargs) -> Image:
    return Image.fromarray(self.convolve_array(other, **kwargs))

def open(*args, **kwargs):
  return Convol(Image.open(*args, **kwargs))

def new(*args, **kwargs):
  return Convol(Image.new(*args, **kwargs))

# S_x [[1, 0, -0.2], [1, 0, -1], [0.1, 0, -1.8]]
# p.filter_convolve(S_x).show()
def make_kernel(matrix: list, **kwargs) -> Kernel:
  matrix = np.array(matrix)
  assert notEmpty(matrix), 'Empty kernel'
  n, m = (len(matrix), len(matrix[0]))
  return Kernel(size=(n, m), kernel=matrix.flatten(), **kwargs)

def minLen(xs, ys): return min(len(xs), len(ys))

# 最后我不得不说，Python 的 self 看起来不错，实际上余赘会使得 OOP 继承抽象类编程的乐趣损失殆尽
