from pathlib import Path
import fitz
import cv2
import layoutparser as lp

dir_data = Path('data')

dir_input = dir_data / 'in/'

model = lp.Detectron2LayoutModel(
            config_path ='lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config', # In model catalog
            label_map   ={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"}, # In model`label_map`
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8] # Optional
        )

for f in sorted(dir_input.glob('*.pdf')):
    print(f)
    dir_output = dir_data / 'out' / f.stem
    dir_output.mkdir(parents=True, exist_ok=True)

    (dir_output / 'raw').mkdir(parents=True, exist_ok=True)
    (dir_output / 'marked').mkdir(parents=True, exist_ok=True)

    with fitz.open(f) as doc:  # type: ignore
        for i in range(doc.page_count):
            f_raw_img = dir_output / "raw" / f"{i}.png"
            if not f_raw_img.exists():
                page = doc.load_page(i)
                page.get_pixmap(dpi=144).save(f_raw_img) # type: ignore
            
            f_marked_img= dir_output / "marked" / f"{i}.png"

            if not f_marked_img.exists():
                image = cv2.imread(str(f_raw_img.absolute()))
                layout = model.detect(image)
                im = lp.draw_box(image, layout)
                im.save(f_marked_img)