from worker.html_gen import HTMLGenWorker, DocInputParams, PageInputParams
from pathlib import Path

def main():
    htmlGenWorker = HTMLGenWorker()

    htmlGenWorker.run(DocInputParams(Path(), Path('./data/flow_pdf_output/The_C++_Programming_Language_4th_Edition_Bjarne_Stroustrup'), -1), None) # type: ignore




if __name__ == '__main__':
    main()