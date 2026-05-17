#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LANGFUSE_DIR="${SCRIPT_DIR}/langfuse"
LANGFUSE_REPO="https://github.com/langfuse/langfuse.git"

log() { printf '\033[1;34m[setup]\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; }

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "missing dependency: $1"
    exit 1
  fi
}

require git
require docker

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  err "docker compose plugin not found (need 'docker compose' or 'docker-compose')"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  err "docker daemon is not running. Start Docker Desktop and retry."
  exit 1
fi

if [[ ! -d "${LANGFUSE_DIR}/.git" ]]; then
  log "cloning langfuse into ${LANGFUSE_DIR}"
  git clone --depth 1 "${LANGFUSE_REPO}" "${LANGFUSE_DIR}"
else
  log "updating existing langfuse checkout"
  git -C "${LANGFUSE_DIR}" pull --ff-only
fi

log "starting langfuse stack via docker compose"
( cd "${LANGFUSE_DIR}" && "${COMPOSE[@]}" up -d )

log "waiting for langfuse to become healthy at http://localhost:3000"
for _ in $(seq 1 60); do
  if curl -fsS http://localhost:3000/api/public/health >/dev/null 2>&1; then
    log "langfuse is up: http://localhost:3000"
    exit 0
  fi
  sleep 2
done

err "langfuse did not become healthy within ~2 minutes"
err "check logs with: (cd ${LANGFUSE_DIR} && ${COMPOSE[*]} logs -f)"
exit 1
