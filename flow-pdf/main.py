import yaml
from pathlib import Path
import experiment
import fitz
from fitz import Document, Page
import shutil

def get_files_from_cfg():
   cfg = yaml.load(Path('./config.yaml').read_text(), Loader=yaml.FullLoader)
   for file in cfg['files']:
      yield (Path(file['input']),Path(file['output']))

def get_files_from_dir():
   for file in Path('./data').glob('*.pdf'):
         yield (file, Path('./data') / file.stem)

for file_input, dir_output in get_files_from_cfg():
# for file_input, dir_output in get_files_from_dir():
    print('Processing file_input:', file_input, 'dir_output:', dir_output)

    if dir_output.exists():
       shutil.rmtree(dir_output)
    dir_output.mkdir()

    doc: Document = fitz.open(file_input) # type: ignore

    # experiment.mark_text(file_input, dir_output, doc)
    # experiment.get_text(file_input, dir_output, doc, 'json')
   #  experiment.repaint(file_input, dir_output, doc)
   #  experiment.get_draws(file_input, dir_output, doc)
    # experiment.mark_drawings(file_input, dir_output, doc)
    experiment.render_image(file_input, dir_output, doc)

    # experiment.get_image_2(file_input, dir_output, doc)
    # experiment.get_image(file_input, dir_output)
    # experiment.get_toc(file_input, dir_output)
    # experiment.get_text(file_input, dir_output, doc, 'rawjson')
    # experiment.get_text(file_input, dir_output, doc, 'xhtml')
    # experiment.get_text(file_input, dir_output, doc, 'xml')
    



    print('Done', file_input)
    print()