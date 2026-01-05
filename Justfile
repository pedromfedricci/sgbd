set dotenv-load := false

compose := "docker compose"
files := "-f docker-compose.yml -f docker-compose.dev.yml"

check:
  uv run ruff check .

format:
  uv run ruff format .

test:
  uv run pytest

ps:
    {{compose}} {{files}} ps

dev-up:
    {{compose}} {{files}} up --detach -V

dev-up-local:
    {{compose}} {{files}} up --detach db
    sleep 5
    ./scripts/start.sh

dev-up-db:
    {{compose}} {{files}} up --detach db

dev-up-build:
    {{compose}} {{files}} up --build --force-recreate --detach

dev-down:
    {{compose}} {{files}} down

dev-db-down:
    {{compose}} {{files}} down db

dev-down-prune:
    {{compose}} {{files}} down --volumes --remove-orphans

dev-db-prune:
    {{compose}} {{files}} down --volumes --remove-orphans db

dev-api-logs:
    {{compose}} {{files}} logs --follow api

dev-db-logs:
    {{compose}} {{files}} logs --follow db

dev-api-env:
    {{compose}} {{files}} run --rm api env | sort

dev-api-bash:
    {{compose}} {{files}} run --rm api bash

dev-db-psql:
    {{compose}} {{files}} exec db psql -U sgbd -d sgbd

# Run E2E tests with fresh containers
test-e2e:
    #!/usr/bin/env bash
    set -euo pipefail

    cleanup() {
        echo "Cleaning up..."
        {{compose}} {{files}} down --volumes --remove-orphans
    }
    trap cleanup EXIT

    echo "Starting services..."
    {{compose}} {{files}} up --build --force-recreate --detach

    echo "Waiting for API to be healthy..."
    timeout 60 bash -c 'until curl -sf http://localhost:8000/docs > /dev/null; do sleep 1; done'

    echo "Running hurl tests..."
    hurl --test tests/*.hurl
