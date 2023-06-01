import yaml
from pathlib import Path
import fitz
from fitz import Document, Page
import shutil
import time
from htutil import file
from worker import Executer, workers  # type: ignore

version = file.read_text(Path(__file__).parent / "git.txt")

print(f"version: {version}")
fitz.TOOLS.set_small_glyph_heights(True)


def get_files_from_cfg():
    cfg = yaml.load(Path("./config.yaml").read_text(), Loader=yaml.FullLoader)
    for file in cfg["files"]:
        yield (Path(file["input"]), Path(file["output"]))


def get_files_from_dir():
    for file in Path("./data").glob("*.pdf"):
        yield (file, Path("./data") / file.stem)


for file_input, dir_output in get_files_from_cfg():
    print("Processing file_input:", file_input, "dir_output:", dir_output)

    if dir_output.exists():
        shutil.rmtree(dir_output)
    dir_output.mkdir(parents=True)

    e = Executer(file_input, dir_output)
    e.register(workers)
    e.execute()

    print("Done", file_input)
    print()
