"""
PyMuPDF Demo Program

Show how to create a PDF page that display content depending on the state
of a set of optional content groups.

We display the first 4 pages of a source file on 4 quadrant of a new
PDF page of size ISO A4.
The 4 source images are displayed such that only is shown at a time. This is
achieved via so-called "Radio-Button-Groups" of optional content groups.
"""
import pymupdf

# source file with at least 4 pages
src = pymupdf.open("source.pdf")

# new PDF with one page
doc = pymupdf.open()
page = doc.new_page()

# define the 4 rectangle quadrants to receive the source pages
r0 = page.rect / 2
r1 = r0 + (r0.width, 0, r0.width, 0)
r2 = r0 + (0, r0.height, 0, r0.height)
r3 = r2 + (r2.width, 0, r2.width, 0)

# make 4 OCGs - one for each source page image.
xref0 = doc.add_ocg("ocg0", on=True)
xref1 = doc.add_ocg("ocg1", on=False)
xref2 = doc.add_ocg("ocg2", on=False)
xref3 = doc.add_ocg("ocg3", on=False)
doc.set_ocStates(
    -1,  # the default OC configuration
    rbgroups=[[xref0, xref1, xref2, xref3]],  # one radio-button group
)

# insert the 4 source page images, each connected to one OCG
page.show_pdf_page(r0, src, 0, oc=xref0)
page.show_pdf_page(r1, src, 1, oc=xref1)
page.show_pdf_page(r2, src, 2, oc=xref2)
page.show_pdf_page(r3, src, 3, oc=xref3)

doc.save(  # save the file
    __file__.replace(".py", ".pdf"),
    garbage=3,
    pretty=True,
    deflate=True,
    clean=True,
)

# the new file can now be viewed by e.g. Adobe Acrobat reader and
# viewing each page will switch off all other three.
