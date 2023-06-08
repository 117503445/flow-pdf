from pathlib import Path
import shutil

dir_target = Path('./data') / 'target'
dir_target.mkdir(parents=True, exist_ok=True)

dir_output =  Path('./data') / 'out'
for f in dir_output.glob('*'):
    file_id = f / 'big_blocks_id.json'
    dir_dest = dir_target / f.name / 'big_blocks_id'
    dir_dest.mkdir(parents=True, exist_ok=True)

    if file_id.exists():
        shutil.copy(file_id, dir_dest)