from .common import PageWorker, Block, Range
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)


from dataclasses import dataclass


@dataclass
class DocInParams(DocInputParams):
    big_text_columns: list[Range]

    core_y: Range


@dataclass
class PageInParams(PageInputParams):
    big_blocks: list


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    shot_rects: list


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class ShotWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        rects = []

        for column in doc_in.big_text_columns:
            blocks = [
                b
                for b in page_in.big_blocks
                if b["bbox"][0] >= column.min and b["bbox"][2] <= column.max
            ]
            last_y = doc_in.core_y.min
            for block in blocks:
                r = (column.min, last_y, column.max, block["bbox"][1])
                if r[3] - r[1] > 0:
                    rects.append(r)
                else:
                    self.logger.warning(f"r.y1 <= r.y0, r = {r}")
                last_y = block["bbox"][3]
            rects.append((column.min, last_y, column.max, doc_in.core_y.max))

        return PageOutParams(rects), LocalPageOutParams()
