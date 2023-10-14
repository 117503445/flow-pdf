FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

RUN pip install nougat-ocr[api] htutil

WORKDIR /workspace/nougat-demo

COPY . .

ENTRYPOINT [ "python", "fc.py" ]