"""
Split a PDF document into multiple pages (1 per page)
--------------------------------------------------------------------------------
License: GNU GPL V3
(c) 2022 Jorj X. McKie

Usage
-----
python split.py input.pdf
"""

import sys
import pymupdf

fn = sys.argv[1]
fn1 = fn[:-4]
src = pymupdf.open(fn)
for i in range(len(src)):
    doc = pymupdf.open()
    doc.insert_pdf(src, from_page=i, to_page=i)
    doc.save("./output/%s-%i.pdf" % (fn1, i))
    doc.close()
