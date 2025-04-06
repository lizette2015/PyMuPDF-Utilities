"""
Created on Thu Jan  3 07:05:17 2019

@author: Jorj
@copyright: (c) 2019 Jorj X. McKie
@license: GNU AFFERO GPL V3

Purpose
--------
Visualize function "drawOval" by using a quadrilateral (tetrapod) as parameter.

For demonstration purposes, oval creation is placed in a function, which
accepts an integer parameter. This value controls the position of some
egdes of the quad.
It then creates a dummy temporary PDF with one page, containing stuff we want
to show and returns an image of it.

The function is called by the main program in an "endless" loop, passing in
the parameter. The image is displayed using PySimpleGUI.

Notes
------
* Changed generated page image format to "PPM", which is very much faster than
  "PNG" both, in terms of creation and reading by tkinter. It also makes us
  independent from the tkinter version used.
* We are not slowing down the speed of showing new images (= "frames per
  second"). The statistics displayed at end of program can hence be used as a
  performance indicator.

Requires
--------
PySimpleGUI, tkinter

"""
import math
import os
import time

import pymupdf
import PySimpleGUI as sg

mytime = time.perf_counter
if not list(map(int, pymupdf.VersionBind.split("."))) >= [1, 14, 5]:
    raise SystemExit("need PyMuPDF v1.14.5 for this script")
print(pymupdf.__doc__)

# ------------------------------------------------------------------------------
# make one page
# ------------------------------------------------------------------------------
def make_oval(i):
    """Make a PDF page and draw an oval inside a Quad.
    The lower two quad points and the fill color are subject to a passed-in
    parameter. Effectively, they exchange their position, thus causing
    changes to the drawn shape.
    The resulting page picture is passed back as an image and the PDF is
    dicarded again.
    """
    doc = pymupdf.open()  # dummy PDF
    red = (1, 0, 0)
    blue = (0, 0, 1)
    page = doc.new_page(width=400, height=300)  # page dimensions as you like
    r = page.rect + (+4, +4, -4, -4)  # leave a border of 4 pix
    q = r.quad  # full page rect as a quad
    f = i / 100.0
    if f >= 0:
        u = f
        o = 0
    else:
        u = 0
        o = -f
    q1 = pymupdf.Quad(
        q.ul + (q.ur - q.ul) * o,
        q.ul + (q.ur - q.ul) * (1 - o),
        q.ll + (q.lr - q.ll) * u,
        q.ll + (q.lr - q.ll) * (1 - u),
    )
    # make an entertaining fill color
    c1 = min(1, max(o, u))
    c3 = min(1, max(1 - u, 1 - o))
    fill = (c1, 0, c3)
    img = page.new_shape()
    img.draw_oval(q1)
    img.finish(
        color=blue,  # blue border
        fill=fill,  # variable fill color
        width=0.3,  # border width
    )
    img.draw_circle(q1.ll, 4)
    img.draw_circle(q1.ul, 4)
    img.finish(fill=red)
    img.draw_circle(q1.ur, 4)
    img.draw_circle(q1.lr, 4)
    img.finish(fill=blue)
    img.commit()
    return page.get_pixmap().tobytes("ppm")  # return a PPM image of the page


# ------------------------------------------------------------------------------
# main program
# ------------------------------------------------------------------------------
png = make_oval(0.0)  # create first picture
img = sg.Image(data=png)  # define form image element
layout = [[img]]  # minimal layout
form = sg.FlexForm(
    "drawOval: left-right points exchange", layout, finalize=True
)  # define form

loop_count = 1  # count the number of loops
t0 = mytime()  # start a timer
i = 0
add = 1

while True:  # loop forever
    event, values = form.Read(timeout=0)
    if event is None:
        break

    png = make_oval(i)  # make next picture
    try:  # guard against form closure
        img.Update(data=png)  # put in new picture
        form.Refresh()  # show updated
    except:
        form.Close()
        break  # user is fed up seeing this

    loop_count += 1  # tally the loops
    i += add  # update the parameter
    if i >= 100:  # loop backwards from here
        add = -1
        continue
    if i <= -100:  # loop forward again
        add = +1
        i = -100

t1 = mytime()
fps = round(loop_count / (t1 - t0), 1)
script = os.path.basename(__file__)
print("'%s' was shown with %g frames per second." % (script, fps))
