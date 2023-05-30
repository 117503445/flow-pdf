import yaml
from pathlib import Path
import experiment
import fitz
from fitz import Document, Page
import shutil
import processor
import time

def get_files_from_cfg():
   cfg = yaml.load(Path('./config.yaml').read_text(), Loader=yaml.FullLoader)
   for file in cfg['files']:
      yield (Path(file['input']),Path(file['output']))

def get_files_from_dir():
   for file in Path('./data').glob('*.pdf'):
         yield (file, Path('./data') / file.stem)

# processors = [processor.RenderImageProcessor, processor.BigBlockProcessor, processor.FirstLineCombineProcessor]
# processors = [processor.RenderImageProcessor, processor.DrawingExtraProcessor]
# processors = [processor.RenderImageProcessor, processor.FontCounterProcessor, processor.MarkNonCommonFontProcessor]
# processors = [ processor.MarkStructProcessor]
# processors = [processor.WidthCounterProcessor, processor.BigBlockProcessor, processor.RenderImageProcessor]
# processors = [processor.TOCProcessor]
# processors = [ processor.LayoutParserProcessor]
processors = [processor.ImageProcessor, processor.DrawingExtraProcessor, processor.WidthCounterProcessor, processor.BigBlockProcessor, processor.ShotProcessor,processor.JSONProcessor, processor.RenderImageProcessor]

for file_input, dir_output in get_files_from_cfg():
# for file_input, dir_output in get_files_from_dir():
   print('Processing file_input:', file_input, 'dir_output:', dir_output)

   if dir_output.exists():
      shutil.rmtree(dir_output)
   dir_output.mkdir()

   params = {}
   for p in processors:
      print(f'{p.__name__} start')
      start = time.perf_counter()
      p(file_input, dir_output, params).process()
      print(f'{p.__name__} finished, time = {(time.perf_counter() - start):.2f}s')

   # doc: Document = fitz.open(file_input) # type: ignore

   # experiment.render_image(file_input, dir_output)
   # experiment.get_draws(file_input, dir_output, doc)
   # experiment.mark_drawings(file_input, dir_output, doc)

   # experiment.get_text(file_input, dir_output, doc, 'json')
   # experiment.parse(file_input, dir_output, doc)

   # experiment.mark_text(file_input, dir_output, doc)
   # experiment.repaint(file_input, dir_output, doc)

   # experiment.get_image_2(file_input, dir_output, doc)
   # experiment.get_image(file_input, dir_output)
   # experiment.get_toc(file_input, dir_output)
   # experiment.get_text(file_input, dir_output, doc, 'rawjson')
   # experiment.get_text(file_input, dir_output, doc, 'xhtml')
   # experiment.get_text(file_input, dir_output, doc, 'xml')
    



   print('Done', file_input)
   print()