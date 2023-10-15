FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

ARG DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install nodejs npm git -y

RUN pip install nougat-ocr[api] htutil

WORKDIR /workspace/nougat

COPY bitcoin-page-2.pdf .
# download models
RUN nougat bitcoin-page-2.pdf -o out -m 0.1.0-base --markdown

COPY mmd-converter mmd-converter
RUN cd /workspace/nougat/mmd-converter && npm i

COPY main.py .

ENTRYPOINT [ "python", "main.py" ]