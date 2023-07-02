from pathlib import Path
import shutil

dir_input = Path("./paper")
dir_output = Path("./paper_pdf")

if Path(dir_output).exists():
    print("dir_output exists")
    exit()

dir_output.mkdir()

for path in Path(dir_input).glob("**/*.pdf"):
    print(path)

    path_dest = dir_output / path.name
    shutil.copy(path, path_dest)
