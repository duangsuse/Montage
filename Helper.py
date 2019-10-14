#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# DIP helper toolkit

# str not empty
notEmpty = lambda s: len(s) !=0
# isEven and isOdd
isEven = lambda n: (n%2) !=0
isOdd = lambda n: not isEven(n)
iplus = lambda a, b: int(a + b)
percentage = lambda p: p/100
# Integral division (trunc)
idiv = lambda b, a: int(b / a)
# parse/show Hexad number
hexRead = lambda s: int(s, 16)
hexWrite = lambda i: padStart('0', 2, hex(i)[2:])

# Distance between color
def colorDistance(c0, c1):
  ti_dista = lambda s01: abs(s01[0] - s01[1])
  return sum(map(ti_dista, zip(c0, c1)))

# f_x. If f_x is fun, f_x()
# delazy(1), delazy(lambda: 1)
def delazy(f_x): return f_x() if callable(f_x) else f_x

# (ty)x=x, (t)x=cast(x)
def coerce(ty, x, cast):
  return x if type(x)==ty else cast(x)

# Try op(), if e caught then delazy(fail)
# xs=iter([1]); Try(lambda: next(xs), 0, StopIteration)
def Try(op, fail, e=Exception):
  try:
    return op()
  except e:
    return delazy(fail)

from profile import time
# With perf counter log
def timed(desc, fmt=lambda x:'', p=lambda: __debug__):
  def __giveop(op):
    def __timed(*args, **kwargs):
      start = time.perf_counter(); res = op(*args, **kwargs)
      cost = time.perf_counter() - start
      if p(): print(f'{delazy(desc)} costs {cost} secs{fmt(args)}')
      return res
    return __timed
  return __giveop

# Call&collect f until generator breaks
def forever(f):
  try:
    while True: yield f()
  except StopIteration: return

# Try coerce xs to iter
def mayIter(xs):
  return Try(lambda: iter(xs), xs, TypeError)

# x^n
def repeat(x, n):
  assert n >= 0, 'N should be natrual number'
  while n != 0: yield x; n -= 1

# Concat all iters
def concat(*iters, cast=mayIter, rev=reversed):
  iterl = list(rev(iters))
  while notEmpty(iterl):
    xs = cast(iterl.pop())
    try:
      for it in xs: yield it
    except StopIteration: pass

# [XXX(n-len(s))s...](n)
# Case of ('**', 7, ...),  '**'[0:1] is used
def padStart(pre, n, s, rest=lambda pre, nm: pre[0:nm]):
  if len(s) >= n: return s
  npad, m = divmod(n-len(s),len(pre))
  return ''.join(concat(repeat(pre, npad), rest(pre, m), s))

# parse '#'? (hex*2)*n
def parseHexColor(hrepr:str, tupn:int=None, k:int=2, read=hexRead):
  assert notEmpty(hrepr), 'Give me a hexcolor'
  hassharp = hrepr[0] == '#'; sz = len(hrepr)
  if hassharp: assert isEven(sz), 'Not a htmlcolor: length not even'
  else: assert isOdd(sz), 'Not a hexcolor: length not odd'
  tupn = tupn or idiv(len(hrepr), k)
  beg = 1 if hassharp else 0
  ary = [read(hrepr[i:(i+k)]) for i in range(beg, k*tupn, k)]
  return tuple(ary)

# Write a string to bytearray
def bawrite(ba, offset, s):
  for i, c in enumerate(s):
    ba[offset+i] = ord(c)
# write prefixed hex tuple
# 很辣鸡，但是或许会稍微快一点……
def showHexColor(tup:tuple, prefix:str='#', show=hexWrite, bpi:int=2):
  prefixbs = prefix.encode(); tlen = len(tup)
  pflen = len(prefixbs); tslen = bpi*tlen
  shown = bytearray(pflen+tslen)
  bawrite(shown, 0, prefix)
  for n, xi in enumerate (range (0, tslen, bpi)):
    bawrite(shown, pflen+ xi, show(tup[n]))
  return shown.decode()





