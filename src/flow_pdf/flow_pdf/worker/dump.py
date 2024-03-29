from .common import PageWorker, is_common_span, get_min_bounding_rect, add_annot
from .common import (
    DocInputParams,
    PageInputParams,
    DocOutputParams,
    PageOutputParams,
    LocalPageOutputParams,
)

from dataclasses import dataclass

from htutil import file
from fitz import Page  # type: ignore
import fitz
import fitz.utils
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


@dataclass
class DocInParams(DocInputParams):
    most_common_font: str
    common_size_range: Range

    big_text_width_range: Range
    big_text_columns: list[Range]

    core_y: Range
    abnormal_size_pages: list[int]


@dataclass
class PageInParams(PageInputParams):
    big_blocks: list[list[MTextBlock]]  # column -> blocks
    page_info: MPage
    shot_rects: list[list[Shot]]  # column -> shots
    image_blocks: list[dict]
    images: list
    drawings: list
    inline_shots: list[ShotR]


@dataclass
class DocOutParams(DocOutputParams):
    pass


@dataclass
class PageOutParams(PageOutputParams):
    pass


@dataclass
class LocalPageOutParams(LocalPageOutputParams):
    pass


class DumpWorker(PageWorker):
    def __init__(self) -> None:
        super().__init__()

        self.disable_cache = True

    def run_page(  # type: ignore[override]
        self, page_index: int, doc_in: DocInParams, page_in: PageInParams
    ) -> tuple[PageOutParams, LocalPageOutParams]:
        with fitz.open(doc_in.file_input) as doc:  # type: ignore
            page: Page = doc.load_page(page_index)  # type: ignore


            page.get_pixmap(dpi=72*2).save(doc_in.dir_output / "raw" / f"{page_index}.png")  # type: ignore

            # block line
            # for block in page_in.page_info.get_text_blocks():
            #     rects = []
            #     for line in block.lines:
            #         rects.append(line.bbox)
            #     add_annot(page, rects, "", "red")

            # block span
            # rects = []
            # for blocks in page_in.big_blocks:
            #     for block in blocks:
            #         for line in block.lines:
            #             for span in line.spans:
            #                     rects.append(span.bbox)
            # add_annot(page, rects, "", "purple")

            # block common span
            # rects = []
            # for blocks in page_in.big_blocks:
            #     for block in blocks:
            #         for line in block.lines:
            #             for span in line.spans:
            #                 if is_common_span(span, doc_in.most_common_font, doc_in.common_size_range):
            #                     rects.append(span.bbox)
            # add_annot(page, rects, "", "purple")

            # block not common span
            # rects = []
            # for blocks in page_in.big_blocks:
            #     for block in blocks:
            #         for line in block.lines:
            #             for span in line.spans:
            #                 if not is_common_span(span, doc_in.most_common_font, doc_in.common_size_range):
            #                     rects.append(span.bbox)
            # add_annot(page, rects, "", "red")

            # inline shots
            add_annot(page, page_in.inline_shots, "", "blue")

            # new line
            # rects = []
            # for b in page_in.big_blocks:
            #     for i in range(1, len(b.lines)):
            #         line = b.lines[i]
            #         delta = line.bbox[0] - b.bbox[0]
            #         if delta > 1:
            #             last_line = b.lines[i - 1]
            #             if last_line.bbox[0] - b.bbox[0] < 1:
            #                 rects.append(line.bbox)
            # add_annot(page, rects, "new-line", "pink")

            # drawings
            # rects = []
            # for block in page_in.drawings:
            #     rects.append(block['rect'])
            # add_annot(page, rects, 'drawings', 'red')

            # image-block
            # rects = []
            # for block in page_in.image_blocks:
            #     rects.append(block.bbox)
            # add_annot(page, rects, "image-block", "red")

            # image
            # rects = []
            # for block in page_in.images:
            #     rects.append(block.bbox)
            # add_annot(page, rects, "image", "red")

            # shot in rect view
            # for c in page_in.shot_rects:
            #     for shot in c:
            #         add_annot(page, shot, "shot-r", "green")

            # big block
            for c in page_in.big_blocks:
                rects = []
                for block in c:
                    rects.append(block.bbox)
                add_annot(page, rects, "big-block", "blue")

            # big block line
            # for c in page_in.big_blocks:
            #     rects = []
            #     for block in c:
            #         for line in block.lines:
            #             rects.append(line.bbox)
            #     add_annot(page, rects, "", "purple")

            # shot in column view
            if page_index in doc_in.abnormal_size_pages:
                rects = page_in.shot_rects[0][0]
                add_annot(page, rects, "shot-abnormal-page", "green")
            else:
                for shots in page_in.shot_rects:
                    rects = []
                    for shot in shots:
                        rects.append(get_min_bounding_rect(shot))
                    add_annot(page, rects, "shot", "green")

            file.write_json(
                doc_in.dir_output / "shot_rects" / f"{page_index}.json",
                page_in.shot_rects,
            )

            # big column
            rects = []
            for column_range in doc_in.big_text_columns:
                r = Rectangle(
                    column_range.min - 3,
                    doc_in.core_y.min - 3,
                    column_range.max + 3,
                    doc_in.core_y.max + 3,
                )
                rects.append(r)
            add_annot(page, rects, "", "pink")

            page.get_pixmap(dpi=72*5).save(doc_in.dir_output / "marked" / f"{page_index}.png")  # type: ignore

        return PageOutParams(), LocalPageOutParams()

    def post_run_page(self, doc_in: DocInParams, page_in: list[PageInParams]):  # type: ignore[override]
        for p in ["marked", "raw", "shot_rects"]:
            (doc_in.dir_output / p).mkdir(parents=True, exist_ok=True)

    def after_run_page(  # type: ignore[override]
        self,
        doc_in: DocInParams,
        page_in: list[PageInParams],
        page_out: list[PageOutParams],
        local_page_out: list[LocalPageOutParams],
    ) -> DocOutParams:
        file.write_json(
            doc_in.dir_output / "meta.json", {"page_count": doc_in.page_count}
        )

        file_meta = doc_in.dir_output / "meta.json"
        file.write_json(
            file_meta,
            {
                "most_common_font": doc_in.most_common_font,
                "common_size_range": doc_in.common_size_range,
                "big_text_width_range": doc_in.big_text_width_range,
                "big_text_columns": doc_in.big_text_columns,
                "core_y": doc_in.core_y,
                "abnormal_size_pages": doc_in.abnormal_size_pages,
            },
        )

        big_blocks_id: list[list[int]] = [[] for _ in range(len(page_in))]
        for i, page in enumerate(page_in):
            for bs in page.big_blocks:
                for b in bs:
                    big_blocks_id[i].append(b.number)
        file.write_json(doc_in.dir_output / "big_blocks_id.json", big_blocks_id)

        return DocOutParams()
