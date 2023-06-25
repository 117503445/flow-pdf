from .common import PageWorker, Block, add_annot
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)


import fitz
from fitz import Page
from dataclasses import dataclass


@dataclass
class DocInParams(DocInputParams):
    pass


@dataclass
class PageInParams(PageInputParams):
    pass


@dataclass
class DocOutParams(DocOutputParams):
    abnormal_size_pages: list[int]


@dataclass
class PageOutParams(PageOutputParams):
    raw_dict: dict
    drawings: list
    blocks: list[Block]
    images: list
    width: int
    height: int


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class ReadDocWorker(PageWorker):
    def __init__(self) -> None:
        super().__init__()

        self.disable_cache = True

    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        with fitz.open(doc_in.file_input) as doc:  # type: ignore
            page: Page = doc.load_page(page_index)

            # if page_index == 0:
            #     self.logger.info(f"p0 {page.mediabox}")
            #     self.logger.info(f"p0 {page.rect}")
            #     self.logger.info(f"p0 {page.cropbox}")

            # if page_index == 1:
            #     self.logger.info(f"p1 {page.mediabox}")
            #     self.logger.info(f"p1 {page.rect}")
            #     self.logger.info(f"p1 {page.cropbox}")

            raw_dict = page.get_text("rawdict")  # type: ignore
            try:
                drawings = page.get_drawings()
            except Exception as e:
                self.logger.warning(f"get_drawings failed: {e}")
                drawings = []
            blocks = [Block(b) for b in page.get_text("blocks")]  # type: ignore
            images = page.get_image_info()  # type: ignore

            width, height = page.mediabox_size


            # block
            rects = []
            for block in raw_dict["blocks"]:
                rects.append(block["bbox"])
            add_annot(page, rects, "", "blue")

            page.get_pixmap(dpi=150).save(doc_in.dir_output / "pre-marked" / f"{page_index}.png")  # type: ignore

            return (
                PageOutParams(raw_dict, drawings, blocks, images, width, height),
                LocalPageOutParams(),
            )

    def post_run_page(self, doc_in: DocInParams, page_in: list[PageInParams]):  # type: ignore[override]
        for p in ["pre-marked"]:
            (doc_in.dir_output / p).mkdir(parents=True, exist_ok=True)

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInputParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        page_size_counter: dict = {}
        for i in range(len(page_out)):
            k = (page_out[i].width, page_out[i].height)
            page_size_counter[k] = page_size_counter.get(k, 0) + 1

        common_size = max(page_size_counter.items(), key=lambda x: x[1])[0]

        abnormal_size_pages = []
        for i in range(len(page_out)):
            k = (page_out[i].width, page_out[i].height)
            if k != common_size:
                abnormal_size_pages.append(i)

        if abnormal_size_pages:
            self.logger.warning(f"abnormal_size_pages: {abnormal_size_pages}")
            # self.logger.warning(f"common_size: {common_size}")
            # idx = abnormal_size_pages[0]
            # self.logger.warning(
            #     f"page_out[{idx}].width = {page_out[idx].width}, page_out[{idx}].height = {page_out[idx].height}"
            # )

        return DocOutParams(abnormal_size_pages)
