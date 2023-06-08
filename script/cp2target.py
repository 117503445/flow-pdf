from pathlib import Path
import shutil
from htutil import file
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

dir_target = Path('./data') / 'target'
dir_target.mkdir(parents=True, exist_ok=True)

dir_output =  Path('./data') / 'out'
for f in dir_output.glob('*'):
    file_id = f / 'big_blocks_id.json'
    dir_dest = dir_target / f.name / 'big_blocks_id'
    if not dir_dest.exists():
        dir_dest.mkdir(parents=True)
        file.write_text(dir_dest / 'note.txt', f'created time: {current_time}\n\n')

    if file_id.exists():
        shutil.copy(file_id, dir_dest)