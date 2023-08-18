import json
from pathlib import Path

meta_version = '0.0.1'

tags = input('tags: ').split(' ')

dir_input = Path(__file__) .parent / 'input'
for f in dir_input.glob('*.pdf'):
    f_dest = dir_input / f'{f.stem}.json'
    f_dest.write_text(json.dumps({
        'version': meta_version,
        'tags': tags,
    }, ensure_ascii=False, indent=4))