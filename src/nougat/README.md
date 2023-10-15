# nougat service

put `.pdf` files in `./data/input`, like `./data/input/bitcoin.pdf`

```sh
# for chinese
docker pull registry.cn-hangzhou.aliyuncs.com/117503445-mirror/flow-pdf-nougat && docker image tag registry.cn-hangzhou.aliyuncs.com/117503445-mirror/flow-pdf-nougat 117503445/flow-pdf-nougat

docker run -v ./data:/local-data --gpus=all 117503445/flow-pdf-nougat
```

view `.mmd` and `.html` files in `./data/output`, like `./data/input/bitcoin.mmd` and `./data/input/bitcoin.html`
