from __future__ import print_function
import pymupdf
import sys

print(pymupdf.__doc__)
# ==============================================================================
# Pie Chart program - semi circle version
# ==============================================================================
from pymupdf.utils import getColor  # for getting RGB colors by name

doc = pymupdf.open()  # new empty PDF
page = doc.new_page()  # creates an ISO-A4 page

img = page.new_shape()  # start a Shape (canvas) for the page

# title of the page
title = "Sitzverteilung nach der Bundestagswahl 2013"

# pie chart center and point of 1st data pie
center = pymupdf.Point(200, 250)
point = pymupdf.Point(100, 250)  # will cycle through table data

# this is the radius
radius = abs(point - center)

blue = getColor("blue")  # we need some colors
white = getColor("white")

lineheight = 20  # legend line height
ts_v = 150  # vertical start of legend block
ts_h = center.x + radius + 50  # horizontal coord of legend block

# these are the data to visualize:
# number of seats of political parties in German parliament since 2013
table = (  # seats, party color & name
    (64, "violetred", "Die Linke"),
    (193, "red", "SPD"),
    (63, "green", "Die Grünen"),
    (253, "black", "CDU"),
    (56, "dodgerblue", "CSU"),
    (1, "gray", "fraktionslos"),
)

seats = float(sum([c[0] for c in table]))  # total seats
stitle = "Bundestagssitze insgesamt: %i" % (seats,)

img.insert_text(pymupdf.Point(72, 72), title, fontsize=14, color=blue)
img.insert_text(pymupdf.Point(ts_h - 30, ts_v - 30), stitle, fontsize=13, color=blue)

img.draw_line(pymupdf.Point(72, 80), pymupdf.Point(550, 80))
img.finish(color=blue)

# draw the table data
for i, c in enumerate(table):
    beta = -c[0] / seats * 180  # express seats as angle in semi circle
    color = getColor(c[1])  # avoid multiple color lookups
    # the method delivers point of other end of the constructed arc
    # we will use it as input for next round
    point = img.draw_sector(center, point, beta, fullSector=True)
    img.finish(color=white, fill=color, closePath=False)

    text = "%s, %i %s" % (c[2], c[0], "Sitze" if c[0] > 1 else "Sitz")
    pos = pymupdf.Point(ts_h, ts_v + i * lineheight)
    img.insert_text(pos, text, color=blue)
    tl = pymupdf.Point(pos.x - 30, ts_v - 10 + i * lineheight)
    br = pymupdf.Point(pos.x - 10, ts_v + i * lineheight)
    rect = pymupdf.Rect(tl, br)  # legend color bar
    img.draw_rect(rect)
    img.finish(fill=color, color=color)

# overlay center of circle with white
img.draw_circle(center, radius - 70)
img.finish(color=white, fill=white)
img.commit()
doc.save("piechart2.pdf")
