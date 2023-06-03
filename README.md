# flow-pdf

flow-pdf converts PDFs into fluid and dynamic HTML documents, transforming the static layout of PDFs into a responsive and user-friendly format.

## dev

```sh
cd fe
pnpm run dev
# pnpm run build

cd flow_pdf
poetry run uvicorn be:app --reload --host 0.0.0.0

docker build -t 117503445/flow-pdf .
docker run --name flow-pdf -d -p 8080:8080 117503445/flow-pdf

docker run --name flow-pdf -p 8080:8080 -it --entrypoint /bin/bash 117503445/flow-pdf
docker rm -f flow-pdf


```
