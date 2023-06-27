from .common import PageWorker
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)


from dataclasses import dataclass
from .flow_type import MSimpleBlock, MPage, init_mpage_from_mupdf, Rectangle, Range
from htutil import file

@dataclass
class DocInParams(DocInputParams):
    pass


@dataclass
class PageInParams(PageInputParams):
    page_info: MPage


@dataclass
class DocOutParams(DocOutputParams):
    most_common_font: str
    common_size_range: Range


@dataclass
class PageOutParams(PageOutputParams):
    pass


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    font_counter: dict[str, int]
    size_counter: dict[float, int]


class FontCounterWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        font_counter: dict[str, int] = {}
        size_counter: dict[float, int] = {}

        for block in page_in.page_info.get_text_blocks():
            for line in block.lines:
                for span in line.spans:
                    font = span.font
                    if font not in font_counter:
                        font_counter[font] = 0
                    font_counter[font] += len(span.chars)

                    size = span.size
                    if size not in size_counter:
                        size_counter[size] = 0
                    size_counter[size] += len(span.chars)

        return PageOutParams(), LocalPageOutParams(font_counter, size_counter)

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        font_counter: dict[str, int] = {}
        size_counter: dict[float, int] = {}
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

        most_common_font_radio = font_counter[most_common_font] / sum(
            font_counter.values()
        )

        most_common_size = sorted(
            size_counter.items(), key=lambda x: x[1], reverse=True
        )[0][0]

        most_common_size_radio = size_counter[most_common_size] / sum(
            size_counter.values()
        )
        if most_common_size_radio >= 0.5:
            common_size_range = Range(most_common_size, most_common_size)
        else:
            self.logger.info(f"most common font size is {most_common_size_radio}")
            most_common_size = 0

            size_list: list[float] = []
            for s, c in size_counter.items():
                for _ in range(c):
                    size_list.append(s)

            def sub_array_range(arr: list[float], sub_arr_range: int) -> Range:
                """
                返回 arr 中包含最多元素的连续子数组，使得该子数组的最大值与最小值之差小于 sub_arr_range。
                """

                if len(arr) == 0:
                    raise ValueError("arr is empty")

                arr.sort()

                max_start = 0
                max_end = 0
                max_len = 1

                start = 0
                end = 0
                while end < len(arr):
                    if arr[end] - arr[start] > sub_arr_range:
                        start += 1
                    else:
                        if end - start + 1 > max_len:
                            max_len = end - start + 1
                            max_start = start
                            max_end = end
                        end += 1

                radio = max_len / len(arr)
                self.logger.info(f'most common font size radio is {radio}')

                return Range(arr[max_start], arr[max_end])

            if not size_list:
                raise ValueError("size_list is empty")
            
            common_size_range = sub_array_range(size_list, 3)

        return DocOutParams(most_common_font, common_size_range)
