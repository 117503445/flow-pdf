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

        def mk_html(elements, dest: Path):
            soup = BeautifulSoup(html, "html.parser")

            # add version to head
            for k, v in doc["meta"].items():
                soup.html.head.append(soup.new_tag("meta", attrs={"name": k, "content": v}))  # type: ignore

            for element in elements:
                if element["type"] == "paragraph":
                    t = soup.new_tag("p")

                    for c in element["children"]:
                        if c["type"] == "text":
                            t.append(c["text"])
                            # span = soup.new_tag("span")
                            # span.append(c["text"])
                            # t.append(
                            #     span
                            # )
                            
                        elif c["type"] == "shot":
                            t.append(
                                soup.new_tag(
                                    "img", src=c["path"], attrs={"class": "inline-img"}
                                )
                            )
                        else:
                            self.logger.warning(f"unknown child type {c['type']}")
                    # for two column layout, paragraph ends with a shot will crash, so add a dot
                    if element["children"][-1]["type"] == "shot":
                        t.append(".")
                    soup.html.body.append(t)  # type: ignore
                elif element["type"] == "shot":
                    t = soup.new_tag(
                        "img", src=element["path"], attrs={"class": "shot"}
                    )
                    soup.html.body.append(t)  # type: ignore
                else:
                    self.logger.warning(f"unknown element type {element['type']}")
            file.write_text(dest, soup.prettify())

        BIG_ELEMENT_SIZE = 5000

        if len(doc["elements"]) < BIG_ELEMENT_SIZE:
            mk_html(doc["elements"], doc_in.dir_output / "output" / "index.html")
        else:
            PER_HTML_ELEMENTS = 500
            for i in range(0, int(len(doc["elements"]) / PER_HTML_ELEMENTS) + 1):
                mk_html(
                    doc["elements"][i * PER_HTML_ELEMENTS : (i + 1) * PER_HTML_ELEMENTS],
                    doc_in.dir_output / "output" / f"part_{i}.html",
                )
            
            # make index
            soup = BeautifulSoup(html, "html.parser")
            # add version to head
            for k, v in doc["meta"].items():
                soup.html.head.append(soup.new_tag("meta", attrs={"name": k, "content": v}))  # type: ignore

            for i in range(0, int(len(doc["elements"]) / PER_HTML_ELEMENTS) + 1):
                a = soup.new_tag(
                        "a", href=f"part_{i}.html", attrs={"class": "part-link"}
                    )
                a.string = f"part_{i}"
                soup.html.body.append(a) # type: ignore

                soup.html.body.append(soup.new_tag("br")) # type: ignore

            file.write_text(doc_in.dir_output / "output" / "index.html", soup.prettify())


        return DocOutParams(), []
