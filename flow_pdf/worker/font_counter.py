from .common import PageWorker
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)


from dataclasses import dataclass


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
    pass


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    font_counter: dict[str, int]
    size_counter: dict[int, int]


class FontCounterWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        font_counter: dict[str, int] = {}
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

        return PageOutParams(), LocalPageOutParams(font_counter, size_counter)

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        font_counter: dict[str, int] = {}
        size_counter: dict[int, int] = {}
        for p_i in local_page_out:
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

        most_common_font_radio = font_counter[most_common_font] / sum(font_counter.values())
        if most_common_font_radio < 0.3:
            self.logger.warning(f"most common font radio is {most_common_font_radio}")

        most_common_size = sorted(
            size_counter.items(), key=lambda x: x[1], reverse=True
        )[0][0]
        
        # TODO font size range
        most_common_size_radio = size_counter[most_common_size] / sum(size_counter.values())
        if most_common_size_radio < 0.3:
            self.logger.warning(f"most common font size is {most_common_size_radio}")
            most_common_size = 0

        return DocOutParams(most_common_font, most_common_size)
