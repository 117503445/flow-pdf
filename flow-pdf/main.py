import fitz
from fitz import Document, Page
import yaml
from pathlib import Path

cfg = yaml.load(Path('./config.yaml').read_text(), Loader=yaml.FullLoader)

for file in cfg['files']:

    dir_input = Path(file['input'])
    dir_output = Path(file['output'])

    if not dir_output.exists():
        dir_output.mkdir()

    # 打开 PDF 文件
    doc: Document = fitz.open(dir_input) # type: ignore

    for i in range(doc.page_count):

        page = doc.load_page(i)

        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            rect = fitz.Rect(block["bbox"])
            
            annot = page.add_rect_annot(rect)
            
            annot.update()
            # annot.update_color(fitz.utils.getColor("red"))
    doc.save(dir_output / dir_input.name)
    doc.close()