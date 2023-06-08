from .common import PageWorker, Range, Block, is_common_span, get_min_bounding_rect
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)

from dataclasses import dataclass

from htutil import file
from fitz import Page
import fitz
import fitz.utils


@dataclass
class DocInParams(DocInputParams):
    most_common_font: str
    most_common_size: int

    big_text_width_range: Range
    big_text_columns: list[Range]

    core_y: Range
    abnormal_size_pages: list[int]


@dataclass
class PageInParams(PageInputParams):
    raw_dict: dict
    big_blocks: list[list]  # column -> block
    shot_rects: list[list]  # column -> block
    image_blocks: list[dict]
    images: list
    drawings: list


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    pass


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class DumpWorker(PageWorker):
    def __init__(self) -> None:
        super().__init__()

        self.disable_cache = True

    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        with fitz.open(doc_in.file_input) as doc:  # type: ignore
            page: Page = doc.load_page(page_index)
            file.write_text(doc_in.dir_output / "raw_dict" / f"{page_index}.json", page.get_text("rawjson"))  # type: ignore

            page.get_pixmap(dpi=150).save(doc_in.dir_output / "raw" / f"{page_index}.png")  # type: ignore

            def add_annot(page, rects, annot: str, color):
                if not rects:
                    return

                for i, rect in enumerate(rects):
                    if annot:
                        a = f"{annot}-{i}"
                        page.add_freetext_annot(
                            (rect[0], rect[1], rect[0] + len(a) * 6, rect[1] + 10),
                            a,
                            fill_color=fitz.utils.getColor("white"),
                            border_color=fitz.utils.getColor("black"),
                        )

                    page.draw_rect(rect, color=fitz.utils.getColor(color))  # type: ignore
            page.draw_rect( (175.56077575683594,
                    109.79204559326172,
                    185.58013916015625,
                    127.0074462890625), color=fitz.utils.getColor('black'))
            # block
            # rects = []
            # for block in page_in.raw_dict["blocks"]:
            #     rects.append(block["bbox"])
            # add_annot(page, rects, "block", "blue")

            # block line
            # for block in page_in.raw_dict["blocks"]:
            #     rects = []
            #     if block["type"] == 0:
            #         for line in block["lines"]:
            #             rects.append(line["bbox"])
            #     add_annot(page, rects, "", "red")
            # add_annot(page, rects, "l", "red")

            # block common span
            # for block in page_in.raw_dict["blocks"]:
            #     rects = []
            #     if block["type"] == 0:
            #         for line in block["lines"]:
            #             for span in line["spans"]:
            #                 if is_common_span(span, doc_in.most_common_font, doc_in.most_common_size):
            #                     rects.append(span["bbox"])
            #     add_annot(page, rects, "", "purple")

            # new line
            # rects = []
            # for b in page_in.big_blocks:
            #     for i in range(1, len(b["lines"])):
            #         line = b["lines"][i]
            #         delta = line["bbox"][0] - b["bbox"][0]
            #         if delta > 1:
            #             last_line = b["lines"][i - 1]
            #             if last_line["bbox"][0] - b["bbox"][0] < 1:
            #                 rects.append(line["bbox"])
            # add_annot(page, rects, "new-line", "pink")

            # big block
            for c in page_in.big_blocks:
                rects = []
                for block in c:
                    rects.append(block["bbox"])
                add_annot(page, rects, "big-block", "blue")

            # drawings
            # rects = []
            # for block in page_in.drawings:
            #     rects.append(block['rect'])
            # add_annot(page, rects, 'drawings', 'red')

            # image-block
            # rects = []
            # for block in page_in.image_blocks:
            #     rects.append(block["bbox"])
            # add_annot(page, rects, "image-block", "red")

            # image
            # rects = []
            # for block in page_in.images:
            #     rects.append(block["bbox"])
            # add_annot(page, rects, "image", "red")

            # shot in column view
            if page_index in doc_in.abnormal_size_pages:
                rects =  page_in.shot_rects[0][0]
                add_annot(page, rects, "shot-abnormal-page", "green")
            else:
                for c in page_in.shot_rects:
                    rects = []
                    for shot in c:
                        rects.append(get_min_bounding_rect(shot))
                    add_annot(page, rects, "shot", "green")

            # shot in rect view
            # for c in page_in.shot_rects:
            #     for shot in c:
            #         add_annot(page, shot, "shot-r", "green")

            file.write_json(
                doc_in.dir_output / "shot_rects" / f"{page_index}.json",
                page_in.shot_rects,
            )

            page.get_pixmap(dpi=150).save(doc_in.dir_output / "marked" / f"{page_index}.png")  # type: ignore

        return PageOutParams(), LocalPageOutParams()

    def post_run_page(self, doc_in: DocInParams, page_in: list[PageInParams]):  # type: ignore[override]
        for p in ["marked", "raw_dict", "raw", "shot_rects"]:
            (doc_in.dir_output / p).mkdir(parents=True, exist_ok=True)

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        file.write_json(
            doc_in.dir_output / "meta.json", {"page_count": doc_in.page_count}
        )

        file_meta = doc_in.dir_output / "meta.json"
        file.write_json(
            file_meta,
            {
                "most_common_font": doc_in.most_common_font,
                "most_common_size": doc_in.most_common_size,
                "big_text_width_range": doc_in.big_text_width_range,
                "big_text_columns": doc_in.big_text_columns,
                "core_y": doc_in.core_y,
                'abnormal_size_pages': doc_in.abnormal_size_pages
            },
        )

        return DocOutParams()
