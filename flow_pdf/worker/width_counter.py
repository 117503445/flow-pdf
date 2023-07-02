from .common import PageWorker
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
    frequent_sub_array,
)
from .flow_type import (
    MSimpleBlock,
    MPage,
    init_mpage_from_mupdf,
    Rectangle,
    Range,
    MTextBlock,
    MLine,
)

import numpy as np
from dataclasses import dataclass
from sklearn.cluster import DBSCAN
from collections import Counter


@dataclass
class DocInParams(DocInputParams):
    pass


@dataclass
class PageInParams(PageInputParams):
    page_info: MPage


@dataclass
class DocOutParams(DocOutputParams):
    big_text_width_range: Range
    big_text_columns: list[Range]
    big_text_line_height_range: Range


@dataclass
class PageOutParams(PageOutputParams):
    pass


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    large_blocks: list[MTextBlock]


class WidthCounterWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        def is_big_block(block: MTextBlock):
            BIG_BLOCK_MIN_WORDS = 50

            words = 0
            for line in block.lines:
                for span in line.spans:
                    s = ""
                    for c in span.chars:
                        s += c.c
                    words += len(s.split())

            return words > BIG_BLOCK_MIN_WORDS

        big_blocks = list(filter(is_big_block, page_in.page_info.get_text_blocks()))

        return PageOutParams(), LocalPageOutParams(big_blocks)

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        blocks = [b for p in local_page_out for b in p.large_blocks]

        widths = []
        for block in blocks:
            for line in block.lines:
                widths.append(line.bbox.x1 - line.bbox.x0)

        # self.logger.debug(f"widths: {widths}")

        if not widths:
            raise Exception("no big text found")

        most_common_widths = frequent_sub_array(widths, 3)

        width_range = Range(min(most_common_widths), max(most_common_widths))
        self.logger.debug(f"width_range: {width_range}")

        delta = width_range.max - width_range.min
        big_text_block = [
            b
            for b in blocks
            if width_range.min - delta * 0.1
            < b.bbox.x1 - b.bbox.x0
            < width_range.max + delta * 0.1
        ]
        if not big_text_block:
            raise Exception("no big text found")

        BIG_TEXT_THRESHOLD = 0.6
        if len(big_text_block) / len(blocks) < BIG_TEXT_THRESHOLD:
            self.logger.warning(
                f"most common label only has {len(big_text_block)} items, less than {BIG_TEXT_THRESHOLD * 100}% of total {len(blocks)} items"
            )

        x0_list = np.array([b.bbox.x0 for b in big_text_block]).reshape(-1, 1)

        if len(x0_list) <= 7:
            min_samples = 2
        elif len(x0_list) <= 10:
            min_samples = 3
        elif len(x0_list) <= 15:
            min_samples = 4
        else:
            min_samples = 5

        db = DBSCAN(eps=10, min_samples=min_samples).fit(x0_list)  # type: ignore
        labels = db.labels_
        # self.logger.debug(f"x0_list: {x0_list}, labels: {labels}")

        big_text_columns = []
        for label in set(labels):
            if label == -1:
                continue

            blocks = [b for j, b in enumerate(big_text_block) if labels[j] == label]
            # bbox_list = [b.bbox for b in blocks]
            # self.logger.debug(f'label: {label}, blocks: {bbox_list}')
            column = Range(
                min([b.bbox.x0 for b in blocks]), max([b.bbox.x1 for b in blocks])
            )
            big_text_columns.append(column)

        # Bano - 2022 - Twins Bft systems made robust
        # merge columns
        if len(big_text_columns) > 1:
            for i in reversed(range(len(big_text_columns) - 1)):
                cur: Range = big_text_columns[i]
                next: Range = big_text_columns[i + 1]

                if cur.max - next.min > (width_range.max - width_range.min) * 0.1:
                    big_text_columns[i] = Range(cur.min, next.max)
                    del big_text_columns[i + 1]

        lines: list[MLine] = []
        for b in big_text_block:
            for line in b.lines:
                if line.bbox.x1 - line.bbox.x0 > (b.bbox.x1 - b.bbox.x0) * 0.9:
                    lines.append(line)

        lines_height = [line.bbox.y1 - line.bbox.y0 for line in lines]
        most_common_heights = frequent_sub_array(lines_height, 0.2)
        height_range = Range(min(most_common_heights), max(most_common_heights))

        return DocOutParams(width_range, big_text_columns, height_range)
