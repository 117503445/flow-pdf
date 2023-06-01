from .common import Worker, Executer
from .read_doc import ReadDocWorker
from .dump import DumpWorker
from .image import ImageWorker
from .font_counter import FontCounterWorker
from .width_counter import WidthCounterWorker

workers = [ReadDocWorker, FontCounterWorker, ImageWorker,WidthCounterWorker, DumpWorker]
