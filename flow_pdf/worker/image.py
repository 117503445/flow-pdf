from .common import PageWorker
from pathlib import Path
from typing import NamedTuple
import fitz
from fitz import Document, Page, TextPage
import concurrent.futures
from dataclasses import dataclass
from .common import DocInputParams, PageInputParams, DocOutputParams, PageOutputParams


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


class ImageWorker(PageWorker):
    def run_page(# type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams  
    ) -> PageOutParams:
        image_blocks = [b for b in page_in.raw_dict["blocks"] if b["type"] == 1]

        return PageOutParams(image_blocks)
