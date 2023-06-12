from pathlib import Path
import shutil
from htutil import file
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

dir_target = Path("./data") / "target"
dir_target.mkdir(parents=True, exist_ok=True)

dir_output = Path("./data") / "out"

changed_list = []

for f in sorted(dir_output.glob("*")):
    file_id = f / "big_blocks_id.json"
    dir_dest = dir_target / f.name / "big_blocks_id"
    if file_id.exists():
        if not dir_dest.exists():
            dir_dest.mkdir(parents=True)
            file.write_text(dir_dest / "note.txt", f"created time: {current_time}\n\n")
            shutil.copy(file_id, dir_dest)
        else:
            cur = file.read_json(file_id)
            expect = file.read_json(dir_dest / "big_blocks_id.json")

            if cur != expect:
                changed_list.append(f)

if changed_list:
    print('please input the index of the accepted files, like "1 3", or "a" to select all')
    for i, f in enumerate(changed_list):
        print(f'{i}: {f.stem}')

    user_input = input()

    if user_input == 'a':
        accepted_list = list(range(len(changed_list)))
    else:
        accepted_list = [int(i) for i in input().split(' ')]

    for i in accepted_list:
        f = changed_list[i]
        file_id = f / "big_blocks_id.json"
        dir_dest = dir_target / f.name / "big_blocks_id"
        shutil.copy(file_id, dir_dest)
        file.append_text(dir_dest / "note.txt", f"accepted time: {current_time}\n")