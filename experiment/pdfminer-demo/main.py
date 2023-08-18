import pdfminer
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

from pathlib import Path
from htutil import file # type: ignore

dir_data = Path('data')

dir_input = dir_data / 'in'

files = sorted(dir_input.glob('*.pdf'))

for f in files:
    dir_out = dir_data / 'out' / f.stem
    print(f'Processing {dir_out}')
    dir_out.mkdir(parents=True, exist_ok=True)

    file_text = dir_out / 'text' / '1.txt'
    if not file_text.exists():
        output_string = StringIO()
        with open(f, 'rb') as fin:
            extract_text_to_fp(fin, output_string)

        file.write_text(file_text, output_string.getvalue())

    file_html = dir_out / 'html' / '1.html'
    if not file_html.exists():
        output_string = StringIO()
        with open(f, 'rb') as fin:
            extract_text_to_fp(fin, output_string, laparams=LAParams(),
                        output_type='html', codec='utf-8')
            
        file.write_text(file_html, output_string.getvalue())