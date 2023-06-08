import yaml
from pathlib import Path
import fitz
from fitz import Document, Page
import shutil
import time
from htutil import file
from worker import Executer, ExecuterConfig, workers_dev  # type: ignore
import concurrent.futures
import common  # type: ignore

from common import version


def get_files_from_cfg():
    cfg = yaml.load(Path("./config.yaml").read_text(), Loader=yaml.FullLoader)

    dir_input = Path(cfg["path"]["input"])
    dir_output = Path(cfg["path"]["output"])

    for file in cfg["files"]:
        yield (dir_input / f"{file}.pdf"), (dir_output / file)


def get_files_from_dir():
    for file in Path("./data").glob("*.pdf"):
        yield (file, Path("./data") / file.stem)


logger = common.create_main_logger()
logger.info(f"version: {version}")


def create_task(file_input: Path, dir_output: Path):
    logger.info(f"start {file_input.name}")
    t = time.perf_counter()
    if dir_output.exists():
        shutil.rmtree(dir_output)
    dir_output.mkdir(parents=True)

    cfg = ExecuterConfig(version, True)  # type: ignore
    e = Executer(file_input, dir_output, cfg)
    e.register(workers_dev)
    e.execute()
    logger.info(f"end {file_input.name}, time = {time.perf_counter() - t:.2f}s")


with concurrent.futures.ProcessPoolExecutor() as executor:
    futures = [
        executor.submit(create_task, file_input, dir_output)
        for file_input, dir_output in get_files_from_cfg()
    ]
    for future in futures:
        future.result()
