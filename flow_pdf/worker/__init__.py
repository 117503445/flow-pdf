from .common import Worker, Executer, ExecuterConfig

from .read_doc import ReadDocWorker
from .pre_dump import PreDumpWorker
from .dump import DumpWorker
from .image import ImageWorker
from .font_counter import FontCounterWorker
from .width_counter import WidthCounterWorker
from .big_block import BigBlockWorker
from .shot import ShotWorker
from .json_gen import JSONGenWorker
from .html_gen import HTMLGenWorker

workers_prod = [
    ReadDocWorker,
    FontCounterWorker,
    ImageWorker,
    WidthCounterWorker,
    BigBlockWorker,
    ShotWorker,
    JSONGenWorker,
    HTMLGenWorker,
]

workers_dev = workers_prod.copy()
workers_dev.insert(workers_dev.index(ReadDocWorker) + 1, PreDumpWorker)
workers_dev.append(DumpWorker)
