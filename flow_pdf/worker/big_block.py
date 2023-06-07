from .common import PageWorker, Block, Range, is_common_span, rectangle_relation, RectRelation
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

    most_common_font: str
    most_common_size: int

    abnormal_size_pages: list[int]


@dataclass
class PageInParams(PageInputParams):
    raw_dict: dict
    drawings: list

@dataclass
class DocOutParams(DocOutputParams):
    core_y: Range


@dataclass
class PageOutParams(PageOutputParams):
    big_blocks: list[list] # column -> block


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class BigBlockWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        big_blocks: list[list] = [[] for _ in range(len(doc_in.big_text_columns))]

        if page_index in doc_in.abnormal_size_pages:
            return PageOutParams(big_blocks), LocalPageOutParams()

        blocks = [b for b in page_in.raw_dict["blocks"] if b["type"] == 0]

        for b in blocks:
            for i, column in enumerate(doc_in.big_text_columns):
                delta = (column.max - column.min) * 0.1
                delta = 0
                if column.min - delta <= b["bbox"][0] <= column.max + delta:
                    big_blocks[i].append(b)
                    # near_lines_count = 0
                    # for line in b["lines"]:
                    #     if line["bbox"][0] < column.min + 20:
                    #         near_lines_count += 1
                
                    # if (near_lines_count / len(b["lines"])) > 0.8 or (near_lines_count == 1 and len(b["lines"]) != 1):
                    #     big_blocks[i].append(b)
                    break


        def is_big_block(block):
            def is_in_width_range(block):
                return (
                    doc_in.big_text_width_range.min * 0.9
                    <= block["bbox"][2] - block["bbox"][0]
                    <= doc_in.big_text_width_range.max * 1.1
                )



            def is_line_y_increase(block):
                for i in range(len(block["lines"]) - 1):
                    if block["lines"][i]["bbox"][3] > block["lines"][i + 1]["bbox"][3]:
                        return False
                return True

            def is_common_text_too_little(block):
                sum_count = 0
                common_count = 0

                for line in block["lines"]:
                    for span in line["spans"]:
                        sum_count += len(span["chars"])
                        if is_common_span(span, doc_in.most_common_font, doc_in.most_common_size):
                            common_count += len(span["chars"])

                return common_count / sum_count > 0.5


            def is_not_be_contained(block):
                # deep_root 0
                for drawing in page_in.drawings:
                    if rectangle_relation(block["bbox"], drawing['rect']) == RectRelation.CONTAINED_BY:
                        return False
                return True
            

            judgers = [
                (is_in_width_range, True),
                (is_line_y_increase, False),
                (is_common_text_too_little, True),
                (is_not_be_contained, True),
            ]
            for judger, enabled in judgers:
                if enabled and not judger(block):
                    return False
            return True

        for i, blocks in enumerate(big_blocks):
            big_blocks[i] = list(filter(is_big_block, blocks))
            big_blocks[i] = sorted(big_blocks[i], key=lambda block: block["bbox"][1])

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
            min([b["bbox"][1] for b in block_list]),
            max([b["bbox"][3] for b in block_list]),
        )

        return DocOutParams(core_y)
