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
from markdowngenerator import MarkdownGenerator


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


class MarkdownGenWorker(Worker):
    def __init__(self) -> None:
        super().__init__()

        self.disable_cache = True

    def run(
        self, doc_in: DocInputParams, page_in: list[PageInputParams]
    ) -> tuple[DocOutputParams, list[PageOutputParams]]:
        js = file.read_json(doc_in.dir_output / "output" / "doc.json")
        file_dest = doc_in.dir_output / "output" / "doc.md"

        with MarkdownGenerator(
            # By setting enable_write as False, content of the file is written
            # into buffer at first, instead of writing directly into the file
            # This enables for example the generation of table of contents
            filename=file_dest,
            enable_write=False,
            enable_TOC=False,
        ) as doc:
            for m in js["meta"]:
                doc.writeTextLine(f"<!-- {m}: {js['meta'][m]} -->", html_escape=False)

            for element in js["elements"]:
                t = element["type"]
                if t == "shot":
                    p = element["path"]
                    doc.writeTextLine(doc.generateImageHrefNotation(p, Path(p).name))
                    doc.writeTextLine("")
                elif t == 'paragraph':
                    for c in element['children']:
                        t_t = c['type']
                        if t_t == 'text':
                            doc.writeText(c['text'])
                        elif t_t == 'shot':
                            doc.writeText(doc.generateImageHrefNotation(c['path'], Path(c['path']).name))
                        else:
                            self.logger.warning(f"Unknown element type: {t_t}")
                    doc.writeTextLine("")
                    doc.writeTextLine("")
                else:
                    self.logger.warning(f"Unknown element type: {t}")

        return DocOutParams(), []
