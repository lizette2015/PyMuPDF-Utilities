"""
Demo skript: Turn Drawings into PNGs
------------------------------------
Walk through the drawings of a page and join path rectangles, which are in
the "neighborhood" of each other. Please see below for a definition.
This potentially results in a smaller set of rectangles, which each cover
a vector graphics figure.

The main function, "detect_rects", can be imported and invoked with a pymupdf.Page
as the only argument. Any document type is supported.
It returns a list of joined rectangles - which for instance can be used as the
"clip" parameter of a Pixmap.

It can be invoked standalone via "python detect_graphics.py input.pdf".
In that case, it iterates over the documents pages and outputs a PNG for each
encountered rectangles.

License & Copyright
-------------------
License AGPL 3.0
Copyright (c) 2021-2024, Jorj McKie
"""

import pymupdf


def detect_rects(page, graphics=None):
    """Detect and join rectangles of neighboring vector graphics."""
    delta = 3

    def are_neighbors(r1, r2):
        """Detect whether r1, r2 are "neighbors".

        Neighbors are defined as:
        The minimum distance between points of r1 and points of r2 is not
        larger than delta.

        This check supports empty rect-likes and thus also lines.
        """
        if (
            (
                r2.x0 - delta <= r1.x0 <= r2.x1 + delta
                or r2.x0 - delta <= r1.x1 <= r2.x1 + delta
            )
            and (
                r2.y0 - delta <= r1.y0 <= r2.y1 + delta
                or r2.y0 - delta <= r1.y1 <= r2.y1 + delta
            )
            or (
                r1.x0 - delta <= r2.x0 <= r1.x1 + delta
                or r1.x0 - delta <= r2.x1 <= r1.x1 + delta
            )
            and (
                r1.y0 - delta <= r2.y0 <= r1.y1 + delta
                or r1.y0 - delta <= r2.y1 <= r1.y1 + delta
            )
        ):
            return True
        return False

    # we exclude graphics not contained in reasonable page margins
    parea = page.rect + (-36, -36, 36, 36)

    if graphics is None:
        graphics = page.get_drawings()
    # exclude graphics not contained inside margins
    paths = [
        p
        for p in page.get_drawings()
        if parea.x0 <= p["rect"].x0 <= p["rect"].x1 <= parea.x1
        and parea.y0 <= p["rect"].y0 <= p["rect"].y1 <= parea.y1
    ]

    # list of all vector graphic rectangles
    prects = sorted([p["rect"] for p in paths], key=lambda r: (r.y1, r.x0))

    new_rects = []  # the final list of the joined rectangles

    # -------------------------------------------------------------------------
    # The strategy is to identify and join all rects that are neighbors
    # -------------------------------------------------------------------------
    while prects:  # the algorithm will empty this list
        r = prects[0]  # first rectangle
        repeat = True
        while repeat:
            repeat = False
            for i in range(len(prects) - 1, 0, -1):  # back to front
                if are_neighbors(prects[i], r):
                    r |= prects[i].tl  # join in to first rect
                    r |= prects[i].br
                    del prects[i]  # delete this rect
                    repeat = True

        prects[0] = +r
        # move first item over to result list
        new_rects.append(prects.pop(0))
        prects = sorted(list(set(prects)), key=lambda r: (r.y1, r.x0))

    new_rects = sorted(list(set(new_rects)), key=lambda r: (r.y1, r.x0))
    return [r for r in new_rects if r.width > 5 and r.height > 5]


if __name__ == "__main__":
    import sys

    doc = pymupdf.open(sys.argv[1])
    for page in doc:
        new_rects = detect_rects(page)
        for i, r in enumerate(new_rects):
            pix = page.get_pixmap(dpi=150, clip=r)
            pix.save("graphic-%03i-%02i.png" % (page.number, i))
