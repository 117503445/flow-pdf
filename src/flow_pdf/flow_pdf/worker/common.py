from pathlib import Path
import inspect
import time
import fitz
import concurrent.futures
from dataclasses import dataclass, fields, asdict
import fitz.utils
from htutil import file
import logging
from enum import Enum
from fitz import Page  # type: ignore
from .flow_type import Rectangle, Range, MSpan

fitz.TOOLS.set_small_glyph_heights(True)


@dataclass
class DocInputParams:
    file_input: Path
    dir_output: Path
    page_count: int


@dataclass
class PageInputParams:
    pass


@dataclass
class DocOutputParams:
    pass


@dataclass
class PageOutputParams:
    pass


@dataclass
class LocalPageOutputParams:
    pass


class Worker:
    logger: logging.Logger
    version: str
    cache_enabled: bool

    def post_run(
        self, doc_in: DocInputParams, page_in: list[PageInputParams]
    ) -> tuple[DocOutputParams, list[PageOutputParams]]:
        try:
            success, result = self.load_cache(doc_in, page_in)
        except Exception as e:
            self.logger.warning(
                f"warning: {self.__class__.__name__} load_cache error: {e}"
            )
            success, result = False, (DocOutputParams(), [])

        if success:
            self.logger.debug("[cached]")
            return result

        doc_out, page_out = self.run(doc_in, page_in)

        self.save_cache(doc_in, page_in, doc_out, page_out)
        return doc_out, page_out

    def run(
        self, doc_in: DocInputParams, page_in: list[PageInputParams]
    ) -> tuple[DocOutputParams, list[PageOutputParams]]:
        return (DocOutputParams(), [])

    def load_cache(
        self, doc_in: DocInputParams, page_in: list[PageInputParams]
    ) -> tuple[bool, tuple[DocOutputParams, list[PageOutputParams]]]:
        if not self.cache_enabled or self.__dict__.get("disable_cache"):
            return False, (DocOutputParams(), [])

        file_pkl = (
            Path("/tmp")
            / "flow-pdf"
            / "cache"
            / doc_in.file_input.name
            / f"{self.__class__.__name__}.pkl"
        )
        if not file_pkl.exists():
            return False, (DocOutputParams(), [])

        d = file.read_pkl(file_pkl)
        if (
            d["src"] != inspect.getsource(self.__class__)
            or d["doc_in"] != doc_in
            or d["page_in"] != page_in
        ):
            return False, (DocOutputParams(), [])

        return True, (d["doc_out"], d["page_out"])

    def save_cache(
        self,
        doc_in: DocInputParams,
        page_in: list[PageInputParams],
        doc_out: DocOutputParams,
        page_out: list[PageOutputParams],
    ):
        if not self.cache_enabled or self.__dict__.get("disable_cache"):
            return

        file_pkl = (
            Path("/tmp")
            / "flow-pdf"
            / "cache"
            / doc_in.file_input.name
            / f"{self.__class__.__name__}.pkl"
        )
        file_pkl.parent.mkdir(parents=True, exist_ok=True)

        file.write_pkl(
            file_pkl,
            {
                "src": inspect.getsource(self.__class__),
                "doc_in": doc_in,
                "page_in": page_in,
                "doc_out": doc_out,
                "page_out": page_out,
            },
        )


class PageWorker(Worker):
    def run(
        self, doc_in: DocInputParams, page_in: list[PageInputParams]
    ) -> tuple[DocOutputParams, list[PageOutputParams]]:
        page_result, local_page_result = self.run_page_parallel(doc_in, page_in)

        doc_result = self.after_run_page(
            doc_in, page_in, page_result, local_page_result
        )

        return (doc_result, page_result)

    def run_page_parallel(
        self, doc_in: DocInputParams, page_in: list[PageInputParams]
    ) -> tuple[list[PageOutputParams], list[LocalPageOutputParams]]:
        self.post_run_page(doc_in, page_in)

        page_out = []
        local_page_out = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(self.run_page, page_index, doc_in, page_in[page_index])
                for page_index in range(doc_in.page_count)
            ]
            for future in futures:
                p_out, l_p_out = future.result()
                page_out.append(p_out)
                local_page_out.append(l_p_out)
            return page_out, local_page_out

    def post_run_page(self, doc_in: DocInputParams, page_in: list[PageInputParams]):
        pass

    def run_page(
        self, page_index: int, doc_in: DocInputParams, page_in: PageInputParams
    ) -> tuple[PageOutputParams, LocalPageOutputParams]:
        raise NotImplementedError()

    def after_run_page(
        self,
        doc_in: DocInputParams,
        page_in: list[PageInputParams],
        page_out: list[PageOutputParams],
        local_page_out: list[LocalPageOutputParams],
    ) -> DocOutputParams:
        return DocOutputParams()


def create_logger(file_input: Path, dir_output: Path):
    logger = logging.getLogger(file_input.stem)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(dir_output / "log.txt")

    formatter = logging.Formatter(
        "%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


@dataclass
class ExecuterConfig:
    version: str
    cache_enabled: bool


class Executer:
    def __init__(self, file_input: Path, dir_output: Path, config: ExecuterConfig):
        with fitz.open(file_input) as doc:  # type: ignore
            page_count = doc.page_count

        self.store = ParamsStore(page_count)
        self.store.doc_set("file_input", file_input)
        self.store.doc_set("dir_output", dir_output)

        self.logger = create_logger(file_input, dir_output)
        self.config = config

    def register(self, workers: list[type]):
        self.workers = workers

    def execute(self):
        for W in self.workers:
            self.logger.info(f"{W.__name__} start")
            start = time.perf_counter()

            if issubclass(W, PageWorker):
                w_method = W.run_page
            elif issubclass(W, Worker):
                w_method = W.run
            else:
                self.logger.warning(f"{W.__name__} is not a worker")
                continue

            k = "doc_in"
            k_class = w_method.__annotations__[k]  # type: ignore
            param_names = [f.name for f in fields(k_class)]
            params = [self.store.doc_get(n) for n in param_names]
            doc_in = k_class(*params)

            k = "page_in"
            if issubclass(W, PageWorker):
                k_class = w_method.__annotations__[k]  # type: ignore
            elif issubclass(W, Worker):
                k_class = w_method.__annotations__[k].__args__[0]  # type: ignore

            param_names = [f.name for f in fields(k_class)]
            page_in = []
            for i in range(self.store.doc_get("page_count")):
                params = [self.store.page_get(n, i) for n in param_names]
                page_in.append(k_class(*params))

            w = W()
            w.logger = self.logger
            w.version = self.config.version
            w.cache_enabled = self.config.cache_enabled

            doc_out, page_out = w.post_run(doc_in, page_in)
            for k, v in asdict(doc_out).items():
                self.store.doc_set(k, v)
            for i, p in enumerate(page_out):
                for k, v in asdict(p).items():
                    self.store.page_set(k, i, v)

            self.logger.info(
                f"{W.__name__} finished, time = {(time.perf_counter() - start):.2f}s"
            )


class ParamsStore:
    def __init__(self, page_count: int):
        self.doc_params = {"page_count": page_count}
        self.page_params: list = [{} for _ in range(page_count)]

    def doc_get(self, name: str):
        return self.doc_params[name]

    def doc_set(self, name: str, value):
        self.doc_params[name] = value

    def page_get(self, name: str, page_index: int):
        return self.page_params[page_index][name]

    def page_set(self, name: str, page_index: int, value):
        # print(f"set page{page_index}.[{name}]")
        # if name in self.page_params[page_index]:
        #     raise Exception(f"page{page_index}.[{name}] already set")
        self.page_params[page_index][name] = value


def is_common_span(
    span: MSpan, most_common_font: str, common_size_range: Range
) -> bool:
    if most_common_font and span.font != most_common_font:
        return False
    if common_size_range:
        if span.size < common_size_range.min or span.size > common_size_range.max:
            return False
    return True


def get_min_bounding_rect(rects: list[Rectangle]) -> Rectangle:
    x0 = min(rects, key=lambda r: r.x0).x0
    y0 = min(rects, key=lambda r: r.y0).y0
    x1 = max(rects, key=lambda r: r.x1).x1
    y1 = max(rects, key=lambda r: r.y1).y1
    return Rectangle(x0, y0, x1, y1)


class RectRelation(Enum):
    NOT_INTERSECT = 0  # 不相交
    CONTAINS = 1  # 1 包含 2
    CONTAINED_BY = 2  # 1 被 2 包含
    INTERSECT = 3  # 相交


def rectangle_relation(rect1: Rectangle, rect2: Rectangle) -> RectRelation:
    # 解析矩形参数
    x1_1, y1_1, x2_1, y2_1 = rect1.x0, rect1.y0, rect1.x1, rect1.y1
    x1_2, y1_2, x2_2, y2_2 = rect2.x0, rect2.y0, rect2.x1, rect2.y1

    # 检查是否相交
    if x2_1 <= x1_2 or x1_1 >= x2_2 or y2_1 <= y1_2 or y1_1 >= y2_2:
        return RectRelation.NOT_INTERSECT

    # 检查是否包含
    if x1_1 <= x1_2 and y1_1 <= y1_2 and x2_1 >= x2_2 and y2_1 >= y2_2:
        return RectRelation.CONTAINS
    if x1_2 <= x1_1 and y1_2 <= y1_1 and x2_2 >= x2_1 and y2_2 >= y2_1:
        return RectRelation.CONTAINED_BY

    # 如果不相交，也不包含，则两个矩形必定相交
    return RectRelation.INTERSECT


def add_annot(page: Page, rects: list[Rectangle], annot: str, color: str):
    if not rects:
        return

    for i, rect in enumerate(rects):
        if annot:
            a = f"{annot}-{i}"
            page.add_freetext_annot(
                # (rect[0], rect[1], rect[0] + len(a) * 6, rect[1] + 10),
                (rect.x1 - len(a) * 6, rect.y0, rect.x1, rect.y0 + 10),
                a,
                fill_color=fitz.utils.getColor("white"),
                border_color=fitz.utils.getColor("black"),
            )

        r = fitz.Rect(*rect.to_tuple())

        # r = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)  # type: ignore
        page.draw_rect(r, color=fitz.utils.getColor(color))  # type: ignore


def frequent_sub_array(arr: list[float], sub_arr_range: float) -> list[float]:
    """
    Returns a contiguous subarray of arr with the most elements, and the difference between the maximum and minimum values of that subarray is less than sub_arr_range
    """

    if len(arr) == 0:
        raise ValueError("arr is empty")

    arr.sort()

    max_start = 0
    max_end = 0
    max_len = 1

    start = 0
    end = 0
    while end < len(arr):
        if arr[end] - arr[start] > sub_arr_range:
            start += 1
        else:
            if end - start + 1 > max_len:
                max_len = end - start + 1
                max_start = start
                max_end = end
            end += 1

    return arr[max_start : max_end + 1]
