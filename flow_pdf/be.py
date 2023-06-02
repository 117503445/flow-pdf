from fastapi import FastAPI, File, UploadFile
import hashlib
from pathlib import Path
from htutil import file
import concurrent.futures
import common  # type: ignore
import time
from worker import Executer, workers  # type: ignore

dir_data = Path("./web-data")
dir_input = dir_data / "input"
dir_output = dir_data / "output"

for dir in [dir_data, dir_input]:
    if not dir.exists():
        dir.mkdir(parents=True)

app = FastAPI()

logger = common.create_main_logger()


def create_task(file_input: Path, dir_output: Path):
    logger.info(f"start {file_input.name}")
    t = time.perf_counter()

    dir_output.mkdir(parents=True)

    e = Executer(file_input, dir_output)
    e.register(workers)
    e.execute()
    logger.info(f"end {file_input.name}, time = {time.perf_counter() - t:.2f}s")


poolExecutor = concurrent.futures.ProcessPoolExecutor()


def make_common_data(code: int, msg: str, data):
    return {"code": code, "msg": msg, "data": data}


@app.get("/")
def hello():
    return make_common_data(0, "Hello", None)


@app.post("/api/task")
async def parse_pdf(file: UploadFile):
    content = await file.read()
    # task id is the sha256 hash of file content
    task_id = hashlib.sha256(content).hexdigest()
    with open(dir_input / f"{task_id}.pdf", "wb") as buffer:
        buffer.write(content)

    poolExecutor.submit(create_task, dir_input / f"{task_id}.pdf", dir_output / task_id)

    return make_common_data(0, "Success", {"taskID": task_id})


# @app.get("/api/task/{task_id}")
# async def query_task(task_id: str):
#     dir_input_task = dir_input / f'{task_id}.pdf'
#     dir_output_task = dir_output / task_id
#     if not dir_input_task.exists():
#         return make_common_data(1, "Task not found", None)

#     if not dir_output_task.exists():
#         return make_common_data(1, "Task is pending", None)

#     file_layout = dir_output_task / 'layout.json'

#     if not file_layout.exists():
#         return make_common_data(2, "Task is executing", None)

#     return make_common_data(0, "Success", file.read_json(file_layout))
