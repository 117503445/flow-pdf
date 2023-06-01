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


@dataclass
class DocInParams(DocInputParams):
    most_common_font: str
    most_common_size: int

    big_text_width_range: Range
    big_text_columns: list[Range]


@dataclass
class PageInParams(PageInputParams):
    pass


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

        return PageOutParams(), LocalPageOutParams()

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
            },
        )

        return DocOutParams()
