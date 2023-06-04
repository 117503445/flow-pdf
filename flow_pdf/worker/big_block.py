from .common import PageWorker, Block, Range
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
    big_text_width_range: Range
    big_text_columns: list[Range]


@dataclass
class PageInParams(PageInputParams):
    raw_dict: dict


@dataclass
class DocOutParams(DocOutputParams):
    core_y: Range


@dataclass
class PageOutParams(PageOutputParams):
    big_blocks: list


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class BigBlockWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        blocks = [b for b in page_in.raw_dict["blocks"] if b["type"] == 0]

        def is_big_block(block):
            def is_in_width_range(block):
                return (
                    doc_in.big_text_width_range.min * 0.9
                    <= block["bbox"][2] - block["bbox"][0]
                    <= doc_in.big_text_width_range.max * 1.1
                )

            def is_in_right_x_position(block):
                for column in doc_in.big_text_columns:
                    if column.min * 0.9 <= block["bbox"][0] <= column.max * 1.1:
                        return True
                return False

            judgers = [is_in_width_range, is_in_right_x_position]
            for judger in judgers:
                if not judger(block):
                    return False
            return True

        big_blocks = list(filter(is_big_block, blocks))

        return PageOutParams(big_blocks), LocalPageOutParams()

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        block_list = [b for page in page_out for b in page.big_blocks]

        core_y = Range(
            min([b["bbox"][1] for b in block_list]),
            max([b["bbox"][3] for b in block_list]),
        )

        return DocOutParams(core_y)
