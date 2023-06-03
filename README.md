# flow-pdf

flow-pdf converts PDFs into fluid and dynamic HTML documents, transforming the static layout of PDFs into a responsive and user-friendly format.

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
