from .common import PageWorker, Block, Range, get_min_bounding_rect
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
    big_text_columns: list[Range]

    core_y: Range


@dataclass
class PageInParams(PageInputParams):
    big_blocks: list
    raw_dict: dict
    drawings: list


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    shot_rects: list


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


def rectangle_relation(
    rect1: tuple[float, float, float, float], rect2: tuple[float, float, float, float]
):
    x1, y2, x2, y1 = rect1
    x3, y4, x4, y3 = rect2

    if x1 >= x4 or x2 <= x3 or y1 <= y4 or y2 >= y3:
        return "not intersect"  # 不相交

    elif x1 >= x3 and x2 <= x4 and y1 <= y3 and y2 >= y4:
        return "contains"  # 包含

    elif x1 <= x3 and x2 >= x4 and y1 >= y3 and y2 <= y4:
        return "contained by"  # 被包含

    else:
        return "intersect"  # 相交


class ShotWorker(PageWorker):
    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        column_shots: list[list[list[tuple[float, float, float, float]]]] = []

        # shot between big blocks
        for column in doc_in.big_text_columns:
            shots: list[list[tuple[float, float, float, float]]] = []

            elements_rect = [
                b
                for b in page_in.big_blocks
                if column.min * 0.9 <= b["bbox"][0] <= column.max * 1.1
            ]
            elements_rect.sort(key=lambda x: x["bbox"][1])
            last_y = doc_in.core_y.min
            for block in elements_rect:
                r = (column.min, last_y, column.max, block["bbox"][1])
                if r[3] - r[1] > 0:
                    shots.append([r])
                else:
                    self.logger.warning(f"r.y1 <= r.y0, r = {r}")
                last_y = block["bbox"][3]
            shots.append([(column.min, last_y, column.max, doc_in.core_y.max)])

            column_shots.append(shots)

        elements_rect = []
        for block in page_in.raw_dict["blocks"]:
            elements_rect.append(block["bbox"])
        for draw in page_in.drawings:
            elements_rect.append(draw["rect"])

        # extend first rect in each column

        for shots in column_shots:
            if len(shots) == 0:
                continue
            first_shot = shots[0]
            if len(first_shot) != 1:
                raise Exception("len(first_shot) != 1")

            intersect_rects = []  # elements intersect with rect
            for r in elements_rect:
                if rectangle_relation(first_shot[0], r) == "intersect":
                    intersect_rects.append(r)

            if not intersect_rects:
                continue

            min_y0 = min([r[1] for r in intersect_rects])
            min_y0 = min(min_y0, first_shot[0][1])
            first_shot[0] = (
                first_shot[0][0],
                min_y0,
                first_shot[0][2],
                first_shot[0][3],
            )

        # delete empty rects
        BORDER_WIDTH = 4
        for shots in column_shots:
            for i in reversed(range(len(shots))):
                shot = shots[i]
                if len(shot) != 1:
                    raise Exception("len(shot) != 1")

                # delete height too small
                if shot[0][3] - shot[0][1] <= BORDER_WIDTH * 2:
                    del shots[i]
                    continue

                inner_rect = (
                    shot[0][0] + BORDER_WIDTH,
                    shot[0][1] + BORDER_WIDTH,
                    shot[0][2] - BORDER_WIDTH,
                    shot[0][3] - BORDER_WIDTH,
                )
                is_found = False
                for r in elements_rect:
                    if rectangle_relation(inner_rect, r) != "not intersect":
                        is_found = True
                        break
                if not is_found:
                    del shots[i]

        # merge shot in different columns

        def is_near(shot1, shot2):
            rect1 = get_min_bounding_rect(shot1)
            rect2 = get_min_bounding_rect(shot2)
            for r in elements_rect:
                if (
                    rectangle_relation(rect1, r) == "intersect"
                    and rectangle_relation(rect2, r) == "intersect"
                ):
                    return True
            return False

        for i, shots in enumerate(column_shots):
            if i == len(column_shots) - 1:
                # The last column does not need to be merged
                break

            for j in range(len(shots)):
                first_shot = shots[j]

                # TODO ZmICE1 - 2.png
                for other_c_index in range(i + 1, len(column_shots)):
                    is_find_near = False
                    next_c = column_shots[other_c_index]
                    for k in range(len(next_c)):
                        next_shot = next_c[k]
                        if is_near(first_shot, next_shot):
                            is_find_near = True
                            shots[j].extend(next_shot)
                            del next_c[k]
                            break
                    if not is_find_near:
                        break

        # prepare output
        shots = []
        for c in column_shots:
            shots.extend(c)

        return PageOutParams(shots), LocalPageOutParams()
