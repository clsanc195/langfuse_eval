# LangSmith Online Evaluator — UI Setup Walkthrough

**Goal**: configure an evaluator that auto-runs on each new trace landing in your LangSmith project, parallel to the Conciseness evaluator you set up in Langfuse.

**Time**: ~5 minutes.

**Why we need this**: the recording deck has parity slides between Langfuse and LangSmith (both showcase server-side auto-evaluation). Without setting this up in LangSmith, the deck would implicitly suggest LangSmith doesn't have the feature — which is wrong (the matrix rates F10 ⭐ for LangSmith). See `docs/recording_guide.md` → "Scene 9 — Online Evaluators" for what the recording will capture.

## Steps

### 1. Open LangSmith
<https://smith.langchain.com>

### 2. Navigate to your project
- Click the project named in your `LANGSMITH_PROJECT` env var (currently `lansmith_trial` per your `.env`)
- Confirm you're in the right workspace (top-left workspace switcher)

### 3. Find the rules / automations / evaluators tab

Inside the project, look for one of these in the top tab nav (the label varies by UI version — Q2 2026 is most likely **Rules**):
- **Rules** ← most common
- **Automations**
- **Online Evaluators**
- Under a ⚙️ Settings icon → "Automation Rules"

### 4. Create a new rule

Click **+ Add Rule** (or **+ New Automation Rule** / **+ Create Online Evaluator** — naming varies).

### 5. Configure the rule

| Field | Value |
| --- | --- |
| **Name** | `conciseness-check` (mirrors the Langfuse evaluator name for clean side-by-side) |
| **Filter — Run type** | `chain` |
| **Filter — Is root** | `true` (only score the parent trace, not every sub-span) |
| **Filter — Tag (optional)** | `observability_comparison` (limits to demo traces) |
| **Sampling rate** | `1.0` (100% — all matching traces) |
| **Action** | "Run an LLM-as-judge evaluator" / "Apply evaluator" |

### 6. Pick the evaluator template

LangSmith has a dropdown of pre-built evaluators. In order of preference:

1. **Conciseness** (if available as a direct template)
2. **Criteria** → in the criterion field type `conciseness`
3. **Custom** → write a prompt template:

   ```
   Rate the conciseness of this assistant response from 0.0 to 1.0.
   1.0 = response is appropriately brief and to the point
   0.5 = somewhat verbose but acceptable
   0.0 = unnecessarily long or padded

   Question: {input}
   Response: {output}

   Return JSON: {"score": <number>, "reasoning": "<one sentence>"}
   ```

### 7. Pick the judge model

Anthropic Claude (or GPT-4 if you have OpenAI configured).

If LangSmith complains it doesn't have an API key for your chosen provider:
- Go to **Settings → Secrets** (or **Settings → Workspace → Secrets**)
- Add `ANTHROPIC_API_KEY` with the value from your `.env`
- Come back to the rule config

### 8. Save / Enable the rule

Click **Save** or **Enable** depending on the UI version.

### 9. (Optional) Back-fill existing traces

If the UI offers an "Apply to past runs" / "Back-fill" button, click it — otherwise the evaluator only scores **new** traces going forward.

### 10. Trigger fresh data

Re-run one of the notebooks to land new traces the evaluator will pick up:

```bash
cd observability_comparison
source .venv/bin/activate
jupyter nbconvert --to notebook --execute notebooks/02_langsmith.ipynb \
  --output /tmp/test.ipynb --ExecutePreprocessor.timeout=180
```

Or any of:
- `notebooks/langsmith/error_path.ipynb`
- `notebooks/langsmith/multi_turn.ipynb`

## Verification

After ~1–2 minutes:

1. Open any new trace in the Runs list
2. Right panel → **Feedback** section should show `conciseness` with a score 0.0–1.0
3. **Optional**: search the project for runs with `run_name` like `LLM-Judge-Evaluator` or `Execute evaluator` — those are the evaluator's own runs

## Troubleshooting

| Problem | Likely fix |
| --- | --- |
| Can't find Rules tab | Look under ⚙️ Settings → Automation Rules. Some accounts have it gated to Plus tier — check pricing-page features. |
| Evaluator created but no scores appear | Wait 2-3 min, then re-run a notebook. Online evaluators only score *new* traces by default. Use back-fill if available. |
| Anthropic model not in dropdown | Settings → Secrets → add `ANTHROPIC_API_KEY` from `.env`. May need to refresh page. |
| Score appears but always 0 or empty | The custom prompt may not be returning valid JSON. Use the pre-built `criteria` evaluator with `conciseness` as the criterion instead. |
| Hit a tier-gated limit | LangSmith Developer tier is sometimes limited on Online Evaluators count. The matrix rated this ⭐ but real-world tier gating may apply. |

## After it's working — ping me

Once you have at least one trace scored by the `conciseness-check` evaluator, say "done" and we'll:
1. Confirm `recording_guide.md` Scene 9 for LangSmith is ready (it already is — see the doc)
2. Move on to recording captures

If you hit a snag — different UI labels, missing dropdown options, gated feature, or you just want to skip — drop a screenshot or describe what you see and I'll adjust.
