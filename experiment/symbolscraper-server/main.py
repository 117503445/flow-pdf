import time
import requests
import asyncio
import functools
import argparse
import os
import subprocess
from pathlib import Path

def sync_calls_docker(files):
    r = "http://localhost:7002/process-pdf"

    for f in files:
        print(f.stem)
        file = {"pdf": (f.name, open(f, 'rb'), "application/pdf")}
        resp = requests.post(r, files=file)

        if resp.status_code != 200:
            print(f"Error: {resp.status_code}, {f.stem}")
            continue
        else:
            dir_out = dir_data / 'out' / f.stem
            dir_out.mkdir(parents=True, exist_ok=True)
            with open(dir_out / '1.xml', 'w') as out:
                out.write(resp.text)


dir_data = Path('data')

dir_input = dir_data / 'in'

files = sorted(dir_input.glob('*.pdf'))

sync_calls_docker(files)
