from .common import PageWorker, Range, Block
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


@dataclass
class PageInParams(PageInputParams):
    raw_dict: dict
    big_blocks: list
    image_blocks: list[dict]
    shot_rects: list
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

            # rects = []
            # for block in page_in.raw_dict["blocks"]:
            #     rects.append(block["bbox"])
            # add_annot(page, rects, "block", "blue")

            # for block in page_in.raw_dict["blocks"]:
            #     rects = []
            #     if block["type"] == 0:
            #         for line in block["lines"]:
            #             rects.append(line["bbox"])
            #     add_annot(page, rects, "l", "red")

            # for block in page_in.raw_dict["blocks"]:
            #     rects = []
            #     if block["type"] == 0:
            #         for line in block["lines"]:
            #             for span in line["spans"]:
            #                 if (
            #                     span["font"] == doc_in.most_common_font
            #                     and abs(span["size"] - doc_in.most_common_size) < 0.5
            #                 ):
            #                     rects.append(span["bbox"])
            #     add_annot(page, rects, "", "purple")

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

            rects = []
            for block in page_in.big_blocks:
                rects.append(block["bbox"])
            add_annot(page, rects, "big-block", "blue")

            # rects = []
            # for block in page_in.drawings:
            #     rects.append(block['rect'])
            # add_annot(page, rects, 'drawings', 'red')

            # rects = []
            # for block in page_in.image_blocks:
            #     rects.append(block["bbox"])
            # add_annot(page, rects, "image-block", "red")

            # rects = []
            # for block in page_in.images:
            #     rects.append(block["bbox"])
            # add_annot(page, rects, "image", "red")

            add_annot(page, page_in.shot_rects, "shot", "green")

            file.write_json(doc_in.dir_output / "shot_rects" / f"{page_index}.json", page_in.shot_rects)

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
            },
        )

        return DocOutParams()
