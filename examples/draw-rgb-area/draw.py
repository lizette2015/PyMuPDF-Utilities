"""
Draw an RGB pixel area with numpy and save it with pymupdf
--------------------------------------------------------------------------------
License: GNU GPL V3
(c) 2022 Jorj X. McKie

Usage
-----
python draw.py

Description
-----------
This is 10+ times faster than saving with pure python solutions like pypng and
almost 2 times faster than saving with PIL. However, PIL images are smaller than
those of MuPDF.

Dependencies
------------
Pillow, numpy
"""

from __future__ import print_function
import sys
import time
import pymupdf
import numpy as np
import PIL
from PIL import Image

print("Python:", sys.version)
print("NumPy version", np.__version__)
print(pymupdf.__doc__)
print("PIL version", PIL.__version__)

height = 2048
width = 2028

image = np.ndarray((height, width, 3), dtype=np.uint8)

for i in range(height):
    for j in range(width):
        image[i, j] = np.array([i % 256, j % 256, (i + j) % 256], dtype=np.uint8)

samples = image.tobytes()

ttab = [(time.perf_counter(), "")]

pix = pymupdf.Pixmap(pymupdf.csRGB, width, height, samples, 0)
pix.save("output_pymupdf.png")
ttab.append((time.perf_counter(), "pymupdf"))

pix = Image.frombuffer("RGB", [width, height], samples, "raw", "RGB", 0, 1)
pix.save("output_PIL.png")
ttab.append((time.perf_counter(), "PIL"))

for i, t in enumerate(ttab):
    if i > 0:
        print("storing with %s: %g sec." % (t[1], t[0] - ttab[i - 1][0]))
