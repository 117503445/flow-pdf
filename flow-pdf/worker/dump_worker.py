from .common import Worker
from pathlib import Path
from typing import NamedTuple
import fitz
from fitz import Document, Page, TextPage
import concurrent.futures

from htutil import file


class DocInParams(NamedTuple):
    dir_output: Path
    page_count: int


class PageInParams(NamedTuple):
    raw_dict: dict


class DocOutParams(NamedTuple):
    pass


class PageOutParams(NamedTuple):
    pass


class DumpWorker(Worker):
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
