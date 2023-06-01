from .common import PageWorker, Block, Range
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
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
    blocks: list[Block]


@dataclass
class DocOutParams(DocOutputParams):
    big_text_width_range: Range
    big_text_columns: list[Range]


@dataclass
class PageOutParams(PageOutputParams):
    pass


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    large_blocks: list[Block]


class WidthCounterWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        def is_big_block(block: Block):
            BIG_BLOCK_MIN_WORDS = 50

            words = block.lines.split(" ")
            return len(words) > BIG_BLOCK_MIN_WORDS

        big_blocks = list(filter(is_big_block, page_in.blocks))

        return PageOutParams(), LocalPageOutParams(big_blocks)

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        blocks = [b for p in local_page_out for b in p.large_blocks]

        widths = [b.x1 - b.x0 for b in blocks]

        if widths:
            db = DBSCAN(
                eps=5
                # eps=0.3, min_samples=10
            ).fit(
                np.array(widths).reshape(-1, 1)
            )  # type: ignore
            labels = db.labels_
            # get most common label
            label_counts = Counter(labels)
            most_common_label = sorted(
                label_counts.items(), key=lambda x: x[1], reverse=True
            )[0][0]

            big_text_block = [
                b for i, b in enumerate(blocks) if labels[i] == most_common_label
            ]
            big_text_width = [b.x1 - b.x0 for b in big_text_block]

            BIG_TEXT_THRESHOLD = 0.6
            if len(big_text_width) / len(widths) < BIG_TEXT_THRESHOLD:
                print(
                    f"WARNING: most common label only has {len(big_text_width)} items, less than {BIG_TEXT_THRESHOLD * 100}% of total {len(widths)} items"
                )

            width_range = Range(min(big_text_width), max(big_text_width))
            
        
            db = DBSCAN(
                eps=30
                # eps=0.3, min_samples=10
            ).fit(
                np.array([b.x0 for b in big_text_block]).reshape(-1, 1)
            )  # type: ignore
            labels = db.labels_

            columns = []
            for i in range(len(set(labels))):
                blocks = [b for j, b in enumerate(big_text_block) if labels[j] == i]
                column = Range(min([b.x0 for b in blocks]), max([b.x1 for b in blocks]))
                columns.append(column)
            big_text_columns = columns
        else:
            # print("WARNING: no big text found")
            raise Exception("no big text found")

        return DocOutParams(width_range, big_text_columns)
