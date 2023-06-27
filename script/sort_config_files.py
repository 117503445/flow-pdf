import yaml
from pathlib import Path


cfg = yaml.load(Path("./config.yaml").read_text(), Loader=yaml.FullLoader)
cfg["files"] = sorted(cfg["files"])
yaml.dump(cfg, Path("./config.yaml.new").open("w"), allow_unicode=True)
