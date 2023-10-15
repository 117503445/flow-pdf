FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

ARG DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install nodejs npm git -y

RUN pip install nougat-ocr[api] htutil

WORKDIR /workspace/nougat

COPY . .

# download models
RUN nougat bitcoin-page-2.pdf -o out -m 0.1.0-base --markdown

RUN cd /workspace/nougat/mmd-converter && npm i

WORKDIR /workspace/nougat

ENTRYPOINT [ "python", "fc.py" ]