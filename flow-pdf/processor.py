from collections import Counter
import time
import fitz
from fitz import Document, Page, TextPage
from pathlib import Path
import json
from htutil import file
import numpy as np
import requests
from sklearn.cluster import DBSCAN
import fitz.utils
from sklearn.preprocessing import StandardScaler
import concurrent.futures
from functools import cache
from typing import Any


END_CHARACTERS = '.!?'

COLORS = {
    'text': 'blue',
    'inline-image': 'green',
    'block-image': 'red',

    'drawings': 'purple',
    'title': 'yellow',
    'list': 'orange',
    'table': 'pink',
}

class Processor():
    def __init__(self, file_input: Path, dir_output: Path, params: dict[str, Any] = {}):
        self.file_input = file_input
        self.dir_output = dir_output
        self.params = params
    
    @cache
    def get_page_count(self):
        with fitz.open(self.file_input) as doc: # type: ignore
            return doc.page_count
    
    def get_page_output_path(self, page_index: int, suffix: str):
        return self.dir_output / f'page_{page_index}_{suffix}'
        
    def process(self):
        self.process_page_parallel()

    def process_page_parallel(self):
        results = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for page_index in range(self.get_page_count()):
                futures.append(executor.submit(self.process_page, page_index))

            # for future in concurrent.futures.as_completed(futures):
            for future in futures:
                results.append(future.result())
            
        return results


    def process_page(self, page_index: int):
        pass

# 渲染标记，打印 params 信息
class RenderImageProcessor(Processor):
    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            
            page.get_pixmap(dpi = 150).save(self.get_page_output_path(page_index, 'raw.png')) # type: ignore


            def add_annot(page, rects, annot: str, color):
                if not rects:
                    return

                for rect in rects:
                    page.add_freetext_annot((rect[0], rect[1], rect[0]+len(annot) * 5, rect[1]+10), annot, fill_color=fitz.utils.getColor('white'), border_color = fitz.utils.getColor('black'))
                    
                    page.draw_rect(rect, color = fitz.utils.getColor(color)) # type: ignore
                


            if 'big-block' in self.params:
                rects = []
                for block in self.params['big-block'][page_index]:
                    rects.append(block['bbox'])
                add_annot(page, rects, 'big-block', 'blue')

            if 'drawings' in self.params:
                add_annot(page, self.params['drawings'][page_index], 'drawings', 'red')

            if 'images' in self.params:
                rects = []
                for block in self.params['images'][page_index]:
                    rects.append(block['bbox'])
                add_annot(page, rects, 'images', 'red')
                    # page.draw_rect(block['bbox'], color = fitz.utils.getColor(COLORS['text'])) # type: ignore
                    # r = (block['bbox'][0], block['bbox'][1], block['bbox'][0] +20, block['bbox'][1] + 10)
                    # page.add_freetext_annot(r, 'text', fill_color=fitz.utils.getColor('white'), border_color = fitz.utils.getColor('black'))
            

            if 'core-y' in self.params:
                rects = [(self.params['big_text_columns'][0]['min'], self.params['core-y']['min'], self.params['big_text_columns'][-1]['max'], self.params['core-y']['max'])]
                add_annot(page, rects, 'core', 'yellow')

            page.get_pixmap(dpi = 150).save(self.get_page_output_path(page_index, 'marked.png')) # type: ignore


            keys = ['big_text_width_range', 'big_text_columns']
            content = {}
            for k in keys:
                content[k] = self.params[k]

            file.write_json(self.get_page_output_path(page_index, 'meta.json'), content)

# 判断正文块
# out: blocks, core-y

# blocks: page index -> blocks
class BigBlockProcessor(Processor):
    def process(self):
        self.params['big-block'] = {}
        block_list = []
        for i, blocks in enumerate(self.process_page_parallel()):
            block_list.extend(blocks)
            self.params['big-block'][i] = blocks
        self.params['core-y'] = {
            'min': min([b['bbox'][1] for b in block_list]),
            'max': max([b['bbox'][3] for b in block_list])
        }

    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            d = self.params['raw-dict'][page_index]

            blocks = [b for b in d['blocks'] if b['type'] == 0] # type: ignore

            def is_big_block(block):
                if self.params['big_text_width_range']['min']*0.9 <= block['bbox'][2] - block['bbox'][0] <= self.params['big_text_width_range']['max']*1.1:
                    for column in self.params['big_text_columns']:
                        if column['min']*0.9 <= block['bbox'][0] <= column['max']*1.1:
                            return True
                    return False
                else:
                    return False

            blocks = list(filter(is_big_block, blocks))

            # page.get_pixmap(dpi = 150).save(self.get_page_output_path(page_index, 'BigBlock-debug.png')) # type: ignore
            # file.write_json(self.get_page_output_path(page_index, 'blocks.json'), blocks)
            return blocks

# 提取位图
# output: images
class ImageProcessor(Processor):
    def process(self):
        self.params['images'] = {}
        for i, images in enumerate(self.process_page_parallel()):
            self.params['images'][i] = images

    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            d = self.params['raw-dict'][page_index]

            blocks = [b for b in d['blocks'] if b['type'] == 1] # type: ignore
            return blocks


# def debug_mark(page, rects, annot: str, color, dest: str):
#     if not rects:
#         return

#     for rect in rects:
#         page.add_freetext_annot(rect, annot, fill_color=fitz.utils.getColor('white'), border_color = fitz.utils.getColor('black'))
#         page.draw_rect(rect, color = fitz.utils.getColor(color)) # type: ignore
#     page.get_pixmap(dpi = 150).save(dest) # type: ignore


# The first line indent causes the line to become a separate block, which should be merged into the next block.
# in: blocks
# out: blocks
class FirstLineCombineProcessor(Processor):
    def process(self):
        # file.write_json(self.dir_output / 'blocks.json', params['blocks'])
        for page_index, page_blocks in self.params['blocks'].items():
            print('page_index', page_index)
            page_blocks: list[Block]
            i = 0
            while i < len(page_blocks):
                block = page_blocks[i]
                lines = block.lines.split('\n')


                def is_far_to_next_block():
                    if i == len(page_blocks) - 1:
                        return False
                        # return True # or False, doesn't matter
                    
                    next_block = page_blocks[i + 1]

                    LINE_DISTANCE_THRESHOLD = 5

                    if next_block.y0 - block.y1 < LINE_DISTANCE_THRESHOLD:
                        return False
                    else:
                        return True


                conditions = {
                    'lines > 1': lambda: len(list(filter(lambda x: x.strip(), lines))) > 1,
                    'has end': lambda: lines[0][-1] in END_CHARACTERS,
                    'is last block': lambda: i == len(page_blocks) - 1,
                    'far from next block': lambda: is_far_to_next_block()
                }


                labels = ','.join([label for label, condition in conditions.items() if condition()])
                if not labels:
                    labels = '[]'
                print(f'page {page_index} block {i}, labels = {labels}')

                if any([c() for c in conditions.values()]):
                    i += 1
                    continue

                page_blocks[i + 1].lines = lines[0] + page_blocks[i + 1].lines
                # assert page_blocks[i + 1].y0 > block.y0
                # TODO algorithm, code ..
                page_blocks[i + 1].y0 = block.y0

                page_blocks[i + 1].x1 = max(page_blocks[i + 1].x1, block.x1)
                page_blocks.pop(i)
                i += 1
            file.write_json(self.get_page_output_path(page_index, 'blocks_combined.json'), page_blocks)


# drawings 聚类 提取
# out: drawings
class DrawingExtraProcessor(Processor):
    def process(self):
        self.params['drawings'] = {}
        for i, drawings in enumerate(self.process_page_parallel()):
            self.params['drawings'][i] = drawings
    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            
            points:list[list] = []

            drawings = page.get_drawings()
            for drawing in drawings:
                rect = drawing["rect"]

                (x0,y0,x1,y1) = rect

                # sample 5 points for a rect
                points.append([x0, y0])
                points.append([x1, y0])
                points.append([x0, y1])
                points.append([x1, y1])
                points.append([(rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2])

            if points:
                points = np.array(points) # type: ignore

                db = DBSCAN(
                    eps = 40
                    # eps=0.3, min_samples=10
                    ).fit(points) # type: ignore
                labels = db.labels_


                labels = labels[::5]

                # n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
                # n_noise_ = list(labels).count(-1)

                # print(f'points count: {len(points)}')
                # print("Estimated number of clusters: %d" % n_clusters_)
                # print("Estimated number of noise points: %d" % n_noise_)

                images = {} # label -> drawing list
                for j, label in enumerate(labels):
                    if label not in images:
                        images[label] = []
                    images[label].append(drawings[j])
                
                # print(images)


                # counter = 0
                rects =[]
                for j, drawings in images.items():
                    MIN_DRAWINGS = 10
                    if len(drawings) < MIN_DRAWINGS:
                        continue
                    
                    x0 = page.rect.width
                    y0 = page.rect.height
                    x1 = 0
                    y1 = 0
                    for drawing in drawings:
                        rect = drawing["rect"] 
                        x0 = min(x0, rect[0])
                        y0 = min(y0, rect[1])
                        x1 = max(x1, rect[2])
                        y1 = max(y1, rect[3])
                    # print('draw rect',x0, y0, x1, y1)
                    rect = fitz.Rect(x0, y0, x1, y1)
                    rects.append(rect)
                return rects
            else:
                return []

                # debug_mark(page, rects, 'drawing', 'red', self.get_page_output_path(page_index, 'drawing.png')) # type: ignore
                    
                    # page.get_pixmap(dpi = 150, clip = rect).save(self.dir_output /  f'page_{page_index}_image_{counter}.png') # type: ignore
                    # counter += 1

class FontCounterProcessor(Processor):
    def process(self):
        self.params['fonts'] = {}
        for i, font_counter in enumerate(self.process_page_parallel()):
            # combine fonts
            for font, count in font_counter.items():
                if font not in self.params['fonts']:
                    self.params['fonts'][font] = 0

                self.params['fonts'][font] += count
        
        self.params['common_font'] = sorted(self.params['fonts'].items(), key=lambda x: x[1], reverse=True)[0][0]
        
        file.write_json(self.dir_output / 'fonts.json', self.params['fonts'])
        file.write_json(self.dir_output / 'common_font.json', self.params['common_font'])

    def process_page(self, page_index: int):
        f_font_count = {}
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            # file.write_text(self.get_page_output_path(page_index, 'rawdict.json'), page.get_text('rawjson')) # type: ignore
            d = page.get_text('rawdict') # type: ignore

            for block in d['blocks']:
                if block['type'] != 0:
                    # ignore non-text blocks
                    continue
                # if 'lines' not in block:
                #     print(f'page {page_index} block {block["bbox"]} has no lines')
                #     continue
                for line in block['lines']:
                    for span in line['spans']:
                        font = span['font']
                        if font not in f_font_count:
                            f_font_count[font] = 0
                        f_font_count[font] += len(span['chars'])
        return f_font_count
        # file.write_json(self.get_page_output_path(page_index, 'f_font_count.json'), f_font_count)

class MarkNonCommonFontProcessor(Processor):
    def process_page(self, page_index: int):
        text = ''
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            d = page.get_text('rawdict') # type: ignore

            for block in d['blocks']:
                if block['type'] != 0:
                    # ignore non-text blocks
                    continue
                for line in block['lines']:
                    for span in line['spans']:
                        font = span['font']
                        if font != self.params['common_font']:
                            a = span["ascender"]
                            d = span["descender"]
                            r = fitz.Rect(span["bbox"])
                            o = fitz.Point(span["origin"])
                            r.y1 = o.y - span["size"] * d / (a - d)
                            r.y0 = r.y1 - span["size"]
                            page.draw_rect(r, color = fitz.utils.getColor('green')) # type: ignore
                        else:
                            text += ''.join([c['c'] for c in span['chars']])

                text += '\n'
                
            page.get_pixmap(dpi = 150).save(self.get_page_output_path(page_index, 'non-common.png')) # type: ignore

        file.write_text(self.get_page_output_path(page_index, 'non-common.txt'), text) # type: ignore


class MarkStructProcessor(Processor):
    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            d = page.get_text('rawdict') # type: ignore

            for block in d['blocks']:
                if block['type'] != 0:
                    # ignore non-text blocks
                    continue
                # page.draw_rect(block['bbox'], color = fitz.utils.getColor('red')) # type: ignore
                for line in block['lines']:
                    # page.draw_rect(line['bbox'], color = fitz.utils.getColor('yellow')) # type: ignore
                    for span in line['spans']:
                        page.draw_rect(span['bbox'], color = fitz.utils.getColor('green')) # type: ignore
                        pass
                
            page.get_pixmap(dpi = 150).save(self.get_page_output_path(page_index, 'struct.png')) # type: ignore

# 统计大段文字的宽度和位置
# out: big_text_width_range, big_text_x0_range
class WidthCounterProcessor(Processor):
    def process(self):
        blocks = []
        for i, results in enumerate(self.process_page_parallel()):
            blocks.extend(results)

        widths = [b.x1 - b.x0 for b in blocks]

        if widths:
            db = DBSCAN(eps = 5
                        # eps=0.3, min_samples=10
                        ).fit(np.array(widths).reshape(-1, 1)) # type: ignore
            labels = db.labels_
            # get most common label
            label_counts = Counter(labels)
            most_common_label = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[0][0]

            big_text_block = [b for i, b in enumerate(blocks) if labels[i] == most_common_label]
            big_text_width = [b.x1 - b.x0 for b in big_text_block]

            BIG_TEXT_THRESHOLD = 0.6
            if len(big_text_width) / len(widths) < BIG_TEXT_THRESHOLD:
                print(f'WARNING: most common label only has {len(big_text_width)} items, less than {BIG_TEXT_THRESHOLD * 100}% of total {len(widths)} items')

            width_range = {
                'min': min(big_text_width),
                'max': max(big_text_width)
            }
            self.params['big_text_width_range'] = width_range


            db = DBSCAN(eps = 30
            # eps=0.3, min_samples=10
            ).fit(np.array([b.x0 for b in big_text_block]).reshape(-1, 1)) # type: ignore
            labels = db.labels_


            columns=[]
            for i in range(len(set(labels))):
                blocks = [b for j, b in enumerate(big_text_block) if labels[j] == i]
                column = {
                    'min': min([b.x0 for b in blocks]),
                    'max': max([b.x1 for b in blocks])
                }
                columns.append(column)
            self.params['big_text_columns'] = columns
        else:
            print('WARNING: no big text found')


    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            blocks = [Block(b) for b in page.get_text('blocks')] # type: ignore

            def is_big_block(block: Block):
                BIG_BLOCK_MIN_WORDS = 50

                words = block.lines.split(' ')
                return len(words) > BIG_BLOCK_MIN_WORDS

            blocks = list(filter(is_big_block, blocks))
            

            # file.write_json(self.get_page_output_path(page_index, 'blocks.json'), blocks)
            # file.write_text(self.get_page_output_path(page_index, 'blocks.json'), json.dumps(blocks, indent=2, default=lambda x: x.__dict__)) # type: ignore

            return blocks

class LayoutParserProcessor(Processor):
    def process(self):
        url = "http://172.17.0.2:8000/api/task"
        resp = requests.post(url, files={"file": open(self.file_input, "rb")}) # type: ignore
        task_id = resp.json()['data']['taskID']

        while True:
            resp = requests.get(url+f'/{task_id}').json()
            print(resp['code'], resp['msg'])
            if resp['code'] == 0:
                break
            time.sleep(5)
        
        layout = resp['data']
        layout = { i:r for i , r in enumerate(layout)}
        self.params['layout'] = layout

        file.write_json(self.dir_output / 'layout.json', layout)

        self.process_page_parallel()

    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)

            page_layout = self.params['layout'][page_index]
            
            # page.get_pixmap(dpi = 150).save(self.get_page_output_path(page_index, 'raw.png')) # type: ignore

            for block in page_layout['_blocks']:

                if block['type'] == 'Title':
                    pass
                    # if block['score'] < 0.9:
                    #     continue
                else:
                    continue
                # elif block['type'] not in ['Figure']:
                #     continue

                b = block['block']
                r = (b['x_1'] / 2, b['y_1'] / 2 , b['x_2'] / 2, b['y_2'] / 2)

                d_t = {
                    'Text': 'text',
                    'Title': 'title',
                    'List': 'list',
                    'Table': 'table',
                    'Figure': 'block-image',
                }

                page.draw_rect(r, color = fitz.utils.getColor(COLORS[d_t[block['type']]])) # type: ignore
        
            page.get_pixmap(dpi = 150).save(self.get_page_output_path(page_index, 'marked.png')) # type: ignore

class TOCProcessor(Processor):
    def process(self):
        with fitz.open(self.file_input) as doc:# type: ignore
            toc = doc.get_toc()
            file.write_json(self.dir_output / 'toc.json', toc)

# out: raw-dict
class RawDictProcessor(Processor):
    def process(self):
        self.params['raw-dict'] = {}
        for i, page_result in enumerate(self.process_page_parallel()):
            self.params['raw-dict'][i] = page_result
        

    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            return page.get_text('rawdict') # type: ignore
            


class Block:
    # blocks example: (x0, y0, x1, y1, "lines in the block", block_no, block_type)
    def __init__(self, block: list) -> None:
        self.x0 = block[0]
        self.y0 = block[1]
        self.x1 = block[2]
        self.y1 = block[3]
        self.lines: str = block[4]
        self.block_no = block[5]
        self.block_type = block[6]
