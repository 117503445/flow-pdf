from .common import Worker
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


class HTMLGenWorker(Worker):
    def __init__(self) -> None:
        super().__init__()

        self.disable_cache = True

    def run(
        self, doc_in: DocInputParams, page_in: list[PageInputParams]
    ) -> tuple[DocOutputParams, list[PageOutputParams]]:
        doc = file.read_json(doc_in.dir_output / "output" / "doc.json")

        html = file.read_text(Path(__file__).parent / "template.html")

        soup = BeautifulSoup(html, "html.parser")

        # add version to head
        for k, v in doc["meta"].items():
            soup.html.head.append(soup.new_tag("meta", attrs={"name": k, "content": v}))  # type: ignore

        for element in doc["elements"]:
            if element["type"] == "paragraph":
                t = soup.new_tag("p")

                for c in element["children"]:
                    if c["type"] == "text":
                        t.append(c["text"])
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
                t = soup.new_tag("img", src=element["path"], attrs={"class": "shot"})
                soup.html.body.append(t)  # type: ignore

            else:
                self.logger.warning(f"unknown element type {element['type']}")
        file.write_text(doc_in.dir_output / "output" / "index.html", soup.prettify())

        return DocOutParams(), []
