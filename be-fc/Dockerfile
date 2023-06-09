FROM golang:1.20 AS base
WORKDIR /src
COPY go.* .
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

FROM base AS build
RUN --mount=target=. \
    --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go build -v -o /app/flow-pdf-be-sc -trimpath -ldflags "-s -w" ./cmd/be/main.go

# Import the binary from build stage
FROM gcr.io/distroless/static:nonroot as prd
WORKDIR /home/nonroot
COPY --from=build /app/flow-pdf-be-sc /home/nonroot
# this is the numeric version of user nonroot:nonroot to check runAsNonRoot in kubernetes
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/home/nonroot/flow-pdf-be-sc"]