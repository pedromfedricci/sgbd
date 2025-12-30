set dotenv-load := false

compose := "docker compose"
files := "-f docker-compose.yml -f docker-compose.dev.yml"

dev-up:
    {{compose}} {{files}} up --detach -V

dev-up-db:
    {{compose}} {{files}} up --detach db

dev-up-build:
    {{compose}} {{files}} up --build --force-recreate --detach

dev-down:
    {{compose}} {{files}} down

dev-down-db:
    {{compose}} {{files}} down db

dev-down-prune:
    {{compose}} {{files}} down --volumes

dev-logs-api:
    {{compose}} {{files}} logs --follow api

dev-logs-db:
    {{compose}} {{files}} logs --follow db

dev-api-env:
    {{compose}} {{files}} run --rm api env | sort

dev-api-bash:
    {{compose}} {{files}} run --rm api bash
