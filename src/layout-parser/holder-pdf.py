from pathlib import Path
import fitz
import cv2
import layoutparser as lp
import json
import fitz.utils

dir_data = Path('data')
holder_types =set(['Table', 'Figure'])

def make_holder(f: Path):
    dir_output = dir_data / 'layout-parser-output' / f.stem

    with fitz.open(f) as doc:  # type: ignore
        for i in range(doc.page_count):
            page = doc.load_page(i)
            f_layout = dir_output / "layout" / f"{i}.json"
            f_holder_img = dir_output / "holder" / f"{i}.png"

            with open(f_layout) as f:
                layout = json.load(f)

            for index, box in enumerate(layout['blocks']):
                if box['type'] in holder_types:
                    x0, x1, y0, y1 = int(box['x_1']), int(box['x_2']), int(box['y_1']), int(box['y_2'])

                    x0, x1, y0, y1 = int(x0/2), int(x1/2), int(y0/2), int(y1/2)

                    print(f'page {i}, x0: {x0}, x1: {x1}, y0: {y0}, y1: {y1}')

                    rect = fitz.Rect(x0, y0, x1, y1)
                    page.draw_rect(rect, color=fitz.utils.getColor('white'), fill=fitz.utils.getColor('white'))  # type: ignore

                    # 写入字符串
                    text = f'Here is the placeholder for block {index}.'
                    # for i in range(1000):
                    #     text += f"$$$BLOCKS##{index}##BLOCKS$$$" 
                    text_rect = fitz.Rect(x0, y0, x1, y1)
                    page.add_freetext_annot(text_rect, text, fontsize = 12)

        doc.save('hotstuff-holder.pdf')
    
make_holder(Path('data/input/HotStuff.pdf'))