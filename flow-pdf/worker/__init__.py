from .common import Worker, Executer
from .read_doc import ReadDocWorker
from .dump import DumpWorker
from .image import ImageWorker
from .font_counter import FontCounterWorker

workers = [ReadDocWorker, FontCounterWorker, ImageWorker, DumpWorker]
