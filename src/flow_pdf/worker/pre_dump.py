from .common import PageWorker, add_annot
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)
from .flow_type import MSimpleBlock, MPage, init_mpage_from_mupdf, Rectangle


import fitz
from fitz import Page  # type: ignore
from dataclasses import dataclass
from htutil import file


@dataclass
class DocInParams(DocInputParams):
    pass


@dataclass
class PageInParams(PageInputParams):
    page_info: MPage
    drawings: list
    blocks: list[MSimpleBlock]
    # images: list


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    pass


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class PreDumpWorker(PageWorker):
    def __init__(self) -> None:
        super().__init__()

        self.disable_cache = True

    def post_run_page(self, doc_in: DocInParams, page_in: list[PageInParams]):  # type: ignore[override]
        for p in ["pre-marked", "json", "rawjson"]:
            (doc_in.dir_output / p).mkdir(parents=True, exist_ok=True)

    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        with fitz.open(doc_in.file_input) as doc:  # type: ignore
            page: Page = doc.load_page(page_index)

            file.write_text(doc_in.dir_output / "rawjson" / f"{page_index}.json", page.get_text("rawjson"))  # type: ignore

            file.write_text(doc_in.dir_output / "json" / f"{page_index}.json", page.get_text("json"))  # type: ignore

            # if page_index == 0:
            #     self.logger.info(f"p0 {page.mediabox}")
            #     self.logger.info(f"p0 {page.rect}")
            #     self.logger.info(f"p0 {page.cropbox}")

            # if page_index == 1:
            #     self.logger.info(f"p1 {page.mediabox}")
            #     self.logger.info(f"p1 {page.rect}")
            #     self.logger.info(f"p1 {page.cropbox}")

            # block line
            enable_block_line = True
            for text_block in page_in.page_info.get_text_blocks():
                rects: list[Rectangle] = []
                for line in text_block.lines:
                    rects.append(line.bbox)
                add_annot(page, rects, "", "red")

            # block
            rects = []
            for block in page_in.page_info.blocks:
                delta = 0
                if enable_block_line:
                    delta = 3
                b = Rectangle(
                    block.bbox.x0 - delta,
                    block.bbox.y0 - delta,
                    block.bbox.x1 + delta,
                    block.bbox.y1 + delta,
                )
                rects.append(b)
            add_annot(page, rects, "block", "blue")

            # # drawings
            # rects = []
            # for drawing in drawings:
            #     rects.append(drawing['rect'])
            # add_annot(page, rects, 'drawing', 'red')

            page.get_pixmap(dpi=150).save(doc_in.dir_output / "pre-marked" / f"{page_index}.png")  # type: ignore

            # self.logger.debug(f'page[{page_index}] finished')

            return (
                PageOutParams(),
                LocalPageOutParams(),
            )
