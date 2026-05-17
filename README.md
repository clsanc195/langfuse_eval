# Langfuse Showcase

End-to-end demo of [Langfuse](https://langfuse.com) (self-hosted, local) against a small RAG-style pipeline using Anthropic Claude. The notebook walks through four scenarios, each producing a visually distinct view in the Langfuse UI:

1. **Single LLM call** — basic trace primitive
2. **Multi-step pipeline** — trace hierarchy over retrieve-then-generate
3. **Dataset + experiment** — curated test set, re-runnable experiment
4. **LLM-as-judge evaluator** — faithfulness scoring per trace, aggregated per run

## Prerequisites

- Docker Desktop (running)
- Python 3.11+
- An Anthropic API key  

## Setup

### 1. Start Langfuse locally 

```bash
./setup.sh
```

Clones the official `langfuse/langfuse` repo into `./langfuse` and brings up the stack via `docker compose`. When it reports ready, open <http://localhost:3000>.

Sign up (local account — no email gating on self-host), create an organization and a project, then go to **Settings → API Keys** and create a key pair.

### 2. Configure credentials

```bash
cp .env.example .env
# edit .env with your real keys
```

`.env` is git-ignored.

### 3. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install langfuse anthropic opentelemetry-instrumentation-anthropic python-dotenv jupyter
```

### 4. Run the notebook

```bash
jupyter notebook langfuse_showcase.ipynb
```

## Files

| File | Purpose |
| --- | --- |
| `setup.sh` | Clones Langfuse and starts the docker compose stack |
| `langfuse_showcase.ipynb` | The four-scenario walkthrough |
| `.env.example` | Template for required env vars (copy to `.env`) |
| `.gitignore` | Excludes secrets, the cloned Langfuse repo, and local Python state |

## Stopping Langfuse

```bash
(cd langfuse && docker compose down)
```

## What's git-ignored

- `.env` and any `.env.*` variant (except `.env.example`)
- `*.pem`, `*.key`, `secrets/` — generic secret patterns
- `langfuse/` — the cloned upstream repo
- `.venv/`, `__pycache__/`, `.ipynb_checkpoints/` — local Python/Jupyter state
- `.idea/`, `.vscode/`, `.DS_Store` — IDE and OS noise

Before committing, double-check that no real API keys leaked into notebook cells or outputs.
# langfuse_eval
