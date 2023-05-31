from .common import PageWorker
from pathlib import Path
from typing import NamedTuple
import fitz
from fitz import Document, Page, TextPage
import concurrent.futures


class DocInParams(NamedTuple):
    file_input: Path
    page_count: int


class PageInParams(NamedTuple):
    pass


class DocOutParams(NamedTuple):
    pass


class PageOutParams(NamedTuple):
    raw_dict: dict


class ReadDocWorker(PageWorker):
    def run(
        self, doc_in: DocInParams, page_in: list[PageInParams]
    ) -> tuple[DocOutParams, list[PageOutParams]]:
        results: list[PageOutParams] = []
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for page_index in range(doc_in.page_count):
                futures.append(
                    executor.submit(
                        self.page_run, page_index, doc_in, page_in[page_index]
                    )
                )
            for future in futures:
                results.append(future.result())

        return (DocOutParams(), results)

    def page_run(
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> PageOutParams:
        with fitz.open(doc_in.file_input) as doc:  # type: ignore
            page: Page = doc.load_page(page_index)
            raw_dict = page.get_text("rawdict")  # type: ignore
            return PageOutParams(raw_dict=raw_dict)
