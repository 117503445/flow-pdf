import yaml
from pathlib import Path
import fitz
from fitz import Document, Page
import shutil
import time
from htutil import file
from worker import Executer, workers  # type: ignore
import concurrent.futures
import common  # type: ignore

version = file.read_text(Path(__file__).parent / "git.txt")

print(f"version: {version}")


def get_files_from_cfg():
    cfg = yaml.load(Path("./config.yaml").read_text(), Loader=yaml.FullLoader)
    for file in cfg["files"]:
        yield (Path(file["input"]), Path(file["output"]))


def get_files_from_dir():
    for file in Path("./data").glob("*.pdf"):
        yield (file, Path("./data") / file.stem)


logger = common.create_main_logger()


def create_task(file_input: Path, dir_output: Path):
    logger.info(f"start {file_input.name}")
    t = time.perf_counter()
    if dir_output.exists():
        shutil.rmtree(dir_output)
    dir_output.mkdir(parents=True)

    e = Executer(file_input, dir_output)
    e.register(workers)
    e.execute()
    logger.info(f"end {file_input.name}, time = {time.perf_counter() - t:.2f}s")


with concurrent.futures.ProcessPoolExecutor() as executor:
    futures = [
        executor.submit(create_task, file_input, dir_output)
        for file_input, dir_output in get_files_from_cfg()
    ]
    for future in futures:
        future.result()
