FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

RUN pip install nougat-ocr[api] htutil

WORKDIR /workspace/nougat-demo

COPY . .

# download models
RUN nougat bitcoin-page-2.pdf -o out -m 0.1.0-base --markdown

ENTRYPOINT [ "python", "fc.py" ]