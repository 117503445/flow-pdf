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



# return dir_data and files
def get_files()->tuple[Path, list[Path]]:
    eventsENV = os.getenv("FC_CUSTOM_CONTAINER_EVENT")
    if eventsENV:
        logger.info("FC MODE")
        events: dict = json.loads(eventsENV)["events"]
        if len(events) == 0:
            logger.error("events is empty")
            exit(1)
        dir_data = Path("/data/nougat")
        files = [Path(event["oss"]["object"]["key"]) for event in events]
        return dir_data, files
    elif Path('/local-data').exists():
        logger.info("LOCAL MODE")
        dir_data = Path('/local-data')
        files = [f for f in dir_data.glob('**/*.pdf')]
        return dir_data, files
    else:
        logger.error("NO MODE DETECTED")
        exit(1)

dir_data, files = get_files()

dir_input = dir_data / "input"
dir_output = dir_data / "output"
dir_input.mkdir(parents=True, exist_ok=True)
dir_output.mkdir(parents=True, exist_ok=True)

def process_file(f: Path):
    logger.info(f"processing {f.name}")
    stem = Path(f).stem

    file_task = dir_output / stem / "task.json"
    file_doc = dir_output / stem / "output" / "doc.json"

    if file_doc.exists():
        logger.info(f"file_doc exists")
        doc = file.read_json(file_doc)
        if doc["meta"]["flow-pdf-version"] == version:
            logger.info(f"file_doc version is same, skip")
            return
        else:
            logger.info(f'clean old version {doc["meta"]["flow-pdf-version"]}')
            shutil.rmtree(dir_output / stem)

    file_input = dir_input / f"{stem}.pdf"

    logger.info(f"start {file_input.name}")

    file.write_json(file_task, {"status": "executing"})

    try:
        command = f'nougat {file_input} -o {dir_output / stem / "output"} -m 0.1.0-base --markdown'
        logger.debug(f'nougat command = {command}')
        subprocess.run(command, shell=True)

        file_mmd = dir_output / stem / "output" / f'{stem}.mmd'
        if not file_mmd.exists():
            raise Exception(f'{file_mmd} not exists')
        file_html = dir_output / stem / "output" / f'{stem}.html'

        command = f'node app.js --input {file_mmd} --output {file_html}'
        logger.debug(f'mmd-converter command = {command}')
        subprocess.run(command, shell=True, cwd='./mmd-converter')
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

for f in files:
    process_file(f)