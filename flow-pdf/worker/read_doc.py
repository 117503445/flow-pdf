from .common import PageWorker
from .common import DocInputParams, PageInputParams, DocOutputParams, PageOutputParams

from pathlib import Path
from typing import NamedTuple
import fitz
from fitz import Document, Page, TextPage
import concurrent.futures
from dataclasses import dataclass


@dataclass
class DocInParams(DocInputParams):
    pass


@dataclass
class PageInParams(PageInputParams):
    pass


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    raw_dict: dict


class ReadDocWorker(PageWorker):
    def run_page(
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> PageOutParams:
        with fitz.open(doc_in.file_input) as doc:  # type: ignore
            page: Page = doc.load_page(page_index)
            raw_dict = page.get_text("rawdict")  # type: ignore
            return PageOutParams(raw_dict=raw_dict)
