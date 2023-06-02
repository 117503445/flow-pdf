from .common import PageWorker, Block
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)
from htutil import file
from pathlib import Path
from dataclasses import dataclass
from bs4 import BeautifulSoup


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
    pass


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class HTMLGenWorker(PageWorker):
    def __init__(self) -> None:
        super().__init__()

        self.disable_cache = True

    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        elements = file.read_json(doc_in.dir_output / "output" / "elements.json")

        html = file.read_text(Path(__file__).parent / "template.html")

        soup = BeautifulSoup(html, "html.parser")
        for element in elements:
            if element["type"] == "block":
                t = soup.new_tag("div")

                for c in element["childs"]:
                    if c["type"] == "text":
                        t.append(c["text"])
                    elif c['type'] == 'new-line':
                        t.append(soup.new_tag('br'))
                    elif c["type"] == "shot":
                        t.append(
                            soup.new_tag(
                                "img", src=c["path"], attrs={"class": "inline-img"}
                            )
                        )
                    else:
                        self.logger.warning(f"unknown child type {c['type']}")
                soup.html.body.append(t)  # type: ignore
            elif element["type"] == "shot":
                t = soup.new_tag("img", src=element["path"])
                soup.html.body.append(t)  # type: ignore
            else:
                self.logger.warning(f"unknown element type {element['type']}")
        file.write_text(doc_in.dir_output / "output" / "index.html", soup.prettify())

        return PageOutParams(), LocalPageOutParams()
