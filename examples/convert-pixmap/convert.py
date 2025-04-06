"""
Convert an arbitrary pixmap to JPEG format using Pillow
--------------------------------------------------------------------------------
License: GNU GPL V3
(c) 2022 Jorj X. McKie

Usage
-----
python convert.py input.png

Dependencies
------------
Pillow
"""

import sys
import pymupdf
from PIL import Image

print(pymupdf.__doc__)
assert len(sys.argv) == 2, "Usage: %s <input file>" % sys.argv[0]

pix = pymupdf.Pixmap(sys.argv[1])
rgb = "RGB"
if pix.alpha:  # JPEG cannot have alpha!
    pix0 = pymupdf.Pixmap(pix, 0)  # drop alpha channel
    pix = pix0  # rename pixmap

img = Image.frombuffer(rgb, [pix.width, pix.height], pix.samples, "raw", rgb, 0, 1)
img.save("output.jpg")
