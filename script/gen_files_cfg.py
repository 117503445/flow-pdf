from pathlib import Path
import yaml

dir_in = Path("./data/in")
f_list = []
for f in sorted(dir_in.glob("*.pdf")):
    f_list.append(f.name.replace(".pdf", ""))
cfg = {"files": f_list}
yaml.dump(cfg, Path("./config.yaml.new").open("w"), allow_unicode=True)
