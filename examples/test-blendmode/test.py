"""
Generate highlight annotations using blend modes
-------------------------------------------------------------------------------
License: GNU AFFERO GPL V3
(c) 2020 Jorj X. McKie

Usage
-----
python test.py

Purpose
--------
This utility is an example application of PyMuPDF to demonstrate the
(rather complex) influencing factors background and text colors, opacity and
blend mode for the appearance of an annotation.

For each of the PDF blend modes (as defined in
http://www.adobe.com/content/dam/Adobe/en/devnet/acrobat/pdfs/pdf_reference_1-7.pdf
pages 520+) it generates a highlight annotation which uses it.

Dependencies
------------
PyMuPDF
"""

import os

import pymupdf

print(pymupdf.__doc__)

blend_modes = (
    pymupdf.PDF_BM_ColorBurn,
    pymupdf.PDF_BM_ColorDodge,
    pymupdf.PDF_BM_Darken,
    pymupdf.PDF_BM_Difference,
    pymupdf.PDF_BM_Exclusion,
    pymupdf.PDF_BM_HardLight,
    pymupdf.PDF_BM_Lighten,
    pymupdf.PDF_BM_Multiply,
    pymupdf.PDF_BM_Normal,
    pymupdf.PDF_BM_Overlay,
    pymupdf.PDF_BM_Screen,
    pymupdf.PDF_BM_SoftLight,
    pymupdf.PDF_BM_Hue,
    pymupdf.PDF_BM_Saturation,
    pymupdf.PDF_BM_Color,
    pymupdf.PDF_BM_Luminosity,
)


doc = pymupdf.open()  # new PDF
page = doc.new_page()  # new page
shape = page.new_shape()  # make a page draw area
opacity = 0.3  # all annotation use this opacity
tcol = (0, 0, 1)  # text color
gold = (1, 1, 0)  # highlight color
bg_color = "skyblue3"
background = pymupdf.utils.getColor(bg_color)  # background color
fname = "hebo"  # Helvetica Bold
fsize = 12  # generous font size
tl = page.rect.tl + (150, 100)
br = page.rect.br - (150, 62)
rect = pymupdf.Rect(tl, br)  # only use this area of the page


rects = pymupdf.make_table(  # define a table with 2 cells per blend mode
    rows=len(blend_modes),  # one row per blend mode
    cols=2,  # for the blend mode and its highlighted version
    rect=rect,  # inside this rectangle
)

# paint page background
# will provide better visibility of highlighted text
shape.draw_rect(page.rect)
shape.finish(fill=background, color=background)

# fill the table
for i, bmode in enumerate(blend_modes):
    r = rects[i]  # contains 2 rectangles
    text = "\n" + bmode  # try to center the name a bit
    shape.insert_textbox(  # blend mode name in left rectangle
        r[0],
        text,
        fontsize=fsize,
        color=tcol,
        fontname=fname,
        align=pymupdf.TEXT_ALIGN_CENTER,
    )
    shape.insert_textbox(  # blend mode name in right rectangle
        r[1],
        text,
        fontsize=fsize,
        color=tcol,
        fontname=fname,
        align=pymupdf.TEXT_ALIGN_CENTER,
    )

shape.insert_textbox(
    (80, 36, page.rect.width - 80, 70),
    "Show how blend mode, opacity %g and background\ncolor '%s' affect a highlight annotation"
    % (opacity, bg_color.upper()),
    fontname=fname,
    color=tcol,
    fontsize=fsize,
    align=pymupdf.TEXT_ALIGN_CENTER,
)

shape.commit()  # this commits text and drawings to the page

# Now add highlight annotations for text in the right column.
# To find the respective text, we search for the blend mode name,
# then take its second occurrence for highlighting
for i, bmode in enumerate(blend_modes):
    annot = page.add_highlight_annot(rects[i][1])  # take second one
    annot.update(blend_mode=bmode, opacity=opacity)  # and finish the annotation

doc.ez_save("output.pdf")
