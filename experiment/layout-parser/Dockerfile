FROM pytorch/pytorch:1.8.1-cuda11.1-cudnn8-runtime

RUN apt-get update && apt-get install gcc git ffmpeg libsm6 libxext6 -y
RUN pip uninstall numpy pillow -y
RUN pip install Pillow==9.1
RUN python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.8/index.html
RUN pip install layoutparser pymupdf
COPY download.py /scripts/download.py
RUN python /scripts/download.py