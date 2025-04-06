"""
Remove an image identified by xref
--------------------------------------------------------------------------------
License: GNU GPL V3
(c) 2022 Jorj X. McKie

Usage
-----
python remove.py

Description
-----------
This script does a pseudo-removal actually by replacing the image with a small
fully transparent pixmap.
"""

import pymupdf
from replace import img_replace

if tuple(map(int, pymupdf.VersionBind.split("."))) < (1, 19, 5):
    raise ValueError("Need v1.19.5+")

doc = pymupdf.open("input.pdf")

page = doc[0]

images = page.get_images()  # we only are interested in first image here
item = images[0]
old_xref = item[0]

pix = pymupdf.Pixmap(pymupdf.csGRAY, (0, 0, 1, 1), 1)
pix.clear_with()
img_replace(page, old_xref, pixmap=pix)

doc.ez_save("output_remove.pdf", garbage=4)
