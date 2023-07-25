FROM node:20.2.0 as fe-build
RUN npm install -g pnpm
WORKDIR /root/fe
COPY fe ./
RUN pnpm install && pnpm run build

FROM python:3.11 as be-base
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /root

FROM be-base as be-poetry
RUN pip install poetry==1.4.2
COPY flow_pdf/poetry.lock flow_pdf/pyproject.toml /root/
RUN poetry export -o requirements.txt

FROM be-base as be-build
WORKDIR /root/app
COPY --from=be-poetry /root/requirements.txt /tmp/requirements.txt
RUN python -m venv .venv && \
    .venv/bin/pip install 'wheel==0.40.0' && \
    .venv/bin/pip install -r /tmp/requirements.txt

FROM python:3.11-slim as be-runtime
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /root/app
ENV PATH=/root/app/.venv/bin:$PATH
COPY --from=be-build /root/app/.venv /root/app/.venv
COPY --from=fe-build /root/fe/dist /root/app/fe/dist

COPY flow_pdf flow_pdf

WORKDIR /root/app/flow_pdf
EXPOSE 8080
ENTRYPOINT [ "uvicorn", "be:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]