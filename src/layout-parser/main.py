from pathlib import Path
import fitz
import cv2
import layoutparser as lp
import json

dir_data = Path('data')

dir_input = dir_data / 'input'

model = lp.Detectron2LayoutModel(
            config_path ='lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config', # In model catalog
            label_map   ={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}, # In model`label_map`
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.6] # Optional
        )

print('load model success')

CACHE = False

holder_types =set(['Table', 'Figure'])

def parse(f: Path):
    
    print(f)
    dir_output = dir_data / 'layout-parser-output' / f.stem
    dir_output.mkdir(parents=True, exist_ok=True)

    (dir_output / 'raw').mkdir(parents=True, exist_ok=True)
    (dir_output / 'marked').mkdir(parents=True, exist_ok=True)
    (dir_output / 'layout').mkdir(parents=True, exist_ok=True)
    (dir_output / 'holder').mkdir(parents=True, exist_ok=True)

    with fitz.open(f) as doc:  # type: ignore
        for i in range(doc.page_count):
            f_raw_img = dir_output / "raw" / f"{i}.png"
            if not f_raw_img.exists():
                page = doc.load_page(i)
                page.get_pixmap(dpi=144).save(f_raw_img) # type: ignore
            
            f_layout = dir_output / "layout" / f"{i}.json"
            f_marked_img = dir_output / "marked" / f"{i}.png"

            f_holder_img = dir_output / "holder" / f"{i}.png"

            if CACHE and f_layout.exists() or f_marked_img.exists():
                continue
        
            image = cv2.imread(str(f_raw_img.absolute()))
            layout = model.detect(image)

            im = lp.draw_box(image, layout, show_element_id = True, show_element_type = True)
            im.save(f_marked_img)

            layout = layout.to_dict()
                        
            with open(f_layout, 'w') as f:
                f.write(json.dumps(layout, indent=4))

            im = cv2.imread(str(f_raw_img))

            for box in layout['blocks']:
                if box['type'] in holder_types:
                    x0, x1, y0, y1 = int(box['x_1']), int(box['x_2']), int(box['y_1']), int(box['y_2'])

                    width = x1 - x0
                    height = y1 - y0

                    cv2.rectangle(image, (x0, y0), (x1, y1), (255, 255, 255), 2)


                    text = "This is a long string to fit inside the rectangle"
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


parse(Path('data/input/HotStuff.pdf'))

# for f in sorted(dir_input.glob('*.pdf')):
#     parse(f)