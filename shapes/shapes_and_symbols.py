import pymupdf
from pymupdf.utils import getColor
"""
-------------------------------------------------------------------------------
Created on Fri Nov 10 07:00:00 2017

@author: Jorj McKie
Copyright (c) 2017-2018 Jorj X. McKie

The license of this program is governed by the GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007. See the "COPYING" file of the PyMuPDF repository.
-------------------------------------------------------------------------------
Contains signs and symbols created with PyMuPDF's image creation features.
The intention is to facilitate the use of these features by providing functions
that create ready-made symbols. We strive to increase the function set from
time to time.

To include a function in your Python script, import it like so:

from shapes_and_symbols import smiley

then use this function anywhere in your script.

Using a function
----------------

smiley(img, rect, ...)

Allmost all functions have the same first and second parameter:

img    - pymupdf.Shape object created by p.new_shape()
rect   - pymupdf.Rect object. This is the area in which the image should appear.

Other parameters are function-specific, but always include a "morph" argument.
This can be used to change the image's appearance in an almost arbitrary way:
rotation, shearing, mirroring. For this you must provide a pymupdf.Point and a
pymupdf.Matrix object. See PyMuPDF documentation, chapter "Shape".

-------------------------------------------------------------------------------
Available functions
-------------------

dontenter - traffic sign Do Not Enter
heart     - heart
clover    - 4 leaved clover
diamond   - rhombus
caro      - one of the 4 card game colors
arrow     - a triangle
hand      - a hand symbol, similar to internet
pencil    - a pencil (eye catcher)
smiley    - emoji
frowney   - emoji
-------------------------------------------------------------------------------

Dependencies
------------
PyMuPDF
-------------------------------------------------------------------------------
"""
# =============================================================================
# Do Not Enter
# =============================================================================
def dontenter(img, r, morph = None):
    """Draw the "Do Not Enter" traffic symbol.
    """
    red = getColor("red3")
    white = (1,1,1)
    img.draw_oval(r)               # draw red circle w/ thick white border
    img.finish(fill = red, color = white, width = r.width * 0.04)
    img.draw_oval(r)               # draw empty circle, thin black border
    img.finish(width = r.width * 0.001)
    deltah = r.width * 0.13
    deltav = r.height * 0.45
    rs = r + (deltah, deltav, -deltah, -deltav)
    img.draw_rect(rs)              # draw white horizontal rectangle
    img.finish(color = white, fill = white, width = r.width * 0.06,
               roundCap = False, morph = morph)
    return

# =============================================================================
# Heart
# =============================================================================
def heart(img, r, col = (1,0,0), morph = None):
    """Draw a heart image inside a rectangle.
    """
    mtop = r.tl + (r.tr - r.tl) * 0.5
    mbot = r.bl + (r.br - r.bl) * 0.5
    htop = mtop + (mbot - mtop)*0.3     # top point where arcs meet
    hbot = mtop + (mbot - mtop)*0.8     # bottom point joining arcs
    # left and right ctrl points, symmetrical.
    pl1  = r.tl + (r.tr - r.tl) * 0.25
    pr1  = r.tr - (r.tr - r.tl) * 0.25
    pl2  = r.tl + (r.bl - r.tl) * 0.40
    pr2  = r.tr + (r.br - r.tr) * 0.40
    # we have defined all 6 points and now draw 2 Bezier curves
    img.draw_bezier(htop, pl1, pl2, hbot)
    img.draw_bezier(htop, pr1, pr2, hbot)
    img.finish(color = col, fill = col, closePath = True, morph = morph)

# =============================================================================
# Clover leaf
# =============================================================================
def clover(img, r, col = (0,1,0), morph = None):
    """Draw a 4-leaf clover image inside a rectangle.
    """
    # this is made of 4 Bezier curves, each starting and ending in the
    # rect's middle point M
    M = r.tl + (r.br - r.tl) * 0.5
    img.draw_bezier(M, r.tl, r.tr, M)
    img.draw_bezier(M, r.tr, r.br, M)
    img.draw_bezier(M, r.bl, r.tl, M)
    img.draw_bezier(M, r.br, r.bl, M)
    img.finish(color = col, fill = col, width = 0.3, morph = morph)

# =============================================================================
# Diamond
# =============================================================================
def diamond(img, r, col = (1,0,0), morph = None):
    """Draw a rhombus in a rectangle.
    """
    white = (1,1,1)
    mto = r.tl + (r.tr - r.tl) * 0.5
    mri = r.tr + (r.br - r.tr) * 0.5
    mbo = r.bl + (r.br - r.bl) * 0.5
    mle = r.tl + (r.bl - r.tl) * 0.5
    img.draw_polyline((mto, mri, mbo, mle))
    img.finish(color = white, fill = col, closePath = True, morph = morph)

# =============================================================================
# Caro (card game color)
# =============================================================================
def caro(img, r, col = (1,0,0), morph = None):
    """Draw a caro symbol in a rectangle.
    """
    white = (1,1,1)
    mto = r.tl + (r.tr - r.tl) * 0.5
    mri = r.tr + (r.br - r.tr) * 0.5
    mbo = r.bl + (r.br - r.bl) * 0.5
    mle = r.tl + (r.bl - r.tl) * 0.5
    M = r.tl + (r.br - r.tl) * 0.5
    img.draw_curve(mle, M, mto)
    img.draw_curve(mto, M, mri)
    img.draw_curve(mri, M, mbo)
    img.draw_curve(mbo, M, mle)
    img.finish(color = white, fill = col, morph = morph)

# =============================================================================
# Arrow
# =============================================================================
def arrow(img, r, fill = None, color = None, morph = None):
    """Draw a triangle symbol in a rectangle. Last parameter indicates direction
    the arrow points to: either as a number or as first letter of east(0), south(1),
    west(3), north(4).
    """
    if color is None:
        stroke = (1,1,1)
    else:
        stroke = color
    if fill is None:
        col = (1,0,0)
    else:
        col = fill
    p1 = r.tl
    p2 = r.bl
    p3 = r.tr + (r.br - r.tr) * 0.5
    img.draw_polyline((p1, p2, p3))
    img.finish(color = stroke, fill = col, closePath = True, morph = morph)

# =============================================================================
# Hand
# =============================================================================
def hand(img, r, color = None, fill = None, morph = None):
    """Put a hand symbol inside a rectangle on a PDF page. Parameters:
    img - an object of the Shape class (contains relevant page information)
    rect - a rectangle. Its width must be at least 30% larger than its height.
    color, fill - color triples for border and filling (optional).
    morph - morphing parameters (point, matrix)
    """
    if r.width >= r.height * 1.25:
        w = r.height * 1.25
        h = r.height
    else:
        w = r.width
        h = w / 1.25

    x0 = r.x0 + (r.width - w) * 0.5
    y0 = r.y0 + (r.height - h) * 0.5
    rect = pymupdf.Rect(x0, y0, x0 + w, y0 + h)

    if not color:
        line = getColor("orange")
    else:
        line = color
    if not fill:
        skin = getColor("burlywood1")
    else:
        skin = fill
    #--------------------------------------------------------------------------
    # Define control points for the symbol, relative to a rect height of 3.
    # This is the actual brainware of the whole thing ...
    #--------------------------------------------------------------------------
    points = ((0.0, 1.4), (1.4, 0.2), (1.4, 1.4), (2.2, 0.0), (1.4, 1.4),
              (3.4, 1.4), (3.4, 1.8), (2.8, 1.8), (2.8, 2.2), (2.6, 2.2),
              (2.6, 2.6), (2.5, 2.6), (2.5, 3.0),
             )
    # rescale points to the argument rectangle.
    f = rect.height / 3
    tl = rect.tl                           # need this as displacement
    # function for rescaling the points in the list
    rescale = lambda x: pymupdf.Point(points[x])*f + tl
    p1  = rescale(0)
    p2  = rescale(1)
    p3  = rescale(2)
    p4  = rescale(3)
    p5  = rescale(4)
    p6  = rescale(5)
    p7  = rescale(6)
    p8  = rescale(7)
    p9  = rescale(8)
    p10 = rescale(9)
    p11 = rescale(10)
    p12 = rescale(11)
    p13 = rescale(12)

    # some additional helper points for Bezier curves of the finger tips.
    d1 = pymupdf.Point(0.4, 0) *f
    d7 = p7 - pymupdf.Point(1.2, 0) * f
    d9 = pymupdf.Point(d7.x, p9.y)
    d11 = pymupdf.Point(d7.x, p11.y)
    # now draw everything
    # IMPORTANT: the end point of each draw method must equal the start point
    # of the next one in order to create one connected path. Only then the
    # "finish" parameters will apply to all individual draws.
    img.draw_curve(p1, p3, p2)
    img.draw_curve(p2, p4, p5)
    img.draw_line(p5, p6)
    img.draw_bezier(p6, p6 + d1, p7 + d1, p7)
    img.draw_line(p7, d7)
    img.draw_line(d7, p8)
    img.draw_bezier(p8, p8 + d1, p9 + d1, p9)
    img.draw_line(p9, d9)
    img.draw_line(d9, p10)
    img.draw_bezier(p10, p10 + d1, p11 + d1, p11)
    img.draw_line(p11, d11)
    img.draw_line(d11, p12)
    img.draw_bezier(p12, p12 + d1, p13 + d1, p13)
    img.draw_line(p13, rect.bl)
    img.finish(color = line, fill = skin, closePath = False, morph = morph)
    return

# =============================================================================
# Pencil
# =============================================================================
def pencil(img, rect, right=True, morph=None):
    """Place a fitting *pencil* symbol in a rectangle.
    :arg img: Shape object of a PDF page
    :arg rect: rect-like to contain the symbol
    :arg right: bool, whether pencil point right (default) or left
    :arg morph: whether to morph the result
    The pencil tip will be the middle of the left or right rectangle side.
    Pencil length will be 3.45 of pencil thickness (height), where the height
    will be chosen to not exceed rectangle height.
    """
    if not right:
        tip = rect.tl + (rect.bl - rect.tl) * 0.5
    else:
        tip = rect.tr + (rect.br - rect.tr) * 0.5
    pb_height = min(rect.width / 3.45, rect.height)
    _pencil(img, tip, pb_height, not right, morph)
    return None

def _pencil(img, penciltip, pb_height, left=True, morph = None):
    """Draw a pencil image. Parameters:
    img       -  Shape object
    penciltip - pymupdf.Point, coordinates of the pencil tip
    pb_height - the thickness of the pencil. This controls the dimension of the
                picture: it will be contained in a rectangle of 100 x 345 pixels
                if this parameter is 100.
    left      - bool, indicates whether the pencil points left (True) or right.
    morph     - a tuple (point, matrix) to achieve image torsion.
    """
    from pymupdf.utils import getColor
    from functools import partial
    # define some colors
    yellow  = getColor("darkgoldenrod")
    black   = getColor("black")
    white   = getColor("white")
    red     = getColor("red")
    wood    = getColor("wheat2")
    wood2   = getColor("wheat3")
    #---------------------------------------------------------------------------
    # some adjustments depending on whether pencil tip is left or right:
    # for choosing between a left point (lp) or a right point (rb),
    # we specify oneof(lp, rp), delivering either lp or rp. Likewise,
    # variable 's' is used as a sign and is either +1 or -1.
    #---------------------------------------------------------------------------
    w = pb_height * 0.005                         # standard line thickness
    pb_width  = 2 * pb_height                    # pencil body width
    myfinish = partial(img.finish, width = w, morph = morph, closePath = False)
    oneof = lambda l, r: l if left else r        # choose an alternative
    s = oneof(1,-1)
    tipendtop = penciltip + pymupdf.Point(s, -0.5) * pb_height
    tipendbot = penciltip + pymupdf.Point(s, 0.5) * pb_height
    r = pymupdf.Rect(tipendtop,
                  tipendbot + (pb_width * s, 0)) # pencil body
    r.normalize()                                # force r to be finite
    # topline / botline indicate the pencil edges
    topline0  = pymupdf.Point(r.x0 + r.width*0.1,
                           r.y0 + pb_height/5.)  # upper pencil edge - left
    topline1  = pymupdf.Point(r.x0 + r.width*0.9,
                           topline0.y)           # upper epncil edge - right
    botline0  = pymupdf.Point(r.x0 + r.width*0.1,
                           r.y1 - pb_height/5.)  # lower pencil edge - left
    botline1  = pymupdf.Point(r.x0 + r.width*0.9,
                           botline0.y)           # lower pencil edge - right

    # control point 1 for pencil rubber
    hp1 = oneof(r.tr, r.tl) + (pb_height*0.6*s, 0)
    # control point 2 for pencil rubber
    hp2 = oneof(r.br, r.bl) + (pb_height*0.6*s, 0)
    # pencil body is some type of yellow
    img.draw_rect(r)
    myfinish(fill = yellow, color = wood)
    img.draw_polyline((r.tl, topline0, botline0, r.bl))
    img.draw_polyline((r.tr, topline1, botline1, r.br))
    myfinish(fill = wood, color = wood)
    # draw pencil edge lines
    img.draw_line(topline0, topline1)
    img.draw_line(botline0, botline1)
    myfinish(color = wood2)

    #===========================================================================
    # black rectangle near pencil rubber
    #===========================================================================
    blackrect = pymupdf.Rect(oneof((r.tr - (pb_height/2., 0)), r.tl),
                          oneof(r.br, (r.bl + (pb_height/2., 0))))
    img.draw_rect(blackrect)
    myfinish(fill = black)

    #===========================================================================
    # draw the pencil rubber
    #===========================================================================
    img.draw_bezier(oneof(r.tr, r.tl), hp1, hp2, oneof(r.br, r.bl))
    myfinish(fill = red)

    #===========================================================================
    # draw pencil tip and curves indicating pencil sharpening traces
    #===========================================================================
    img.draw_polyline((tipendtop, penciltip, tipendbot))
    myfinish(fill = wood)                   # pencil tip
    p1 = tipendtop                          # either left or right
    p2 = oneof(topline0, topline1)
    p3 = oneof(botline0, botline1)
    p4 = tipendbot
    p0 = -pymupdf.Point(pb_height/5., 0)*s     # horiz. displacment of ctrl points
    cp1 = p1 + (p2-p1)*0.5 + p0             # ctrl point upper rounding
    cp2 = p2 + (p3-p2)*0.5 + p0*2.9         # ctrl point middle rounding
    cp3 = p3 + (p4-p3)*0.5 + p0             # ctrl point lower rounding
    img.draw_curve(p1, cp1, p2)
    myfinish(fill = yellow, color=yellow, closePath = True)
    img.draw_curve(p2, cp2, p3)
    myfinish(fill = yellow, color=yellow, closePath = True)
    img.draw_curve(p3, cp3, p4)
    myfinish(fill = yellow, color=yellow, closePath = True)

    #===========================================================================
    # draw the pencil tip lead
    #===========================================================================
    img.draw_polyline((penciltip + (tipendtop - penciltip)*0.4,
                      penciltip,
                      penciltip + (tipendbot - penciltip)*0.4))
    #===========================================================================
    # add a curve to indicate lead is round
    #===========================================================================
    img.draw_curve(penciltip + (tipendtop - penciltip)*0.4,
                  penciltip + (pb_height * 0.6 * s, 0),
                  penciltip + (tipendbot - penciltip)*0.4)
    myfinish(fill = black)

    #===========================================================================
    # re-border pencil body to get rid of some pesky pixels
    #===========================================================================
    img.draw_polyline((p1, p2, p3, p4))
    myfinish(color = yellow)
    br_tl = oneof(blackrect.tl, blackrect.tr)
    br_bl = oneof(blackrect.bl, blackrect.br)
    img.draw_polyline((br_tl, tipendtop, penciltip, tipendbot, br_bl))
    myfinish()
    #===========================================================================
    # draw pencil label - first a rounded rectangle
    #===========================================================================
    p1 = pymupdf.Point(0.65, 0.15) * pb_height
    p2 = pymupdf.Point(0.45, 0.15) * pb_height
    lblrect = pymupdf.Rect(topline0 + oneof(p1, p2),
                        botline1 - oneof(p2, p1))
    img.draw_rect(lblrect)
    img.draw_curve(lblrect.tr,
                   pymupdf.Point(lblrect.x1+pb_height/4., penciltip.y),
                   lblrect.br)
    img.draw_curve(lblrect.tl,
                   pymupdf.Point(lblrect.x0-pb_height/4., penciltip.y),
                   lblrect.bl)
    myfinish(fill = black)

    #===========================================================================
    # finally the white vertical stripes - whatever they are good for
    #===========================================================================
    p1t = blackrect.tl + (blackrect.width/3.,   pb_height/20.)
    p1b = blackrect.bl + (blackrect.width/3.,   -pb_height/20.)
    p2t = blackrect.tl + (blackrect.width*2/3., pb_height/20.)
    p2b = blackrect.bl + (blackrect.width*2/3., -pb_height/20.)
    img.draw_line(p1t, p1b)
    img.draw_line(p2t, p2b)
    img.finish(color = white, width = pb_height*0.08, roundCap = False,
               morph = morph)

    # insert text to indicate a medium lead grade
    if img.insert_textbox(lblrect, "HB", color = white, morph = morph,
                          fontsize = pb_height * 0.22, align = 1) < 0:
        raise ValueError("not enough space to store 'HB' text")
    return

# =============================================================================
# Smiley emoji
# =============================================================================
def smiley(img, rect, color = (0,0,0), fill = (1,1,0), morph = None):
    dx = rect.width * 0.2
    dy = rect.height * 0.25
    w = rect.width * 0.01
    img.draw_oval(rect)                      # draw face
    img.finish(fill = fill, width = w, morph = morph)
    # calculate rectangles containing the eyes
    rl = pymupdf.Rect(rect.tl + (dx, dy),
                   rect.tl + (2 * dx, 2 * dy))
    rr = pymupdf.Rect(rect.tr + (-2 * dx, dy),
                   rect.tr + (-dx, 2 * dy))
    img.draw_oval(rl)                        # draw left eye
    img.draw_oval(rr)                        # draw right eye
    img.finish(fill = color, morph = morph)
    p0 = rl.bl + (0, 0.75 * dy)             # left corner of mouth
    p1 = rr.br + (0, 0.75 * dy)             # right corner of mouth
    c  = rect.bl + (rect.br - rect.bl)*0.5
    img.draw_curve(p0, c, p1)                # draw mouth
    img.finish(width = 4 * w, closePath = False, morph = morph)

# =============================================================================
# Frowney emoji
# =============================================================================
def frowney(img, rect, color = (0,0,0), fill = (1,1,0), morph = None):
    dx = rect.width * 0.2
    dy = rect.height * 0.25
    w = rect.width * 0.01
    img.draw_oval(rect)                      # draw face
    img.finish(fill = fill, width = w, morph = morph)
    # calculate rectangles containing the eyes
    rl = pymupdf.Rect(rect.tl + (dx, dy),
                   rect.tl + (2 * dx, 2 * dy))
    rr = pymupdf.Rect(rect.tr + (-2 * dx, dy),
                   rect.tr + (-dx, 2 * dy))
    img.draw_oval(rl)                        # draw left eye
    img.draw_oval(rr)                        # draw right eye
    img.finish(fill = color, morph = morph)
    p0 = rl.bl + (0, dy)                    # left corner of mouth
    p1 = rr.br + (0, dy)                    # right corner of mouth
    c  = rl.bl + (rr.br - rl.bl)*0.5
    img.draw_curve(p0, c, p1)                # draw mouth
    img.finish(width = 4 * w, closePath = False, morph = morph)

"""
------------------------------------------------------------------------------
 Main program: Create a PDF with one symbol per page.
------------------------------------------------------------------------------
Each page size is chosen to closely surround the symbol.

A page can be used as input to e.g. method showPDFpage in another PDF to
include the symbol at a convenient place.

Another option would be to output the symbol page in SVG format via method
getSVGimage(matrix = ...).
"""
if __name__ == "__main__":
    green = getColor("limegreen")
    red = getColor("red2")
    doc = pymupdf.open()
    p = doc.new_page()
    img = p.new_shape()
    r = pymupdf.Rect(100, 100, 200, 200)
    heart(img, r, red)
    img.commit()
    p.set_cropbox(r + (10, 10, -10, -15))

    p = doc.new_page()
    img = p.new_shape()
    pnt = r.tl + (r.br - r.tl)*0.5
    clover(img, r, green, morph = (pnt, pymupdf.Matrix(45)))
    img.commit()
    p.set_cropbox(r + (5, 5, -5, -5))

    p = doc.new_page()
    img = p.new_shape()
    diamond(img, r, red)
    img.commit()
    p.set_cropbox(r)

    p = doc.new_page()
    img = p.new_shape()
    pnt = r.tl + (r.br - r.tl)*0.5
    caro(img, r, red, morph = (pnt, pymupdf.Matrix(45)))
    img.commit()
    p.set_cropbox(r + (10, 10, -10, -10))

    p = doc.new_page()
    img = p.new_shape()
    pnt = r.tl + (r.br - r.tl)*0.5
    arrow(img, r, fill=red, morph = (pnt, pymupdf.Matrix(1,1)))
    img.commit()
    p.set_cropbox(r)

    p = doc.new_page()
    img = p.new_shape()
    dontenter(img, r, morph = None)
    img.commit()
    p.set_cropbox(r + (-5, -5, 5, 5))

    p = doc.new_page()
    img = p.new_shape()
    rh = r + (0, 120, 30, 120)
    hand(img, rh, morph = None)
    cropbox = +img.rect + (0, 0, 0, 5)
    img.commit()
    p.set_cropbox(cropbox)

    p = doc.new_page()
    img = p.new_shape()
    smiley(img, r, morph = None)
    cropbox = +img.rect + (-5, -5, 5, 5)
    img.commit()
    p.set_cropbox(cropbox)

    p = doc.new_page()
    img = p.new_shape()
    frowney(img, r, morph = None)
    cropbox = +img.rect + (-5, -5, 5, 5)
    img.commit()
    p.set_cropbox(cropbox)

    # create first pencil page (tip left)
    p = doc.new_page()
    img = p.new_shape()
    pencil(img, p.rect, True)
    cropbox = +img.rect + (0, -5, 0, +5)
    img.commit()
    p.set_cropbox(cropbox)

    # create second pencil page (tip right)
    p = doc.new_page()
    img = p.new_shape()
    pencil(img, p.rect, False)
    cropbox = +img.rect + (0, -5, 0, +5)
    img.commit()
    p.set_cropbox(cropbox)

    m = {'title': "Shapes and Symbols",
         'author': "Jorj X. McKie",
         'subject': "Create various symbols for use with e.g. showPDFpage()",
         'keywords': "symbols, shapes, signs",
         'creator': "shapes_and_symbols.py",
         'producer': "PyMuPDF",
         'creationDate': pymupdf.get_pdf_now(),
         'modDate': pymupdf.get_pdf_now()}
    doc.set_metadata(m)
    import os
    scriptdir = os.path.dirname(__file__)
    print(scriptdir)
    doc.save(os.path.join(scriptdir, "symbols.pdf"), garbage = 3, deflate= True)
