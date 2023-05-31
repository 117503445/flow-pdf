from pathlib import Path
import inspect
import time
import fitz


class Worker:
    pass


class PageWorker(Worker):
    pass


class Executer:
    def __init__(self, file_input: Path, dir_output: Path):
        with fitz.open(file_input) as doc:  # type: ignore
            page_count = doc.page_count

        self.store = ParamsStore(page_count)
        self.store.doc_set("file_input", file_input)
        self.store.doc_set("dir_output", dir_output)

    def register(self, workers: list[type]):
        self.workers = workers

    def execute(self):
        for w in self.workers:
            print(f'{w.__name__} start')
            start = time.perf_counter()

            k = "doc_in"
            k_class = w.run.__annotations__[k] # type: ignore
            param_names = k_class._fields
            params = [self.store.doc_get(n) for n in param_names]
            doc_in = k_class(*params)

            k = "page_in"
            k_class = w.run.__annotations__[k].__args__[0] # type: ignore
            param_names = k_class._fields
            page_in = []
            for i in range(self.store.doc_get("page_count")):
                params = [self.store.page_get(n, i) for n in param_names]
                page_in.append(k_class(*params))

            doc_out, page_out = w().run(doc_in, page_in)
            for k, v in doc_out._asdict().items():
                self.store.doc_set(k, v)
            for i, p in enumerate(page_out):
                for k, v in p._asdict().items():
                    self.store.page_set(k, i, v)
            print(f'{w.__name__} finished, time = {(time.perf_counter() - start):.2f}s')


class ParamsStore:
    def __init__(self, page_count: int):
        self.doc_params = {"page_count": page_count}
        self.page_params = [{}] * page_count

    def doc_get(self, name: str):
        return self.doc_params[name]

    def doc_set(self, name: str, value):
        self.doc_params[name] = value

    def page_get(self, name: str, page_index: int):
        return self.page_params[page_index][name]

    def page_set(self, name: str, page_index: int, value):
        self.page_params[page_index][name] = value
