"""
Script showing how to select only text that is contained in a given rectangle
on a page.

We use the page method 'get_text("words")' which delivers a list of all words.
Every item contains the word's rectangle (given by its coordinates, not as a
pymupdf.Rect in this case).
From this list we subselect words positioned in the given rectangle (or at
least intersect).
We sort this sublist by ascending y-ccordinate, and then by ascending x value.
Each original line of the rectangle is then reconstructed using the itertools
'groupby' function.

Remarks
-------
1. The script puts words in the same line, if the y1 value of their bbox are
   *almost* equal. Allowing more tolerance here is imaginable, e.g. by
   taking the pymupdf.IRect of the word rectangles instead.

2. Reconstructed lines will contain words with exactly one space between them.
   So any original multiple spaces will be lost.

3. Depending on your requirements, you can get away without any special script
   by using features new in version 1.17.7. They work on a by-character level,
   meaning they cut away parts of a word where necessary. On the other hand
   they are extremely simple to use: Page.get_textbox(rect), or
   Page.get_text("text", clip=rect), etc. is all you need.
"""
import pymupdf


def make_text(words):
    """Return textstring output of get_text("words").

    Word items are sorted for reading sequence left to right,
    top to bottom.
    """
    line_dict = {}  # key: vertical coordinate, value: list of words
    words.sort(key=lambda w: w[0])  # sort by horizontal coordinate
    for w in words:  # fill the line dictionary
        y1 = round(w[3], 1)  # bottom of a word: don't be too picky!
        word = w[4]  # the text of the word
        line = line_dict.get(y1, [])  # read current line content
        line.append(word)  # append new word
        line_dict[y1] = line  # write back to dict
    lines = list(line_dict.items())
    lines.sort()  # sort vertically
    return "\n".join([" ".join(line[1]) for line in lines])


doc = pymupdf.open("search.pdf")  # any supported document type
page = doc[0]  # we want text from this page

"""
-------------------------------------------------------------------------------
Identify the rectangle.
-------------------------------------------------------------------------------
"""
rect = page.first_annot.rect  # this annot has been prepared for us!
# Now we have the rectangle ---------------------------------------------------

"""
Get all words on page in a list of lists. Each word is represented by:
[x0, y0, x1, y1, word, bno, lno, wno]
The first 4 entries are the word's rectangle coordinates, the last 3 are just
technical info (block number, line number, word number).
The term 'word' here stands for any string without space.
"""

words = page.get_text("words")  # list of words on page

"""
We will subselect from this list, demonstrating two alternatives:
(1) only words inside above rectangle
(2) only words insertecting the rectangle

The resulting sublist is then converted to a string by calling above funtion.
"""

# ----------------------------------------------------------------------------
# Case 1: select the words *fully contained* in the rect
# ----------------------------------------------------------------------------
mywords = [w for w in words if pymupdf.Rect(w[:4]) in rect]

print("Select the words strictly contained in rectangle")
print("------------------------------------------------")
print(make_text(mywords))

# ----------------------------------------------------------------------------
# Case 2: select the words *intersecting* the rect
# ----------------------------------------------------------------------------
mywords = [w for w in words if pymupdf.Rect(w[:4]).intersects(rect)]

print("\nSelect the words intersecting the rectangle")
print("-------------------------------------------")
print(make_text(mywords))
