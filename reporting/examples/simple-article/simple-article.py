import pathlib
import pymupdf
from Reports import *

report = Report(mediabox=pymupdf.paper_rect("a4-l"))

HTML = pathlib.Path("springer.html").read_bytes().decode()
textblock = Block(html=HTML, report=report)

report.sections = [[textblock, Options(cols=2, format=report.mediabox, newpage=True)]]
report.run("output.pdf")
