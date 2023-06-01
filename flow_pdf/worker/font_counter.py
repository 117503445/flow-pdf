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
    most_common_font: str
    most_common_size: int


@dataclass
class PageOutParams(PageOutputParams):
    font_counter: dict[str, int]
    size_counter: dict[int, int]


class FontCounterWorker(PageWorker):
    def run_page(# type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams 
    ) -> PageOutParams:
        font_counter: dict[str, int]  = {}
        size_counter: dict[int, int] = {}

        for block in page_in.raw_dict["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    font: str = span["font"]
                    if font not in font_counter:
                        font_counter[font] = 0
                    font_counter[font] += len(span["chars"])

                    size: int = span["size"]
                    if size not in size_counter:
                        size_counter[size] = 0
                    size_counter[size] += len(span["chars"])

        return PageOutParams(font_counter, size_counter)

    def after_run_page(# type: ignore[override]
        self,
        doc_in: DocInParams,  
        page_in: list[PageInParams],  
        page_out: list[PageOutParams],  
    ) -> DocOutParams:
        font_counter: dict[str, int] = {}
        size_counter: dict[int, int] = {}
        for p_i in page_out:
            for f, c in p_i.font_counter.items():
                if f not in font_counter:
                    font_counter[f] = 0
                font_counter[f] += c
            for s, c in p_i.size_counter.items():
                if s not in size_counter:
                    size_counter[s] = 0
                size_counter[s] += c

        most_common_font = sorted(
            font_counter.items(), key=lambda x: x[1], reverse=True
        )[0][0]
        most_common_size = sorted(
            size_counter.items(), key=lambda x: x[1], reverse=True
        )[0][0]

        return DocOutParams(most_common_font, most_common_size)
