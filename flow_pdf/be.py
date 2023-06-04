from fastapi import FastAPI, File, UploadFile
import hashlib
from pathlib import Path
from htutil import file
import concurrent.futures
import common  # type: ignore
import time
from worker import Executer, workers  # type: ignore
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from common import version


dir_data = Path("./web-data")
dir_input = dir_data / "input"
dir_output = dir_data / "output"

dir_fe = Path(__file__).parent.parent / "fe" / "dist"

for dir in [dir_data, dir_input, dir_output]:
    dir.mkdir(parents=True, exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO Clean failed task

logger = common.create_main_logger()
logger.info(f"version: {version}")

def create_task(file_input: Path, dir_output: Path):
    logger.info(f"start {file_input.name}")
    t = time.perf_counter()

    file_task = dir_output / "task.json"

    file.write_json(
        file_task,
        {
            "status": "executing",
        },
    )

    # TODO: log.txt
    e = Executer(file_input, dir_output, version)
    e.register(workers)
    e.execute()

    file.write_json(
        file_task,
        {
            "status": "done",
        },
    )

    logger.info(f"end {file_input.name}, time = {time.perf_counter() - t:.2f}s")


poolExecutor = concurrent.futures.ProcessPoolExecutor()


def make_common_data(code: int, msg: str, data):
    return {"code": code, "msg": msg, "data": data}


@app.get("/api/hello")
def hello():
    return make_common_data(0, "Hello", None)


@app.post("/api/task")
async def parse_pdf(f: UploadFile):
    content = await f.read()
    # task id is the sha256 hash of file content
    task_id = hashlib.sha256(content).hexdigest()

    dir_task = dir_output / task_id

    file_task = dir_task / "task.json"
    if file_task.exists():
        return make_common_data(0, "Success", {"taskID": task_id})

    with open(dir_input / f"{task_id}.pdf", "wb") as buffer:
        buffer.write(content)

    dir_output.mkdir(parents=True, exist_ok=True)
    file.write_json(
        file_task,
        {
            "status": "pending",
        },
    )

    poolExecutor.submit(create_task, dir_input / f"{task_id}.pdf", dir_output / task_id)

    return make_common_data(0, "Success", {"taskID": task_id})


@app.get("/", response_class=RedirectResponse, status_code=302)
async def redirect_index():
    return "index.html"

# TODO ignore file log
app.mount("/static", StaticFiles(directory=dir_output), name="static")
app.mount("/", StaticFiles(directory=dir_fe), name="fe")
