from .common import (
    PageWorker,
    is_common_span,
    rectangle_relation,
    RectRelation,
)
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


from dataclasses import dataclass


@dataclass
class DocInParams(DocInputParams):
    big_text_width_range: Range
    big_text_columns: list[Range]

    most_common_font: str
    common_size_range: Range

    abnormal_size_pages: list[int]


@dataclass
class PageInParams(PageInputParams):
    page_info: MPage
    drawings: list


@dataclass
class DocOutParams(DocOutputParams):
    core_y: Range


@dataclass
class PageOutParams(PageOutputParams):
    big_blocks: list[list[MTextBlock]]  # column -> blocks


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class BigBlockWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        big_blocks: list[list[MTextBlock]] = [
            [] for _ in range(len(doc_in.big_text_columns))
        ]

        if page_index in doc_in.abnormal_size_pages:
            return PageOutParams(big_blocks), LocalPageOutParams()

        blocks = page_in.page_info.get_text_blocks()

        for b in blocks:
            for i, column in enumerate(doc_in.big_text_columns):
                delta = (column.max - column.min) * 0.1
                if column.min - delta <= b.bbox.x0 <= column.min + delta:
                    big_blocks[i].append(b)
                    # near_lines_count = 0
                    # for line in b.lines:
                    #     if line.bbox.x0 < column.min + 20:
                    #         near_lines_count += 1

                    # if (near_lines_count / len(b.lines)) > 0.8 or (near_lines_count == 1 and len(b.lines) != 1):
                    #     big_blocks[i].append(b)
                    break

        def is_big_block(block: MTextBlock):
            def is_in_width_range(block: MTextBlock):
                return (
                    doc_in.big_text_width_range.min * 0.9
                    <= block.bbox.x1 - block.bbox.x0
                    <= doc_in.big_text_width_range.max * 1.1
                )

            def is_line_y_increase(block: MTextBlock):
                for i in range(len(block.lines) - 1):
                    if block.lines[i].bbox.y1 > block.lines[i + 1].bbox.y1:
                        return False
                return True

            def is_common_text_too_little(block: MTextBlock):
                sum_count = 0
                common_count = 0

                for line in block.lines:
                    for span in line.spans:
                        sum_count += len(span.chars)
                        if is_common_span(
                            span, doc_in.most_common_font, doc_in.common_size_range
                        ):
                            common_count += len(span.chars)

                return common_count / sum_count > 0.5

            def is_not_be_contained(block: MTextBlock):
                # deep_root 0
                for drawing in page_in.drawings:
                    if (
                        rectangle_relation(block.bbox, drawing["rect"])
                        == RectRelation.CONTAINED_BY
                    ):
                        return False
                return True

            def is_enough_lower(block: MTextBlock):
                chars_count = 0
                lower_chars_count = 0

                for line in block.lines:
                    for span in line.spans:
                        for char in span.chars:
                            chars_count += 1
                            if char.c.islower():
                                lower_chars_count += 1

                # self.logger.debug(f"lower_chars_count: {lower_chars_count}, chars_count: {chars_count}, ratio: {lower_chars_count / chars_count}")
                return lower_chars_count / chars_count > 0.5 and chars_count > 10

            def is_single_line_has_end(block: MTextBlock):
                line_height = (
                    block.lines[0].bbox.y1 - block.lines[0].bbox.y0
                )
                block_height = block.bbox.y1 - block.bbox.y0
                if block_height / line_height < 1.5:
                    if block.lines[0].spans[-1].chars[-1].c not in [
                        ".",
                        "。",
                        "!",
                        "！",
                        "?",
                    ]:
                        return False
                return True

            judgers = [
                (is_in_width_range, True),
                (is_line_y_increase, False),  # lines maybe in same y
                (is_common_text_too_little, True),
                (is_not_be_contained, True),
                (is_enough_lower, True),
                (is_single_line_has_end, False),  # like bitcoin
            ]
            for judger, enabled in judgers:
                if enabled and not judger(block):
                    return False
            return True

        for i, blocks in enumerate(big_blocks):
            big_blocks[i] = list(filter(is_big_block, blocks))
            big_blocks[i] = sorted(big_blocks[i], key=lambda block: block.bbox.y0)

        # single block should on the top of another block
        for column_blocks in big_blocks:
            for i in reversed(range(len(column_blocks))):
                if i == len(column_blocks) - 1:
                    continue
                cur_block = column_blocks[i]
                next_block = column_blocks[i + 1]

                line_height = (
                    cur_block.lines[0].bbox.y1 - cur_block.lines[0].bbox.y0
                )
                block_height = cur_block.bbox.y1 - cur_block.bbox.y0
                if block_height / line_height < 1.5:
                    if i + 1 >= len(column_blocks):
                        print(i, len(column_blocks), doc_in.file_input)
                    if (
                        next_block.bbox.y0 - cur_block.bbox.y1
                        >= line_height * 0.5
                    ):
                        if i >= len(column_blocks):
                            print(i, len(column_blocks), doc_in.file_input)
                        del column_blocks[i]

        return PageOutParams(big_blocks), LocalPageOutParams()

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        block_list = [b for page in page_out for bs in page.big_blocks for b in bs]

        core_y = Range(
            min([b.bbox.y0 for b in block_list]),
            max([b.bbox.y1 for b in block_list]),
        )

        return DocOutParams(core_y)
