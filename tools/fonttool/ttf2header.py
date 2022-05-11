#!/usr/bin/python3

#
# (c) 2022 by Fabrizio Di Vittorio (part of www.fabgl.com)
#
# please install prerequisites:
#   pip3 install Pillow
#

from PIL import Image, ImageFont, ImageDraw
import sys
import re
import os
import math



def writeRow(file, width, y, data):
  file.write("  ")
  b = 0
  for x in range(width):
    if b == 0:
      file.write("0b")
    i = y * width + x
    if i < len(data) and data[i] > 127:
      file.write("1")
    else:
      file.write("0")
    b += 1
    if b == 8:
      b = 0
      file.write(", ")
  if b > 0 and b < 8:
    while b < 8:
      file.write("0")
      b += 1
    file.write(", ")
  file.write("\n")
  


def savefontVar_h(f, file, fname, stroke):
  fname = re.sub('[^0-9a-zA-Z]+', '_', f.getname()[0])
  file.write("// {}\n".format(fname))
  file.write("#pragma once\n\n")
  file.write("namespace fabgl {\n\n")
  file.write("#ifdef FABGL_FONT_INCLUDE_DEFINITION\n\n")

  file.write("static const uint8_t FONT_{}_DATA[] = {{\n".format(fname))
  chptr = []
  chptrPos = 0
  
  mh = 0
  for i in range(256):
    w, h = f.getsize(chr(i), stroke_width = stroke)
    if h > mh: mh = h
  
  for i in range(256):
    mask, off = font.getmask2(chr(i), stroke_width = stroke, mode = "1")
    if mask:
      #print(i, "size:", mask.size, "off:", off, "mh:", mh)
      width, height = mask.size
    else:
      width = f.getsize(chr(i), stroke_width = stroke)[0]
      height = 0
    chptr.append(chptrPos)
    sz = (int)(1 + mh * math.ceil(max(8, width) / 8))
    chptrPos += sz
    file.write("  // chr={} sz={} w={} h={}\n".format(i, sz, width, mh))
    file.write("  {}, \n".format(width))
    for y in range(off[1]):
      writeRow(file, width, 0, [])
    for y in range(height):
      writeRow(file, width, y, mask)
    for y in range(mh - height - off[1]):
      writeRow(file, width, 0, [])
  file.write("};\n\n\n")

  file.write("static const uint32_t FONT_{}_CHPTR[] = {{\n  ".format(fname))
  col = 1
  for i in chptr:
    file.write("{:4}, ".format(i))
    if col % 15 == 0:
      file.write("\n  ")
    col += 1
  file.write("};\n\n\n")

  file.write("static const FontInfo FONT_{} = {{\n".format(fname))
  file.write("  .pointSize = {},\n".format(mh))
  file.write("  .width     = 0,\n")
  file.write("  .height    = {},\n".format(mh))
  file.write("  .ascent    = {},\n".format(0))
  file.write("  .inleading = {},\n".format(0))
  file.write("  .exleading = {},\n".format(0))
  flags = ["0"]
  flags.append("FONTINFOFLAGS_VARWIDTH")
  file.write("  .flags     = " + " | ".join(flags) + ",\n")
  file.write("  .weight    = {},\n".format(0))
  file.write("  .charset   = {},\n".format(0))
  file.write("  .data      = FONT_{}_DATA,\n".format(fname))
  file.write("  .chptr     = FONT_{}_CHPTR,\n".format(fname))
  file.write("  .codepage  = 1252,\n")
  file.write("};\n\n")
  file.write("#else\n\n")
  file.write("extern const FontInfo FONT_{};\n\n".format(fname))
  file.write("#endif\n\n")
  file.write("}\n")




if sys.version_info[0] < 3:
  sys.stderr.write("\nPlease use Python 3!\n\n")
  exit()

args = sys.argv[1:]
argn = len(args)

if argn < 2:
  print("usage:\n  python3 ttf2header.py filename size [stroke]")
  print("example:\n  python3 ttf2header.py Arial.ttf 24")
  sys.exit()

input_file = args[0]
out_file   = os.path.splitext(input_file)[0] + ".h"
font_size  = int(args[1])
stroke     = int(args[2]) if argn >= 3 else 0

font = ImageFont.truetype(font = input_file, size = font_size)

fp = open(out_file, "w")
savefontVar_h(font, fp, font.getname()[0], stroke)
fp.close()
