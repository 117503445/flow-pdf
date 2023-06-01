from .common import Worker
from pathlib import Path
from typing import NamedTuple
import fitz
from fitz import Document, Page, TextPage
import concurrent.futures
from dataclasses import dataclass
from .common import DocInputParams, PageInputParams, DocOutputParams, PageOutputParams

from htutil import file

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
    pass


class DumpWorker(Worker):
    def __init__(self) -> None:
        super().__init__()

        self.disable_cache = True

    def run(
        self, doc_in: DocInParams, page_in: list[PageInParams]
    ) -> tuple[DocOutParams, list[PageOutParams]]:
        file.write_json(
            doc_in.dir_output / "meta.json", {"page_count": doc_in.page_count}
        )

        dir_raw_dict = doc_in.dir_output / "raw_dict"
        for page_index, p_i in enumerate(page_in):
            file.write_json(dir_raw_dict / f"{page_index}.json", p_i.raw_dict)

        return (DocOutParams(), [])
