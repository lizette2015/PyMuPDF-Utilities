# written by Green

import io
import pymupdf
import sys
from pprint import pprint


class Block:
    def __init__(self, report, html=None, archive=None, css=None, story=None):
        self.html = html
        self.report = report
        self.archive = self.report.archive
        if archive is not None:
            self.archive.add(archive)

        self.css = css if css else ""
        if self.report.css is not None:  # prepend CSS of owning report
            self.css = self.report.css + self.css

        self.story = story
        self.reset = True  # this building must be reset each time
        self.advance = True

    def make_story(self):
        if not isinstance(self.story, pymupdf.Story):
            self.story = pymupdf.Story(self.html, user_css=self.css, archive=self.archive)


class ImageBlock:
    def __init__(
        self,
        report,
        url=None,
        archive=None,
        css=None,
        story=None,
        width=None,
        height=None,
    ):
        w, h = width, height
        if w is None and h is None:
            self.html = f'<img src="{url}" width=100 height=100/>'
        elif w is None:
            self.html = f'<img src="{url}" height={height}/>'
        elif h is None:
            self.html = f'<img src="{url}" width={width}/>'
        else:
            self.html = f'<img src="{url}" width={width} height={height}/>'

        self.archive = pymupdf.Archive(".") if archive is None else archive
        self.story = story
        self.report = report
        self.advance = True
        self.css = css if css else ""
        if self.report.css is not None:  # prepend CSS of owning report
            self.css = self.report.css + self.css

    def make_story(self):
        if not isinstance(self.story, pymupdf.Story):
            self.story = pymupdf.Story(self.html, user_css=self.css, archive=self.archive)


class Options:
    def __init__(self, cols=0, format=None, newpage=None):
        self.cols = cols
        self.format = format
        self.newpage = newpage


class Size:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height


class Table:
    def __init__(
        self,
        report,
        html=None,
        story=None,
        fetch_rows=None,
        top_row=None,
        last_row_bg=None,
        archive=None,
        css=None,
        alternating_bg=None,
    ):
        self.report = report
        self.html = html
        self.story = story
        self.top_row = top_row
        self.advance = True

        # prepend archive of owning report
        self.archive = self.report.archive
        if archive is not None:
            self.archive.add(archive)

        self.css = css if css else ""
        if self.report.css is not None:  # prepend CSS of owning report
            self.css = self.report.css + self.css

        self.fetch_rows = fetch_rows
        self.HEADER_RECTS = []  # rect area of header
        self.HEADER_RECT = None  # the rectangle wrapping the top row
        self.HEADER_LAST_COL_RECT = None  # the rectangle of last column in top row
        self.HEADER_BLOCKS = None
        self.HEADER_FONT = None
        self.HEADER_PATHS = None
        self.header_tops = []  # list where.y0 coordinates
        self.reset = False  # this building must not be reset
        self.alternating_bg = alternating_bg
        self.last_row_bg = last_row_bg

    def extract_header(self, story):
        """Extract top row from table for later reproduction."""

        def recorder(pos):
            """small recorder function for determining the top row rectangle."""
            if pos.depth == 2:  # select column in template
                self.HEADER_LAST_COL_RECT = pymupdf.Rect(pos.rect)

            if pos.open_close != 2:  # only look at "close"
                return
            if pos.id != pos.header:  # only look at 'id' of top row
                return
            self.HEADER_RECT = pymupdf.Rect(pos.rect)  # found:store header rect

        # write first occurrence of table to find header information
        fp = io.BytesIO()  # for memory PDF
        writer = pymupdf.DocumentWriter(fp)
        story.reset()

        dev = writer.begin_page(self.report.mediabox)

        # customize for multi columns
        columns = self.report.cols  # get columns from parent report

        if columns > 1:  # n columns
            CELLS = self.report.cal_cells(self.report.where, columns)
            CELLS.reverse()
        else:
            CELLS = [self.report.where]

        for CELL in CELLS:
            _, _ = story.place(CELL)
            story.element_positions(
                recorder, {"page": 0, "header": self.top_row}
            )  # get rectangle of top row
            self.HEADER_RECTS.append(self.HEADER_RECT)

        if (
            self.HEADER_LAST_COL_RECT != None
            and self.HEADER_LAST_COL_RECT.x1 > self.HEADER_RECT.x1
        ):  # check last column is over top row
            raise ValueError("Not enough to place it in {0} columns".format(columns))

        story.draw(dev)
        writer.end_page()
        writer.close()

        # re-open temp PDF and load page 0
        doc = pymupdf.open("pdf", fp)
        page = doc[0]
        paths = [
            p for p in page.get_drawings() if p["rect"].intersects(self.HEADER_RECT)
        ]
        blocks = page.get_text(
            "dict", clip=self.HEADER_RECT, flags=pymupdf.TEXTFLAGS_TEXT
        )["blocks"]
        if blocks:  # extract the font name for text in the header
            self.HEADER_FONT = page.get_fonts()[0][3]
        doc.close()
        story.reset()
        # self.HEADER_RECTS = +self.HEADER_RECT
        self.HEADER_RECTS.reverse()
        self.HEADER_RECT = None
        self.HEADER_BLOCKS = blocks
        self.HEADER_PATHS = paths
        return

    def make_story(self):
        story = pymupdf.Story(self.html, user_css=self.css, archive=self.archive)
        body = story.body
        table = body.find("table", None, None)
        if table is None:
            raise ValueError("no table found in the HTML")

        templ = body.find(None, "id", "template")  # locate template row
        if templ is None and self.fetch_rows is not None:
            raise ValueError("cannot find required 'template' row")

        rows = []
        if hasattr(self.fetch_rows, "__getitem__"):
            rows = self.fetch_rows
        elif hasattr(self.fetch_rows, "__next__"):
            rows = [r for r in self.fetch_rows]
        elif callable(self.fetch_rows):
            func = self.fetch_rows()
            if hasattr(func, "__getitem__"):
                rows = func
            elif hasattr(func, "__next__"):
                rows = [r for r in func]
            else:
                raise ValueError("bad type 'fetch_rows'")

        if rows and not len(rows) > 1:
            raise ValueError("row count must be 2 or more")

        fields = rows[0]  # first row must contain header field id's
        rows = rows[1:]  # row data

        for j, data in enumerate(rows):
            row = templ.clone()  # clone model row
            if self.alternating_bg != None and len(self.alternating_bg) >= 2:
                bg_color = self.alternating_bg[j % len(self.alternating_bg)]
                row.set_properties(bgcolor=bg_color)
            else:
                bg_color = "#fff"  # ensure there always is a background color
            if self.last_row_bg and j == len(rows) - 1:
                bg_color = self.last_row_bg
            for i in range(len(data)):
                text = str(data[i]).replace("\\n", "\n").replace("<br>", "\n")
                tag = row.find(None, "id", fields[i])
                if tag is None:
                    raise ValueError(f"id '{fields[i]}' not in template row.")
                if bg_color:
                    tag.set_properties(bgcolor=bg_color)
                if text.startswith("|img|"):
                    _ = tag.add_image(text[5:])
                else:
                    _ = tag.add_text(text)
            table.append_child(row)

        if templ:
            templ.remove()

        if not isinstance(self.story, pymupdf.Story):
            self.story = story

        if self.top_row != None:
            self.extract_header(story=story)

    def repeat_header(self, page, rect, font_dict):
        """Recreate the top row header of the table on given page, rectangle"""

        def make_fontname(page, font, font_dict):
            xref, refname, pno = font_dict[font]
            if pno == page.number:
                return refname
            font_items = page.get_fonts()
            refnames = [item[4] for item in font_items if item[3] == font]
            if refnames != []:
                return refnames[0]
            refnames = [item[4] for item in font_items]
            i = 1
            fontname = "F1"
            while fontname in refnames:
                i += 1
                fontname = f"F{i}"
            font_ex = page.parent.extract_font(xref)
            font_buff = font_ex[-1]
            page.insert_font(fontname=fontname, fontbuffer=font_buff)
            return fontname

        mat = self.HEADER_RECTS[0].torect(rect)

        for p in self.HEADER_PATHS:
            for item in p["items"]:
                if item[0] == "l":
                    page.draw_line(item[1] * mat, item[2] * mat, color=p["color"])
                elif item[0] == "re":
                    page.draw_rect(item[1] * mat, color=p["color"], fill=p["fill"])

        fontname = make_fontname(page, self.HEADER_FONT, font_dict)
        for block in self.HEADER_BLOCKS:
            for line in block["lines"]:
                for span in line["spans"]:
                    point = pymupdf.Point(span["origin"]) * mat
                    page.insert_text(
                        point, span["text"], fontname=fontname, fontsize=span["size"]
                    )


class Report:
    def __init__(
        self,
        mediabox,
        margins=None,
        logo=None,
        columns=1,
        header=None,
        footer=None,
        css=None,
        archive=None,
        font_families=None,
    ):
        self.mediabox = mediabox
        self.margins = margins
        if self.margins is None:
            self.margins = (36, 36, 36, 30)

        self.columns = columns  # column number, 2 as default
        self.sections = []  # sections list

        self.header = header
        if self.header is None:
            self.header = []

        self.footer = footer
        if self.footer is None:
            self.footer = []

        self.sindex = 0
        self.cols = columns
        self.archive = pymupdf.Archive(".") if archive is None else archive
        self.header_rect = None
        self.footer_rect = None
        self.default_option = Options(cols=1, format=mediabox, newpage=True)

        self.css = css if css else ""

        self.where = self.set_margin(self.mediabox)

        if isinstance(logo, str):
            self.logo_file = logo
            self.logo_rect = pymupdf.Rect(
                self.where.tl, self.where.x0 + 100, self.where.y0 + 100
            )
        else:
            self.logo_file = None

        if font_families:
            for family, pymupdf_code in font_families.items():
                temp = [
                    k
                    for k in pymupdf.pymupdf_fontdescriptors.keys()
                    if k.startswith(pymupdf_code)
                ]
                if temp == []:
                    print(
                        f"'{pymupdf_code}' not in pymupdf-fonts - ignored",
                        file=sys.stderr,
                    )
                    continue
                self.css = pymupdf.css_for_pymupdf_font(
                    pymupdf_code, CSS=self.css, archive=self.archive, name=family
                )

    def set_margin(self, rect):  # set margin with rect provided
        L, T, R, B = self.margins
        return rect + (L, T, -R, -B)

    def current_story(self):  # get current story to draw
        ret = self.sections[self.sindex]
        return ret[0] if isinstance(ret, (list, tuple)) else ret

    def check_cols(self):  # set current columns and determin if going new page or not
        _newpage = self.default_option.newpage
        if isinstance(self.get_current_section(), list):
            if (
                len(self.get_current_section()) != 2
                or self.sections[self.sindex][1].cols == 0
            ):
                self.cols = self.default_option.cols
                return _newpage

            self.cols = int(self.sections[self.sindex][1].cols)
            _newpage = self.sections[self.sindex][1].newpage

        return _newpage

    def get_pagerect(self):  # get current page mediabox
        if isinstance(self.sections[self.sindex], list):  # if section has info
            if (
                len(self.sections[self.sindex]) != 2
                or self.sections[self.sindex][1].format is None
            ):  # don't have property
                return pymupdf.Rect(
                    0.0,
                    0.0,
                    self.default_option.format.width,
                    self.default_option.format.height,
                )

            if isinstance(self.sections[self.sindex][1].format, str):
                return pymupdf.paper_rect(self.sections[self.sindex][1].format)

            if isinstance(
                self.sections[self.sindex][1].format, pymupdf.Rect
            ) or isinstance(self.sections[self.sindex][1].format, Size):
                return pymupdf.Rect(
                    0.0,
                    0.0,
                    self.sections[self.sindex][1].format.width,
                    self.sections[self.sindex][1].format.height,
                )

        else:
            return pymupdf.paper_rect(self.default_option.format)

    def get_current_section(
        self, index=None
    ):  # get section unit including section info
        if index is None:
            index = self.sindex
        return (
            self.sections[index]
            if isinstance(self.sections[index], list)
            else [self.sections[index]]
        )

    def is_over(self):  # check the end of sections
        return self.sindex >= len(self.sections)

    def cal_cells(self, rect, columns):  # calculate cell areas
        rows = 1  # default
        TABLE = pymupdf.make_table(rect, cols=columns, rows=rows)  # layouts
        CELLS = [TABLE[i][j] for i in range(rows) for j in range(columns)]
        return CELLS

    def run(self, filename):
        # init
        if self.header is None:  # set empty list
            self.header = []
        else:
            for fElement in self.header:
                fElement.make_story()

        if self.footer is None:
            self.footer = []
        else:
            for fElement in self.footer:
                fElement.make_story()

        if self.is_over():
            raise ValueError("section list is empty")

        self.sindex = 0  # initial value, start from zero
        footer_height = 30.0  # default
        header_height = 0.0  # default
        more = True  # need more pages or not
        pno = 0  #
        self.mediabox = self.get_pagerect()  # init

        fileobject = io.BytesIO()  # let DocumentWriter write to memory
        writer = pymupdf.DocumentWriter(fileobject)  # define output writer

        if len(self.header):
            for hElement in self.header:
                _, self.header_rect = hElement.story.place(self.where)

                if (
                    header_height < self.header_rect[3]
                ):  # select max value for header height
                    header_height = self.header_rect[3]

        if len(self.footer):  # calculate Footer rectangle
            for fElement in self.footer:
                _, self.footer_rect = fElement.story.place(self.mediabox)

                if footer_height < self.footer_rect[3]:
                    footer_height = self.footer_rect[3]  # set footer height max

        _ = self.check_cols()  # set initial columns from first section

        while more:  # loop until all input text has been written out
            dev = writer.begin_page(self.mediabox)  # prepare a new output page

            self.where = self.set_margin(self.mediabox)  # set margin
            self.where.y0 = (  # remove space of header from main area
                self.where.y0 if self.where.y0 > header_height else header_height
            )

            self.where.y1 = (  # remove space of footer from main area
                self.where.y1 - footer_height
            )
            if len(self.header):
                self.header_rect = (  # calculate space of header
                    self.header_rect[0],
                    self.header_rect[1],
                    self.where.x1,
                    header_height,
                )
            if len(self.footer):
                self.foot_rect = (  # calculate space of footer
                    self.where.x0,
                    self.where.y1,
                    self.where.x1,
                    self.where.y1 + footer_height,
                )

            if self.sindex == 0:
                self.current_story().make_story()

            CELLS = self.cal_cells(self.where, self.cols)  # calculate CELLS
            CELL_LENGTH = len(CELLS)  # get Length of Cells

            more_cell = True
            cell_index = 0  # columns index

            if len(self.header) != 0:  # draw Header
                for hElement in self.header:
                    hElement.story = None  # delete
                    hElement.make_story()
                    hElement.story.place(self.header_rect)
                    hElement.story.draw(dev, None)

            while more_cell:  # loop until it reach out max column count in one page
                # content may be complete after any cell, ...
                where = CELLS[cell_index]  # temp where
                if (
                    hasattr(self.current_story(), "HEADER_RECTS")
                    and len(self.current_story().HEADER_RECTS) != 0
                ):  # this section store Table headers positions
                    self.current_story().header_tops.append(
                        {
                            "pno": pno,
                            "left": self.current_story().HEADER_RECTS[cell_index].x0,
                            "top": where.y0,
                        }
                    )  # save positions of top rows to draw

                    if (
                        len(self.current_story().header_tops) > 1
                    ):  # skip first piece of table because that already has a top row
                        where.y0 += (
                            self.current_story().HEADER_RECTS[cell_index].height
                        )  # move beginning of table as much as top row height
                    # where.y1 = round(where.y1 - 0.5)  # make integer for safety

                if more:  # so check this status
                    more, filled = self.current_story().story.place(
                        where
                    )  # draw current section
                    self.current_story().story.draw(dev, None)

                if more == 0:  # if there is nothing to draw
                    if (
                        filled[3] < self.where.y1 and self.current_story().advance
                    ):  # check and add section/block
                        where.y0 = filled[3]  # update latest position for next drawing

                    self.sindex += 1  # go next section

                    if self.is_over():  # check the end of sections
                        break

                    self.mediabox = self.get_pagerect()  # internally set mediabox
                    if self.check_cols():  # check new page or not
                        more_cell = False  # set End value to create new page
                    else:
                        if cell_index * 2 < CELL_LENGTH and CELL_LENGTH != 1:
                            # if last cell index is less than half of CELL_LENGTH,
                            # next section starts next to last cell
                            next_where = CELLS[cell_index + 1]  # remake layout
                        else:  # if not, next section starts from the end of last section
                            next_where = CELLS[cell_index]  # remake layout
                            next_where.y0 = filled[3]
                        next_where.x1 = self.where.x1  # use page end for next area end

                        if (
                            next_where.height * next_where.width > 0
                        ):  # vaild rect to calculate
                            # calculate CELLS to continue current page
                            CELLS = self.cal_cells(next_where, self.cols)
                            CELL_LENGTH = len(
                                CELLS
                            )  # init where and cell_index, cell_length
                            self.where = next_where
                            cell_index = 0
                        else:
                            cell_index += 1

                    if not isinstance(self.current_story().story, pymupdf.Story):
                        self.current_story().make_story()

                else:  # check and select next column
                    cell_index += 1

                if cell_index is CELL_LENGTH:  # check whether one page is completed
                    more_cell = False
                    self.where = self.set_margin(self.mediabox)
                    self.current_story().make_story()
                else:
                    where = CELLS[cell_index]  # select new cell

                more = True

            if len(self.footer) != 0:  # draw Footer
                for fElement in self.footer:
                    fElement.story = None  # delete
                    fElement.make_story()
                    fElement.story.place(self.footer_rect)
                    fElement.story.draw(dev, None)

            writer.end_page()  # finish one page

            if self.is_over():  # end writing
                break
            pno += 1
        writer.close()

        doc = pymupdf.open("pdf", fileobject)
        page_count = doc.page_count  # page count
        font_dict = dict()

        for page in doc:  # draw footer with page number
            page.wrap_contents()

            for item in page.get_fonts():
                xref, _, _, fontname, refname, _ = item
                font_dict[fontname] = (xref, refname, page.number)

            btm_rect = pymupdf.Rect(
                self.where.x0, page.rect.y1 - 30, page.rect.x1, page.rect.y1
            )
            page.insert_textbox(  # draw page number
                btm_rect,
                "Page {0} of {1}".format(page.number + 1, page_count),
                align=pymupdf.TEXT_ALIGN_CENTER,
            )

        for i in range(0, len(self.sections)):
            self.sindex = i
            if (
                hasattr(self.current_story(), "HEADER_RECTS")
                and len(self.current_story().HEADER_RECTS) != 0
            ):
                _ = self.check_cols()  # init COLS
                header_rects = self.current_story().HEADER_RECTS

                self.current_story().header_tops.pop(  # remove first element not draw in following loop
                    0
                )

                for i in range(
                    0, len(self.current_story().header_tops)
                ):  # draw Top Row
                    header = self.current_story().header_tops[i]
                    page = doc.load_page(header["pno"])

                    x1 = (
                        header["left"] + header_rects[(i + 1) % self.cols].width
                    )  # get right
                    y1 = (
                        header["top"] + header_rects[(i + 1) % self.cols].height
                    )  # get bottom
                    self.current_story().repeat_header(
                        page,
                        pymupdf.Rect(header["left"], header["top"], x1, y1),
                        font_dict,
                    )

        doc.subset_fonts()
        doc.ez_save(filename)  # save


__all__ = ["Block", "Table", "ImageBlock", "Size", "Options", "Report"]
