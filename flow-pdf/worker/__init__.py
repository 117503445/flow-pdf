from .common import Worker, Executer
from .read_doc_worker import ReadDocWorker
from .dump_worker import DumpWorker
from .image_worker import ImageWorker

workers = [ReadDocWorker, DumpWorker, ImageWorker]