from .common import PageWorker
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)
from .flow_type import (
    MSimpleBlock,
    MPage,
    init_mpage_from_mupdf,
    Rectangle,
    Range,
    MTextBlock,
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

        # TODO not use DBSCAN
        db = DBSCAN(eps=3).fit(np.array(widths).reshape(-1, 1))  # type: ignore
        labels = db.labels_
        # get most common label
        label_counts = Counter(labels)
        most_common_label = sorted(
            label_counts.items(), key=lambda x: x[1], reverse=True
        )[0][0]

        most_common_widths = [
            w for i, w in enumerate(widths) if labels[i] == most_common_label
        ]

        width_range = Range(min(most_common_widths), max(most_common_widths))
        self.logger.debug(f"width_range: {width_range}")
        if width_range.max - width_range.min > 30:
            self.logger.debug(f'widths: {widths}, labels: {list(labels)}')
            self.logger.debug(f"width range too big")
            raise Exception("width range too big")

        delta = width_range.max - width_range.min
        delta = 0
        big_text_block = [
            b
            for b in blocks
            if width_range.min - delta * 0.1
            < b.lines[0].bbox.x1 - b.lines[0].bbox.x0
            < width_range.max + delta * 0.1
        ]

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
        self.logger.debug(f"x0_list: {x0_list}, labels: {labels}")

        columns = []
        for label in set(labels):
            if label == -1:
                continue

            blocks = [b for j, b in enumerate(big_text_block) if labels[j] == label]
            if not blocks:
                raise Exception("no blocks found")
            
            bbox_list = [b.bbox for b in blocks]
            self.logger.debug(f'label: {label}, blocks: {bbox_list}')
            column = Range(
                min([b.bbox.x0 for b in blocks]), max([b.bbox.x1 for b in blocks])
            )
            columns.append(column)
        big_text_columns = columns

        return DocOutParams(width_range, big_text_columns)
