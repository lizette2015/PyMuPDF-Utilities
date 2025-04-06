"""
Draw a caustic curve
--------------------------------------------------------------------------------
License: GNU GPL V3+
(c) 2019 Jorj X. McKie

Usage
-----
python draw.py

Description
-----------
This script is intended to create simple graphics with the methods 'drawLine()',
'drawCircle()' and friends. A caustic is the shape the early morning sun paints
onto your desperately needed cup of coffee, when shining from a low angle
through the window on your left side ...

We draw each sun ray after it has been reflected by the cup.

The resulting picture is save in three image formats: PDF, PNG and SVG / SVGZ
"""

from __future__ import print_function
import gzip
import math
import pymupdf

print(pymupdf.__doc__)


def pvon(a):
    """Starting point of a reflected sun ray, given an angle a."""
    return (math.cos(a), math.sin(a))


def pbis(a):
    """End point of a reflected sun ray, given an angle a."""
    return (math.cos(3 * a - math.pi), (math.sin(3 * a - math.pi)))


fileprfx = "output"  # filename prefix
coffee = pymupdf.pdfcolor["coffee"]  # color: latte macchiato?
yellow = pymupdf.pdfcolor["yellow"]  # color of sun rays
blue = pymupdf.pdfcolor["blue"]  # color cup border
doc = pymupdf.open()  # new empty PDF
page = doc.new_page(-1, width=800, height=800)  # create square sized page
center = pymupdf.Point(
    page.rect.width / 2, page.rect.height / 2  # center of circle on page
)

radius = page.rect.width / 2 - 20  # leave a border of 20 pixels

img = page.new_shape()
img.draw_circle(center, radius)
img.finish(color=coffee, fill=coffee)  # fill coffee into the cup

count = 200  # how many sun rays we draw
interval = math.pi / count  # angle fraction
for i in range(1, count):
    a = -math.pi / 2 + i * interval  # go from -90 to +90 degrees
    von = pymupdf.Point(pvon(a)) * radius + center  # start point adjusted
    bis = pymupdf.Point(pbis(a)) * radius + center  # end point adjusted
    img.draw_line(von, bis)

img.finish(width=1, color=yellow, closePath=False)  # a ray is a fine yellow line

img.draw_circle(center, radius)
img.finish(color=blue)  # cup border is blue
page.set_cropbox(img.rect)  # adjust visible page
img.commit()
doc.save(fileprfx + ".pdf")

# create a PNG image
doc.get_page_pixmap(0).save(fileprfx + ".png")

# save as SVG / SVGZ images
svg = page.get_svg_image()
svgz = gzip.compress(svg.encode("utf-8"))
fout = open(fileprfx + ".svg", "w")
fout.write(svg)
fout.close()
fout = open(fileprfx + ".svgz", "wb")
fout.write(svgz)
fout.close()
