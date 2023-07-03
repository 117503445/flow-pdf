from .common import (
    PageWorker,
    is_common_span,
    rectangle_relation,
    RectRelation,
    get_min_bounding_rect,
    frequent_sub_array,
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
    MLine,
    MSpan,
    Point,
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

    text_blocks_bbox: list[list[Rectangle]]  # column -> bbox, for shot


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

        text_blocks_bbox: list[list[Rectangle]] = [
            [] for _ in range(len(doc_in.big_text_columns))
        ]

        if page_index in doc_in.abnormal_size_pages:
            return PageOutParams(big_blocks, text_blocks_bbox), LocalPageOutParams()

        blocks = page_in.page_info.get_text_blocks()

        for b in blocks:
            for i, column in enumerate(doc_in.big_text_columns):
                delta = (column.max - column.min) * 0.1
                if (
                    column.min - delta <= b.bbox.x0 <= column.min + delta
                    and column.max - delta <= b.bbox.x1 <= column.max + delta
                ):
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
                line_height = block.lines[0].bbox.y1 - block.lines[0].bbox.y0
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
                (is_in_width_range, False),
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
        # for column_blocks in big_blocks:
        #     for i in reversed(range(len(column_blocks))):
        #         if i == len(column_blocks) - 1:
        #             continue
        #         cur_block = column_blocks[i]
        #         next_block = column_blocks[i + 1]

        #         line_height = cur_block.lines[0].bbox.y1 - cur_block.lines[0].bbox.y0
        #         block_height = cur_block.bbox.y1 - cur_block.bbox.y0
        #         if block_height / line_height < 1.5:
        #             if i + 1 >= len(column_blocks):
        #                 print(i, len(column_blocks), doc_in.file_input)
        #             if next_block.bbox.y0 - cur_block.bbox.y1 >= line_height * 0.5:
        #                 if i >= len(column_blocks):
        #                     print(i, len(column_blocks), doc_in.file_input)
        #                 del column_blocks[i]

        # merge
        for column_blocks in big_blocks:
            for i in reversed(range(len(column_blocks))):
                if i == len(column_blocks) - 1:
                    continue

                cur_block = column_blocks[i]
                next_block = column_blocks[i + 1]

                if next_block.bbox.y0 - cur_block.bbox.y1 <= 10:
                    cur_block.lines.extend(next_block.lines)
                    cur_block.bbox.x0 = min(cur_block.bbox.x0, next_block.bbox.x0)
                    cur_block.bbox.y0 = min(cur_block.bbox.y0, next_block.bbox.y0)
                    cur_block.bbox.y1 = max(cur_block.bbox.y1, next_block.bbox.y1)
                    cur_block.bbox.x1 = max(cur_block.bbox.x1, next_block.bbox.x1)
                    del column_blocks[i + 1]

        for i, column_blocks in enumerate(big_blocks):
            for block in column_blocks:
                text_blocks_bbox[i].append(block.bbox)
            text_blocks_bbox[i].sort(key=lambda rect: rect.y0)

        # TODO Line
        # Aublin et al. - 2013 - Rbft Redundant byzantine fault tolerance

        for column_blocks in big_blocks:
            for i, b in enumerate(column_blocks):
                spans: list[MSpan] = []
                for line in b.lines:
                    spans.extend(line.spans)

                spans.sort(key=lambda span: (span.bbox.x0, span.bbox.y0))

                spans_list: list[list[MSpan]] = []

                remain_spans: list[MSpan] = []
                reremain_spans: list[MSpan] = []

                for span in spans:
                    if span.bbox.width() > b.bbox.width() * 0.5:
                        spans_list.append([span])
                    else:
                        remain_spans.append(span)

                remain_spans.sort(key=lambda span: (span.bbox.x0, span.bbox.y0))

                for span in remain_spans:
                    found = False
                    for spans in spans_list:
                        intersection_start = max(span.bbox.y0, spans[0].bbox.y0)
                        intersection_end = min(span.bbox.y1, spans[0].bbox.y1)
                        if intersection_end > intersection_start:
                            found = True
                            break
                    if not found:
                        spans_list.append([span])
                    else:
                        reremain_spans.append(span)

                for span in reremain_spans:
                    max_intersection_radio = 0.0
                    max_intersection_spans: list[MSpan] = []

                    for spans in spans_list:
                        intersection_start = max(span.bbox.y0, spans[0].bbox.y0)
                        intersection_end = min(span.bbox.y1, spans[0].bbox.y1)
                        radio = (
                            intersection_end - intersection_start
                        ) / span.bbox.height()
                        if radio > max_intersection_radio:
                            max_intersection_radio = radio
                            max_intersection_spans = spans

                    if max_intersection_radio == 0.0:
                        raise Exception("max_intersection_radio == 0.0")

                    max_intersection_spans.append(span)

                lines: list[MLine] = []

                for spans in spans_list:
                    spans.sort(key=lambda span: (span.bbox.x0, span.bbox.y0))
                    rects = []
                    for span in spans:
                        rects.append(span.bbox)
                    lines.append(
                        MLine(get_min_bounding_rect(rects), 0, Point(0, 0), spans)
                    )

                lines.sort(key=lambda line: (line.bbox.y0, line.bbox.x0))

                column_blocks[i] = MTextBlock(b.bbox, 0, lines)

        # split
        for i, column_blocks in enumerate(big_blocks):
            new_column_blocks: list[MTextBlock] = []
            for j, b in enumerate(column_blocks):
                MIN_DELTA = 5.0
                deltas = []
                for line in b.lines:
                    deltas.append(b.bbox.x1 - line.bbox.x1)
                sub_d = frequent_sub_array(deltas, 2)

                RIGHT_DISTANCE_THRESHOLD = 0.5
                radio = len(sub_d) / len(deltas)
                if radio > RIGHT_DISTANCE_THRESHOLD:
                    MIN_DELTA += sub_d[-1]

                # self.logger.debug(f'page[{page_index}] column[{i}] j[{j}] radio: {radio}, MIN_DELTA: {MIN_DELTA}, deltas: {deltas}, sub_d: {sub_d}')

                p_lines_list: list[list[MLine]] = [[]]
                for j in range(len(b.lines)):
                    line = b.lines[j]
                    p_lines_list[-1].append(line)

                    # TODO
                    # Danezis et al. - 2022 - Narwhal and Tusk a DAG-based mempool and efficien 8

                    if b.bbox.x1 - line.bbox.x1 > MIN_DELTA:
                        p_lines_list.append([])

                if len(p_lines_list[-1]) == 0:
                    del p_lines_list[-1]

                for p_lines in p_lines_list:
                    rects = []
                    for line in p_lines:
                        rects.append(line.bbox)
                    r = get_min_bounding_rect(rects)
                    new_column_blocks.append(MTextBlock(r, 0, p_lines))

            big_blocks[i] = new_column_blocks

        return PageOutParams(big_blocks, text_blocks_bbox), LocalPageOutParams()

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        block_list = [b for page in page_out for bs in page.big_blocks for b in bs]
        if not block_list:
            self.logger.debug(f"no big block, doc_in = {doc_in}")
            raise Exception("no big block")

        core_y = Range(
            min([b.bbox.y0 for b in block_list]),
            max([b.bbox.y1 for b in block_list]),
        )

        return DocOutParams(core_y)
