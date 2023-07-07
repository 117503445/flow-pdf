# 进阶使用

## Docker 自部署

通过自己部署 Docker 镜像，可以解除文件大小、保存时间的限制。

[可选] 从国内镜像站下载镜像

```sh
docker pull registry.cn-hangzhou.aliyuncs.com/117503445-mirror/flow-pdf && docker tag registry.cn-hangzhou.aliyuncs.com/117503445-mirror/flow-pdf 117503445/flow-pdf
```

下载 `docker-compose.yml`

```yaml
version: '3.9'
services:
  flow-pdf:
    image: '117503445/flow-pdf'
    container_name: flow-pdf
    restart: unless-stopped
    volumes:
        - './web-data:/root/app/flow_pdf/web-data'
    ports:
      - '8080:8080'
    deploy:
      resources:
        limits:
          cpus: '16'
          memory: '8G'
```

运行

```sh
docker-compose up -d
```

访问 `http://localhost:8080` 即可使用

## 本地开发

### 核心解析逻辑

核心代码位于 `flow_pdf/worker` 目录下，本地开发时使用 `flow_pdf/main.py` 进行调用。

安装依赖

```sh
poetry install
```

将 PDF 文件放在 `data` 目录下，比如 `data/bitcoin.pdf`

将 `config.yaml.example` 粘贴为 `config.yaml`，并修改为

```yaml
path:
  input: ./data/in
  output: /tmp/flow-pdf/out # 使用 tmp 文件夹，避免硬盘读写，增加性能

files:
  - bitcoin # 不需要 .pdf 后缀
```

运行

```sh
poetry run python flow_pdf/main.py
```

也可以挂载 tmp 文件夹

```sh
mkdir -p /tmp/flow-pdf/out
ln -s /tmp/flow-pdf/out ./data/out
```

然后更新配置文件

```yaml
path:
  input: ./data/in
  output: ./data/out # <--- updated

files:
  - bitcoin
```

### Web 端

后端采用 FastAPI 调用核心解析逻辑，前端使用 React。

启动后端

```sh
cd flow_pdf
poetry run uvicorn be:app --reload --host 0.0.0.0
```

安装前端依赖

```sh
cd fe
pnpm install
```

启动前端

```sh
pnpm run dev
```

### 镜像构建推送

```sh
docker build -t 117503445/flow-pdf .
docker tag 117503445/flow-pdf registry.cn-hangzhou.aliyuncs.com/117503445-mirror/flow-pdf
docker push registry.cn-hangzhou.aliyuncs.com/117503445-mirror/flow-pdf
```
