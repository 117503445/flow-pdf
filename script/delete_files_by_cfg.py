from pathlib import Path
import yaml

cfg = yaml.load(Path("./config.yaml").read_text(), Loader=yaml.FullLoader)

dir_in = Path("./data/in")

dir_in_backup = Path("./data/in_backup")
dir_in_backup.mkdir(exist_ok=True)


for f in dir_in.glob("*.pdf"):
    if f.name.replace(".pdf", "") not in cfg["files"]:
        f.rename(dir_in_backup / f.name)
