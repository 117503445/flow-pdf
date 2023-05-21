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

            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
            
        return results


    def process_page(self, page_index: int):
        pass


class RenderImageProcessor(Processor):
    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            
            page.get_pixmap(dpi = 150).save(self.get_page_output_path(page_index, 'raw.png')) # type: ignore

class BigBlockProcessor(Processor):
    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            blocks = [Block(b) for b in page.get_text('blocks')] # type: ignore
            # TODO - use block_type to filter out images

            def is_big_block(block: Block):
                BIG_BLOCK_MIN_WORDS = 5
                END_CHARACTERS = '.!?'

                words = block.lines.split(' ')
                return words[-1][-1] in END_CHARACTERS or len(words) > BIG_BLOCK_MIN_WORDS

            blocks = list(filter(is_big_block, blocks))

            file.write_text(self.get_page_output_path(page_index, 'blocks.json'), json.dumps(blocks, indent=2, default=lambda x: x.__dict__)) # type: ignore


class Block:
    # blocks example: (x0, y0, x1, y1, "lines in the block", block_no, block_type)
    def __init__(self, block: list) -> None:
        self.x0 = block[0]
        self.y0 = block[1]
        self.x1 = block[2]
        self.y1 = block[3]
        self.lines = block[4]
        self.block_no = block[5]
        self.block_type = block[6]