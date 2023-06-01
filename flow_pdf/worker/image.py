from .common import PageWorker
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
    pass


@dataclass
class PageInParams(PageInputParams):
    raw_dict: dict


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    image_blocks: list[dict]


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class ImageWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        image_blocks = [b for b in page_in.raw_dict["blocks"] if b["type"] == 1]

        return PageOutParams(image_blocks), LocalPageOutParams()
