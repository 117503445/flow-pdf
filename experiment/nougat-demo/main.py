from pathlib import Path

dir_data = Path('data')
dir_input = dir_data / 'input'
dir_output = dir_data / 'output'

# nougat data/input/hotstuff.pdf -o data/output -m 0.1.0-base --markdown


import subprocess

for file in dir_input.glob('*.pdf'):
    command = f'nougat {file} -o {dir_output} -m 0.1.0-base --markdown'
    print(command)
    subprocess.run(command, shell=True)
