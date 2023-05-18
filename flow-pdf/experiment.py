import fitz
from fitz import Document, Page
from pathlib import Path
import json
from htutil import file
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import metrics
import fitz.utils
from sklearn.preprocessing import StandardScaler

# official example
def get_image(dir_input: Path, dir_output: Path, doc: Document):
    for page_index in range(len(doc)): # iterate over pdf pages
        page = doc[page_index] # get the page
        image_list = page.get_images()

        # print the number of images found on the page
        if image_list:
            print(f"Found {len(image_list)} images on page {page_index}")
        else:
            print("No images found on page", page_index)

        for image_index, img in enumerate(image_list, start=1): # enumerate the image list
            xref = img[0] # get the XREF of the image
            pix = fitz.Pixmap(doc, xref) # create a Pixmap

            if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                pix = fitz.Pixmap(fitz.csRGB, pix)

            pix.save(dir_output / ("page_%s-image_%s.png" % (page_index, image_index))) # save the image as png
            pix = None

# by chatgpt
def get_image_2(dir_input: Path, dir_output: Path, doc: Document):
    for i in range(doc.page_count):
        # 获取第一页
        page: Page = doc[i]

        # 遍历页面上的所有图像
        for img in page.get_images():
            print('find image', img)
            # 如果图像是矢量图像，则进行裁剪
            if img[0] == 1:

                # 裁剪图像
                xref = img[1]
                pix = fitz.Pixmap(doc, xref)
                output_path = f'image_{xref}.png'
                pix.write_png(output_path) # type: ignore

def get_toc(dir_input: Path, dir_output: Path, doc: Document):
    print('toc =',doc.get_toc()) # type: ignore

def get_text(dir_input: Path, dir_output: Path, doc: Document, opt = 'text'):
    for i in range(doc.page_count):
        page: Page = doc.load_page(i)
        if opt in ['text']:
            print(page.get_text()) # type: ignore
        elif opt in ['blocks']:
            print(json.dumps(page.get_text(opt), indent=2)) # type: ignore
        elif opt in ['html', 'json', 'rawjson', 'xhtml', 'xml']:
            extension_mapping = {
                'html': 'html',
                'json': 'json',
                'rawjson': 'json',
                'xhtml': 'xhtml',
                'xml': 'xml'
            }
            extension = extension_mapping[opt]
            file.write_text(dir_output / f'page_{i}.{extension}', page.get_text(opt)) # type: ignore


def get_draws(dir_input: Path, dir_output: Path, doc: Document):
    for i in range(doc.page_count):
        page: Page = doc.load_page(i)
        file.write_text(dir_output / f'page_{i}.json', json.dumps(page.get_drawings(), indent=2, default=lambda x: x.__dict__) ) # type: ignore


def mark_drawings(dir_input: Path, dir_output: Path, doc: Document):
    for i in range(doc.page_count):
        page: Page = doc.load_page(i)
        print(f'page {i}')

        # points = [[],[]]
        points = []

        drawings = page.get_drawings()
        for drawing in drawings:
            rect = drawing["rect"] 
            # if rect[0] == rect[2]:
            #     rect[2] += 1
            # if rect[1] == rect[3]:
            #     rect[3] += 1
            # annot = page.add_rect_annot(rect)
            # annot.update()

            # points[0].append(rect[0])
            # points[0].append(rect[2])
            # points[1].append(rect[1])
            # points[1].append(rect[3])

            (x0,y0,x1,y1) = rect

            # sample 5 points for a rect
            points.append([x0, y0])
            points.append([x1, y0])
            points.append([x0, y1])
            points.append([x1, y1])
            points.append([(rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2])

        # if points[0]:
        if points:
            points = np.array(points)
            # points = StandardScaler().fit_transform(points)
            # print(points)
            db = DBSCAN(
                eps = 40
                # eps=0.3, min_samples=10
                ).fit(points)
            labels = db.labels_
            # print(labels)

            colors = {
                -1: 'red',
                0: 'blue',
                1: 'green',
                2: 'yellow',
                3: 'pink',
                4: 'purple',
                5: 'orange',
                6: 'brown',
                7: 'black',
            }

            n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
            n_noise_ = list(labels).count(-1)

            print(f'points count: {len(points)}')
            print("Estimated number of clusters: %d" % n_clusters_)
            print("Estimated number of noise points: %d" % n_noise_)

            for j, drawing in enumerate(drawings):
                rect = drawing["rect"] 

                if rect[0] == rect[2]:
                    rect[2] += 1
                if rect[1] == rect[3]:
                    rect[3] += 1
                page.draw_rect(rect, color = fitz.utils.getColor(colors[labels[j * 5]]))

            page.get_pixmap(dpi = 150).save(dir_output /  f'draw_{i}.png') # type: ignore
        


def mark_text(dir_input: Path, dir_output: Path, doc: Document ):
    for i in range(doc.page_count):
        page = doc.load_page(i)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            rect = fitz.Rect(block["bbox"])
            
            annot = page.add_rect_annot(rect)
            
            annot.update()
            # annot.update_color(fitz.utils.getColor("red"))
    doc.save(dir_output / dir_input.name)
    # doc.close()


def repaint(dir_input: Path, dir_output: Path, doc: Document):
    for i in range(doc.page_count):
        page = doc.load_page(i)

        paths = page.get_drawings()  # extract existing drawings
        # this is a list of "paths", which can directly be drawn again using Shape
        # -------------------------------------------------------------------------
        #
        # define some output page with the same dimensions
        outpdf = fitz.open() # type: ignore
        outpage = outpdf.new_page(width=page.rect.width, height=page.rect.height)
        shape = outpage.new_shape()  # make a drawing canvas for the output page
        # --------------------------------------
        # loop through the paths and draw them
        # --------------------------------------
        for path in paths:
            # ------------------------------------
            # draw each entry of the 'items' list
            # ------------------------------------
            for item in path["items"]:  # these are the draw commands
                if item[0] == "l":  # line
                    shape.draw_line(item[1], item[2])
                elif item[0] == "re":  # rectangle
                    shape.draw_rect(item[1])
                elif item[0] == "qu":  # quad
                    shape.draw_quad(item[1])
                elif item[0] == "c":  # curve
                    shape.draw_bezier(item[1], item[2], item[3], item[4])
                else:
                    raise ValueError("unhandled drawing", item)
            # ------------------------------------------------------
            # all items are drawn, now apply the common properties
            # to finish the path
            # ------------------------------------------------------
            try:
                shape.finish(
                    fill=path["fill"],  # fill color
                    color=path["color"],  # line color
                    dashes=path["dashes"],  # line dashing
                    even_odd=path.get("even_odd", True),  # control color of overlaps
                    closePath=path["closePath"],  # whether to connect last and first point
                    lineJoin=path["lineJoin"],  # how line joins should look like
                    lineCap=max(path["lineCap"]),  # how line ends should look like
                    width=path["width"],  # line width
                    stroke_opacity=path.get("stroke_opacity", 1),  # same value for both
                    fill_opacity=path.get("fill_opacity", 1),  # opacity parameters
                    )
                print('success')
            except Exception as ex:
                print('ex', ex)
        # all paths processed - commit the shape to its page
        shape.commit()
        outpdf.save(dir_output / f'page_{i}.pdf')


def render_image(dir_input: Path, dir_output: Path, doc: Document):
    for i in range(doc.page_count):
        page = doc.load_page(i)

        # 150 dpi, A little blurry
        # 200 dpi, clear but slow
        page.get_pixmap(dpi = 150).save(dir_output /  f'raw_{i}.png')