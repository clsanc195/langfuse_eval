#!/usr/bin/env bash
set -euo pipefail

# Setup script for the observability_comparison demo.
#
# This is an extended version of the parent setup.sh:
#  - Brings up self-hosted Langfuse via docker compose (same as before)
#  - Creates a local Python venv at ./.venv inside this folder
#  - Installs the packages needed by all three notebooks (Langfuse, LangSmith, Galileo)
#  - Prints next-step hints for the two SaaS platforms (LangSmith, Galileo)
#
# LangSmith and Galileo are SaaS-only and require an account + API key;
# they cannot be self-hosted from this script. See the README for signup links.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LANGFUSE_DIR="${SCRIPT_DIR}/langfuse"
LANGFUSE_REPO="https://github.com/langfuse/langfuse.git"
VENV_DIR="${SCRIPT_DIR}/.venv"

log()  { printf '\033[1;34m[setup]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m  %s\n' "$*"; }
err()  { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; }

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "missing dependency: $1"
    exit 1
  fi
}

require git
require docker
require python3

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

# ---------- 1. Langfuse (self-hosted) ----------
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
LANGFUSE_READY=0
for _ in $(seq 1 60); do
  if curl -fsS http://localhost:3000/api/public/health >/dev/null 2>&1; then
    log "langfuse is up: http://localhost:3000"
    LANGFUSE_READY=1
    break
  fi
  sleep 2
done

if [[ "${LANGFUSE_READY}" -ne 1 ]]; then
  warn "langfuse did not become healthy within ~2 minutes"
  warn "check logs with: (cd ${LANGFUSE_DIR} && ${COMPOSE[*]} logs -f)"
  warn "continuing with Python setup anyway"
fi

# ---------- 2. Python venv + dependencies ----------
if [[ ! -d "${VENV_DIR}" ]]; then
  log "creating venv at ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

log "upgrading pip"
python -m pip install --quiet --upgrade pip

log "installing python dependencies (this can take a minute)"
pip install --quiet \
  "anthropic>=0.39" \
  "python-dotenv>=1.0" \
  "jupyter>=1.0" \
  "ipykernel>=6.29" \
  "langgraph>=0.2.50" \
  "langchain>=0.3" \
  "langchain-anthropic>=0.3" \
  "langchain-core>=0.3" \
  "langfuse>=2.50" \
  "opentelemetry-instrumentation-anthropic" \
  "langsmith>=0.1.130" \
  "galileo>=1.0"

log "python deps installed into ${VENV_DIR}"

# ---------- 3. .env scaffold ----------
if [[ ! -f "${SCRIPT_DIR}/.env" ]]; then
  if [[ -f "${SCRIPT_DIR}/.env.example" ]]; then
    cp "${SCRIPT_DIR}/.env.example" "${SCRIPT_DIR}/.env"
    log "created ${SCRIPT_DIR}/.env from .env.example — fill in your keys"
  fi
fi

# ---------- 4. Next-step hints ----------
cat <<'EOF'

================================================================================
 Next steps
================================================================================

1. Langfuse (self-hosted, already running):
   - Open http://localhost:3000
   - Sign up locally, create an organization + project
   - Settings -> API Keys -> create a key pair
   - Paste into .env as LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY

2. LangSmith (SaaS, free tier available):
   - Sign up at https://smith.langchain.com
   - Free "Developer" plan: 1 seat, 5k traces/month, no credit card required
   - Settings -> API Keys -> Create API Key (Personal Access Token)
   - Paste into .env as LANGSMITH_API_KEY
   - Set LANGSMITH_PROJECT to whatever you want (e.g. observability-comparison)

3. Galileo (SaaS, free tier available):
   - Sign up at https://app.galileo.ai/sign-up
     - HEADS UP: Galileo gates signup behind a WORK EMAIL — personal
       addresses (gmail/outlook/icloud/...) are rejected at the form.
       Workarounds:
         * Use a company / .edu address
         * Use an email on a custom domain you own
         * Email support@galileo.ai requesting a personal-email exception
       If none of those work, skip Galileo for now; the other two notebooks
       and docs/comparison.md still tell most of the story.
     - Once in, the free tier has no credit card and a starter trace/eval
       quota per month. Pick any workspace name when prompted.
   - Once logged in: top-right user menu -> API Keys -> Create API Key
   - Create or note a Project name and Log Stream name (the UI will offer
     defaults; "observability-comparison" / "default" both work)
   - Paste into .env as:
       GALILEO_API_KEY=...
       GALILEO_PROJECT=observability-comparison
       GALILEO_LOG_STREAM=default
       GALILEO_CONSOLE_URL=https://app.galileo.ai   # leave as default unless on a dedicated cluster

4. Anthropic:
   - https://console.anthropic.com -> API Keys
   - Paste into .env as ANTHROPIC_API_KEY

5. Run the notebooks:
   source .venv/bin/activate
   jupyter notebook notebooks/

================================================================================
EOF
