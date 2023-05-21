import fitz
from fitz import Document, Page
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
    # def process(self, params: dict[str, Any]):
    #     pass

    def process_page(self, page_index: int):
        with fitz.open(self.file_input) as doc: # type: ignore
            page: Page = doc.load_page(page_index)
            page.get_pixmap(dpi = 150).save(self.dir_output / f'page_{page_index}_raw.png') # type: ignore