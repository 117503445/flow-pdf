from pathlib import Path
import fitz
import cv2
import layoutparser as lp
import json
dir_data = Path('data')
holder_types =set(['Table', 'Figure'])

def make_holder(f: Path):
    dir_output = dir_data / 'layout-parser-output' / f.stem

    for f_raw_img in (dir_output / 'raw').glob('*.png'):
        f_layout = dir_output / "layout" / f"{f_raw_img.stem}.json"
        f_marked_img = dir_output / "marked" / f"{f_raw_img.stem}.png"
        f_holder_img = dir_output / "holder" / f"{f_raw_img.stem}.png"


        with open(f_layout) as f:
            layout = json.load(f)

        image = cv2.imread(str(f_raw_img))
        for index, box in enumerate(layout['blocks']):
            if box['type'] in holder_types:
                x0, x1, y0, y1 = int(box['x_1']), int(box['x_2']), int(box['y_1']), int(box['y_2'])
                print(f'page {f_raw_img.stem}, x0: {x0}, x1: {x1}, y0: {y0}, y1: {y1}')
                cv2.rectangle(image, (x0, y0), (x1, y1), (255, 255, 255), -1)

                width = x1 - x0
                height = y1 - y0
                cv2.rectangle(image, (x0, y0), (x1, y1), (255, 255, 255), 2)


                text = f"$$$BLOCKS##{index}##BLOCKS$$$"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.0
                text_color = (0, 0, 0)  # 黑色，以BGR格式表示
                text_thickness = 2
                (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, text_thickness)
                print(text_width, text_height)
                text_x = x0 + (width - text_width) // 2
                text_y = y0 + (height + text_height) // 2
                cv2.putText(image, text, (text_x, text_y), font, font_scale, text_color, text_thickness)
        cv2.imwrite(str(f_holder_img), image)

        

make_holder(Path('data/input/HotStuff.pdf'))