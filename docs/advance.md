## usage

[optional] pull docker image (use ali mirror to speed up chinese users)

```sh
docker pull registry.cn-hangzhou.aliyuncs.com/117503445-mirror/flow-pdf && docker tag registry.cn-hangzhou.aliyuncs.com/117503445-mirror/flow-pdf 117503445/flow-pdf
```

create `docker-compose.yml` in empty folder

```yaml
# docker-compose.yml
services:
  flow-pdf:
    image: '117503445/flow-pdf'
    container_name: flow-pdf
    restart: unless-stopped
    volumes:
        - './web-data:/root/app/flow_pdf/web-data'
    working_dir: /root/app/flow_pdf/flow_pdf
    ports:
      - '8080:8080'

    # not necessary, but can be used to limit resources
    deploy:
      resources:
        limits:
          cpus: '16'
          memory: '8G'
```

run

```sh
docker-compose up -d
```

visit `http://localhost:8080`

## dev

core

```sh
poetry install
poetry run python flow_pdf/main.py
```

fe

```sh
cd fe
# pnpm install
pnpm run dev
# pnpm run build
```

be

```sh
cd flow_pdf
poetry run uvicorn be:app --reload --host 0.0.0.0
```

Docker

```sh
docker build -t 117503445/flow-pdf .
docker run --name flow-pdf -d -p 8080:8080 117503445/flow-pdf
```
