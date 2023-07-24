from pathlib import Path
from htutil import file

meta_version = '0.0.1'

dir_input = Path('data') / 'in'
for f in dir_input.glob('*.pdf'):
    f_dest = dir_input / f'{f.stem}.json'
    file.write_json(f_dest, {
        'version': meta_version,
        'tags': ['cc'],
    })


dir_input = Path('data') / 'in_qht'
for f in dir_input.glob('*.pdf'):
    f_dest = dir_input / f'{f.stem}.json'
    file.write_json(f_dest, {
        'version': meta_version,
        'tags': ['qht'],
    })