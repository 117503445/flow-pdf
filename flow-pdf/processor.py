import fitz
from fitz import Document, Page, TextPage
from pathlib import Path
import json
from htutil import file
import numpy as np
from sklearn.cluster import DBSCAN
import fitz.utils
from sklearn.preprocessing import StandardScaler
import concurrent.futures
from functools import cache
from typing import Any


END_CHARACTERS = '.!?'

class Processor():
    def __init__(self, file_input: Path, dir_output: Path):
        self.file_input = file_input
        self.dir_output = dir_output
    
    @cache
    def get_page_count(self):
        with fitz.open(self.file_input) as doc: # type: ignore
            return doc.page_count
    
    def get_page_output_path(self, page_index: int, suffix: str):
        return self.dir_output / f'page_{page_index}_{suffix}'
        
    def process(self, params: dict[str, Any] = {}):
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


class RenderImageProcessor(Processor):
    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            
            page.get_pixmap(dpi = 150).save(self.get_page_output_path(page_index, 'raw.png')) # type: ignore

# out: blocks

# blocks: page index -> blocks
class BigBlockProcessor(Processor):
    def process(self, params: dict[str, Any] = {}):
        params['blocks'] = {}
        for i, blocks in enumerate(self.process_page_parallel()):
            params['blocks'][i] = blocks

    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            blocks = [Block(b) for b in page.get_text('blocks')] # type: ignore
            # TODO - use block_type to filter out images

            def is_big_block(block: Block):
                BIG_BLOCK_MIN_WORDS = 5
                

                words = block.lines.split(' ')
                return words[-1][-1] in END_CHARACTERS or len(words) > BIG_BLOCK_MIN_WORDS

            blocks = list(filter(is_big_block, blocks))


            file.write_json(self.get_page_output_path(page_index, 'blocks.json'), blocks)
            # file.write_text(self.get_page_output_path(page_index, 'blocks.json'), json.dumps(blocks, indent=2, default=lambda x: x.__dict__)) # type: ignore

            return blocks

# The first line indent causes the line to become a separate block, which should be merged into the next block.
# in: blocks
# out: blocks
class FirstLineCombineProcessor(Processor):
    def process(self, params: dict[str, Any] = {}):
        # file.write_json(self.dir_output / 'blocks.json', params['blocks'])
        for page_index, page_blocks in params['blocks'].items():
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


class DrawingExtraProcessor(Processor):
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


                counter = 0
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
                    
                    page.get_pixmap(dpi = 150, clip = rect).save(self.dir_output /  f'page_{page_index}_image_{counter}.png') # type: ignore
                    counter += 1

class FontCounterProcessor(Processor):
    def process_page(self, page_index: int):
        f_font_count = {}
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            file.write_text(self.get_page_output_path(page_index, 'rawdict.json'), page.get_text('rawjson')) # type: ignore
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
        file.write_json(self.get_page_output_path(page_index, 'f_font_count.json'), f_font_count)
        

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