# Observability Platforms — Side-by-Side Comparison

Three notebooks running **the exact same LangGraph workflow** and tracing it through three different observability platforms:

1. **Langfuse** (self-hosted, OSS)
2. **LangSmith** (SaaS, LangChain's hosted offering)
3. **Galileo** (SaaS, evaluation-first)

The goal is to put the platforms next to each other on identical input so you can compare:
- Instrumentation effort (lines of code, env vars, decorators vs callbacks)
- How each UI renders a multi-step tool-using agent
- Built-in evaluation / dataset features
- Hosting model + cost
- Where each one is the clear win

## The shared scenario

A small **permission-checking agent** with three dependent tools, defined once in `shared/workflow.py` and imported by all three notebooks:

| Tool | Input | Output |
| --- | --- | --- |
| `get_ads_id` | employee name | internal `ads_id` |
| `get_permissions` | `ads_id` | list of permission strings |
| `check_admin_access` | permissions + resource | boolean `has_admin` |

Each tool's output feeds the next, so the **number of tools the model invokes depends on what the user asks for**:

| User question | Tools called |
| --- | --- |
| "What's the ads_id for Jane Doe?" | 1: `get_ads_id` |
| "What permissions does Jane Doe have?" | 2: `get_ads_id` → `get_permissions` |
| "Does Jane Doe have admin on `billing-prod`?" | 3: `get_ads_id` → `get_permissions` → `check_admin_access` |

The agent is a standard LangGraph ReAct loop (LLM → tools → LLM …). Each notebook runs all three scenarios so every UI shows the same shape of trace.

## Folder layout

```
observability_comparison/
├── setup.sh              # Brings up Langfuse + installs Python deps
├── .env.example          # Copy to .env, fill in keys
├── shared/
│   └── workflow.py       # The LangGraph agent + tools + fixture prompts
├── notebooks/
│   ├── 01_langfuse.ipynb
│   ├── 02_langsmith.ipynb
│   └── 03_galileo.ipynb
└── docs/
    └── comparison.md     # Side-by-side writeup
```

## Prerequisites

- Docker Desktop (for Langfuse self-host)
- Python 3.11+
- Anthropic API key
- LangSmith account (free)
- Galileo account (free)

## Setup

### 1. Run the setup script

```bash
cd observability_comparison
./setup.sh
```

It will:
- Clone and `docker compose up` Langfuse at <http://localhost:3000>
- Create a `.venv` in this folder
- Install all Python deps (LangGraph, LangChain, all three SDKs)
- Print next-step hints for each platform

### 2. Get your keys

#### Langfuse (self-hosted, free)
- Open <http://localhost:3000> after `setup.sh` finishes
- Sign up (local account; no email gating)
- Create an organization → create a project
- **Settings → API Keys → Create new API keys**
- Copy `pk-lf-…` and `sk-lf-…` into `.env`

#### LangSmith (SaaS, free Developer tier)
- Sign up at <https://smith.langchain.com>
- Free **Developer** plan: 1 seat, 5k traces/month, no credit card
- **Settings → API Keys → Create API Key**
- Copy `lsv2_pt_…` into `.env` as `LANGSMITH_API_KEY`

#### Galileo (SaaS, free tier)
- Sign up at <https://app.galileo.ai/sign-up>
  - **Heads up: Galileo gates signup behind a work email** — personal addresses (gmail/outlook/icloud/etc.) are rejected at the form. Workarounds:
    - Use a company/.edu address if you have one
    - Use an email on a domain you own (e.g. `you@yourdomain.dev`)
    - Or contact `support@galileo.ai` / request a demo via the marketing site to get a personal-email exception — they sometimes grant these for evaluation
    - If none of the above work, skip ahead and run notebooks 01 + 02; `docs/comparison.md` still covers Galileo based on its docs and SDK
  - Free tier (once you're in): no credit card, starter quota of traces + evaluations per month — enough for this demo
  - Verify your email, pick a workspace name when prompted
- Get an API key:
  - Once logged in, click your **avatar (top-right) → API Keys**
  - **Create API Key** — copy it immediately (it's shown once)
- Project + log stream:
  - The Galileo SDK auto-creates them on first use; the defaults in `.env.example` are fine
- Paste into `.env`:
  ```
  GALILEO_API_KEY=...
  GALILEO_PROJECT=observability-comparison
  GALILEO_LOG_STREAM=default
  ```

#### Anthropic
- <https://console.anthropic.com> → API Keys → paste into `.env` as `ANTHROPIC_API_KEY`

### 3. Run the notebooks

```bash
source .venv/bin/activate
jupyter notebook notebooks/
```

Run them in order (1 → 2 → 3); each is self-contained and ~5 minutes to walk through.

### 4. Read the comparison

`docs/comparison.md` summarizes what you'll have seen by the end.

## Stopping Langfuse

```bash
(cd langfuse && docker compose down)
```

## What's git-ignored

- `.env` and any `.env.*` (except `.env.example`)
- `langfuse/` (re-cloned by `setup.sh`)
- `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`

Before committing, double-check that no real API keys leaked into notebook outputs.
