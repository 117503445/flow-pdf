import logging
from htutil import file
from pathlib import Path
import os
import json
from pathlib import Path
import shutil
import traceback
import subprocess

def create_main_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s,%(msecs)03d [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    return logger

logger = create_main_logger()

file_git = Path(__file__).parent / "git.txt"
if file_git.exists():
    version = file.read_text(file_git)
else:
    version = 'dev'

if version == "dev":
    logger.warning("dev mode, version is not set")
else:
    logger.info(f"version: {version}")

eventsStr = os.getenv("FC_CUSTOM_CONTAINER_EVENT")

if not eventsStr:
    logger.error("FC_CUSTOM_CONTAINER_EVENT is not set")
    exit(1)

events: dict = json.loads(eventsStr)["events"]
if len(events) == 0:
    logger.error("events is empty")
    exit(1)

dir_data = Path("/data/nougat")
dir_input = dir_data / "input"
dir_output = dir_data / "output"
dir_input.mkdir(parents=True, exist_ok=True)
dir_output.mkdir(parents=True, exist_ok=True)

for event in events:
    file_k: str = event["oss"]["object"]["key"]
    stem = Path(file_k).stem

    file_task = dir_output / stem / "task.json"
    file_doc = dir_output / stem / "output" / "doc.json"

    if file_doc.exists():
        logger.info(f"file_doc exists")
        doc = file.read_json(file_doc)
        if doc["meta"]["flow-pdf-version"] == version:
            logger.info(f"file_doc version is same, skip")
            continue
        else:
            logger.info(f'clean old version {doc["meta"]["flow-pdf-version"]}')
            shutil.rmtree(dir_output / stem)

    file_input = dir_input / f"{stem}.pdf"

    logger.info(f"start {file_input.name}")

    file.write_json(file_task, {"status": "executing"})

    try:
        command = f'nougat {file} -o {dir_output / stem / "output"} -m 0.1.0-base --markdown'
        logger.debug(f'command = {command}')
        subprocess.run(command, shell=True)
        file.write_json(file_task, {"status": "done"})
        logger.info(f"{file_input.name} success")
    except Exception as e:
        file.write_json(
            file_task,
            {
                "status": "error",
                "error": str(e),
            },
        )
        logger.error(f"{file_input.name} error")
        traceback.print_exc()

    logger.info(f"end {file_input.name}")
