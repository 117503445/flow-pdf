from .common import (
    PageWorker,
    get_min_bounding_rect,
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
    Shot,
    ShotR,
)
from typing import Union
from dataclasses import dataclass


@dataclass
class DocInParams(DocInputParams):
    big_text_columns: list[Range]

    core_y: Range

    abnormal_size_pages: list[int]


@dataclass
class PageInParams(PageInputParams):
    # big_blocks: list[list[MTextBlock]]  # column -> blocks
    page_info: MPage
    drawings: list

    width: int
    height: int

    text_blocks_bbox: list[list[Rectangle]] # column -> bbox, for shot


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    shot_rects: list[list[Shot]]  # column -> shots


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


def shot_between_blocks(
    column_shots: list[list[Shot]], doc_in: DocInParams, page_in: PageInParams
):
    for i, column in enumerate(doc_in.big_text_columns):
        shots: list[Shot] = []

        last_y = doc_in.core_y.min
        for bbox in page_in.text_blocks_bbox[i]:
            r = (column.min, last_y, column.max, bbox.y0)
            if r[3] - r[1] > 0:
                shots.append([Rectangle(r[0], r[1], r[2], r[3])])
            last_y = bbox.y1
        
        if doc_in.core_y.max - last_y > 0:
            shots.append([Rectangle(column.min, last_y, column.max, doc_in.core_y.max)])

        column_shots[i] = shots


class ShotWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        column_shots: list[list[Shot]] = [
            [] for _ in range(len(doc_in.big_text_columns))
        ]  # column -> shots

        if page_index in doc_in.abnormal_size_pages:
            column_shots[0].append([Rectangle(0, 0, page_in.width, page_in.height)])
            return PageOutParams(column_shots), LocalPageOutParams()

        try:
            shot_between_blocks(column_shots, doc_in, page_in)
        except Exception as e:
            self.logger.error(f"shot_between_blocks, page_index = {page_index}, error: {e}")
            raise e

        elements_rect: list[Rectangle] = []
        for block in page_in.page_info.blocks:
            elements_rect.append(block.bbox)
        for draw in page_in.drawings:
            elements_rect.append(draw["rect"])

        # remove top and bottom blank
        for shots in column_shots:
            for i in reversed(range(len(shots))):
                shot = shots[i]
                if len(shot) != 1:
                    raise Exception("len(shot) != 1")

                except_intersect_rects = []
                for r in elements_rect:
                    if rectangle_relation(shot[0], r) != RectRelation.NOT_INTERSECT:
                        except_intersect_rects.append(r)
                if except_intersect_rects:
                    min_y0 = min([r.y0 for r in except_intersect_rects])
                    min_y0 = max(min_y0, shot[0].y0)
                    max_y1 = max([r.y1 for r in except_intersect_rects])
                    max_y1 = min(max_y1, shot[0].y1)
                    shot[0] = Rectangle(shot[0].x0, min_y0, shot[0].x1, max_y1)

        # extend first rect in each column
        for shots in column_shots:
            if len(shots) == 0:
                continue
            first_shot = shots[0]
            if len(first_shot) != 1:
                raise Exception("len(first_shot) != 1")

            intersect_rects: list[Rectangle] = []  # elements intersect with rect
            for r in elements_rect:
                if rectangle_relation(first_shot[0], r) == RectRelation.INTERSECT:
                    intersect_rects.append(r)

            if not intersect_rects:
                continue

            min_y0 = min([r.y0 for r in intersect_rects])
            min_y0 = min(min_y0, first_shot[0].y0)
            first_shot[0] = Rectangle(
                first_shot[0].x0,
                min_y0,
                first_shot[0].x1,
                first_shot[0].y1,
            )

        # extend left
        if column_shots:
            column = column_shots[0]
            for i in range(len(column)):
                if len(column[i]) != 1:
                    raise Exception("len(column[i]) != 1")
                shot = column[i]
                min_x0 = shot[0].x0
                for r in elements_rect:
                    if rectangle_relation(shot[0], r) == RectRelation.INTERSECT:
                        min_x0 = min(min_x0, r.x0)
                shot[0] = Rectangle(min_x0, shot[0].y0, shot[0].x1, shot[0].y1)

        # extend right
        if column_shots:
            column = column_shots[-1]
            for i in range(len(column)):
                if len(column[i]) != 1:
                    raise Exception("len(column[i]) != 1")
                shot = column[i]
                max_x1 = shot[0].x1
                for r in elements_rect:
                    if rectangle_relation(shot[0], r) == RectRelation.INTERSECT:
                        max_x1 = max(max_x1, r.x1)
                shot[0] = Rectangle(shot[0].x0, shot[0].y0, max_x1, shot[0].y1)

        # delete empty rects
        BORDER_WIDTH = 4
        for shots in column_shots:
            for i in reversed(range(len(shots))):
                shot = shots[i]
                if len(shot) != 1:
                    raise Exception("len(shot) != 1")

                # delete height too small
                if shot[0].y1 - shot[0].y0 <= BORDER_WIDTH * 2:
                    del shots[i]
                    continue

                inner_rect = Rectangle(
                    shot[0].x0 + BORDER_WIDTH,
                    shot[0].y0 + BORDER_WIDTH,
                    shot[0].x1 - BORDER_WIDTH,
                    shot[0].y1 - BORDER_WIDTH,
                )
                is_found = False
                for r in elements_rect:
                    if rectangle_relation(inner_rect, r) != RectRelation.NOT_INTERSECT:
                        is_found = True
                        break
                if not is_found:
                    del shots[i]

        # merge shot in different columns

        def is_near(shot1: Shot, shot2: Shot):
            rect1 = get_min_bounding_rect(shot1)
            rect2 = get_min_bounding_rect(shot2)
            for r in elements_rect:
                if (
                    rectangle_relation(rect1, r) == RectRelation.INTERSECT
                    and rectangle_relation(rect2, r) == RectRelation.INTERSECT
                ):
                    return True
            return False

        for i, shots in enumerate(column_shots):
            if i == len(column_shots) - 1:
                # The last column does not need to be merged
                break

            for j in range(len(shots)):
                cur_shot = shots[j]

                # TODO ZmICE1 - 2.png
                for other_c_index in range(i + 1, len(column_shots)):
                    next_c = column_shots[other_c_index]
                    is_find_near = False
                    for k in range(len(next_c)):
                        next_shot = next_c[k]
                        if is_near(cur_shot, next_shot):
                            is_find_near = True
                            shots[j].extend(next_shot)
                            del next_c[k]
                            break
                    if not is_find_near:
                        break

        return PageOutParams(column_shots), LocalPageOutParams()
