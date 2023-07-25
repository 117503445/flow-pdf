from .common import PageWorker
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)
from dataclasses import dataclass
from .flow_type import (
    MPage,
    MImageBlock,
)


@dataclass
class DocInParams(DocInputParams):
    pass


@dataclass
class PageInParams(PageInputParams):
    page_info: MPage


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    image_blocks: list[MImageBlock]


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class ImageWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        image_blocks = page_in.page_info.get_image_blocks()

        return PageOutParams(image_blocks), LocalPageOutParams()
