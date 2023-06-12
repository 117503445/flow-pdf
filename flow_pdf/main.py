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

cfg = yaml.load(Path("./config.yaml").read_text(), Loader=yaml.FullLoader)

def get_files_from_cfg():
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

if cfg['compare']['enabled']:
    dir_target = Path(cfg['compare']['target'])
    for _, dir_output in get_files_from_cfg():
        dir_t = dir_target / dir_output.stem
        file_t = dir_t / "big_blocks_id" / 'big_blocks_id.json'
        if not file_t.exists():
            logger.warning(f"target file not found: {file_t}")
            continue

        cur = file.read_json(dir_output  / 'big_blocks_id.json')
        expect = file.read_json(file_t)

        if cur != expect:
            logger.debug(f'{dir_output.stem} changed')
            for i in range(len(cur)):
                if cur[i] != expect[i]:
                    add_list = []
                    del_list = []
                    for j in range(len(cur[i])):
                        if cur[i][j] not in expect[i]:
                            add_list.append(cur[i][j])
                    for j in range(len(expect[i])):
                        if expect[i][j] not in cur[i]:
                            del_list.append(expect[i][j])
                    logger.debug(f'page {i}, add: {add_list}, del: {del_list}')
