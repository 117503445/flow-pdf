from typing import List
import layoutparser as lp
import cv2
import pickle as pkl
from pathlib import Path

import json
# import uuid
import hashlib

from fastapi import FastAPI, File, UploadFile

import queue
import threading

import fitz
from fitz import Document, Page
import concurrent.futures

dir_data = Path('data')
dir_input = dir_data / 'input'
dir_output = dir_data / 'output'
path_list = [dir_data, dir_input, dir_output]
for dir in path_list:
    if not dir.exists():
        dir.mkdir()

model = lp.Detectron2LayoutModel(
            config_path ='lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config', # In model catalog
            label_map   ={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"}, # In model`label_map`
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8] # Optional
        )

def render_image_page(file_input: Path, dest: Path, page_index: int):
    doc = fitz.open(file_input)
    page = doc.load_page(page_index)

    img = page.get_pixmap()
    print(img)
    img.save(dest) # type: ignore



# 定义任务处理函数
def process_task(task):
    # 加锁以确保同一时间只有一个线程在处理任务
    # 执行任务处理逻辑
    print(f"开始处理任务 {task}")
    # ...

    file_input = dir_input / f'{task}.pdf'
    dir_task_output = dir_output / task
    if not dir_task_output.exists():
        dir_task_output.mkdir()

    doc: Document = fitz.open(file_input) # type: ignore
    page_count = doc.page_count



    results = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for i in range(page_count):
            futures.append( executor.submit(render_image_page, file_input = file_input,  dest=dir_task_output / f'page_{i}.png', page_index = i) )
        for future in futures:
            results.append(future.result())
    doc.close()

    for p in sorted(dir_task_output.glob('page_*.png')):
        convert(p)

    print(f"完成处理任务 {task}")

task_queue = queue.Queue()

# 定义任务生产者函数
def create_task(task):
    # 将任务加入队列
    task_queue.put(task)

# 定义任务消费者函数
def run_worker():
    while True:
        # 获取下一项任务
        task = task_queue.get()
        # 处理任务
        process_task(task)
        # 标记任务为已完成
        task_queue.task_done()

t = threading.Thread(target=run_worker)
t.daemon = True
t.start()

app = FastAPI()

def make_common_data(code: int, msg: str, data):
    return {"code": code, "msg": msg, "data": data}

@app.get("/")
def hello():
    return make_common_data(0, "Hello", None)

@app.post("/api/parse_pdf")
async def parse_pdf(file: UploadFile):

    content = await file.read()
    # task id is the sha256 hash of file content
    task_id = hashlib.sha256(content).hexdigest()
    with open(dir_input / f'{task_id}.pdf', "wb") as buffer:
        buffer.write(content)

    create_task(task_id)

    return make_common_data(0, "Success", {
        'taskID': task_id
    })
    # dir_task = dir_input / task_id
    # if not dir_task.exists():
    #     dir_task.mkdir()

    # for image in images:
    #     name = image.filename
    #     if name == None:
    #         name = "non" # TODO
    #     # TODO file name
    #     with open(dir_task / name, "wb") as buffer:
    #         buffer.write()



def write_pkl(path, content) -> None:
    with open(path, 'wb') as f:
        pkl.dump(content, f)
def read_pkl(path):
    with open(path, 'rb') as f:
        result = pkl.load(f)
    return result
def write_text(path, content: str) -> None:
    content = str(content)
    with open(path, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(content)
def write_json(path, content, indent=4) -> None:
    write_text(path, json.dumps(content, indent=indent, ensure_ascii=False, default=lambda x: x.__dict__))

def convert(path):
    image = cv2.imread(str(path.absolute()))
    # model = lp.Detectron2LayoutModel(
    #             config_path ='lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config', # In model catalog
    #             label_map   ={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"}, # In model`label_map`
    #             extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8] # Optional
    #         )

    layout = model.detect(image)
    write_json(str(path.absolute()) + '.layout.json', layout)

    im = lp.draw_box(image, layout)
    im.save(str(path.absolute()) + '.marked.png')

def dev_run():
    names = ['bitcoin', 'raft', 'hotstuff']
    short_names = [ 'c++', 'gtm5']
    for name in names:
        print(name)
        for p in sorted(Path(f'data/{name}').glob('page_*.png')):
            print(p.name)
            convert(p)
    for name in short_names:
        print(name)
        for i in range(30):
            p = Path(f'data/{name}/page_{i}.png')
            print(p.name)
            convert(p)