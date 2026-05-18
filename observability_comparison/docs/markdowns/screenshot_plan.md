# Screenshot Capture Plan

Multi-step plan for gathering the screenshots needed for the **Langfuse vs LangSmith vs Galileo** comparison deck.

**Audience**: internal engineering + PM / leadership
**Target length**: ~45 min talk
**Status**: in progress — see checklist at the bottom

## Working method

We are capturing screenshots **one at a time**. For each:
1. Claude (the assistant) asks for a specific screenshot with detailed navigation instructions
2. You take the screenshot and share it
3. Claude analyzes it: is it on-frame, on-message, comparable to its counterparts? Does it tell the slide's story?
4. **Go**: move to the next. **Re-shoot**: take it again with adjusted framing/state.
5. Repeat until the 22-shot list is complete
6. Decide which advanced scenarios (errors, multi-turn, datasets) to add before round 2

## Capture standards

- **Browser**: 1440×900 or 1920×1080, light mode, zoom 100%
- **Same trace** across all three platforms wherever possible (we'll use `two_tools` as the hero trace — most representative complexity)
- **URL bar visible** in shots (proves it's the real UI)
- **Naming**: `NN-section-platform.png` (e.g. `04-trace-detail-langfuse.png`) so files sort naturally
- **Crop ratio consistent** across each triple (the 3-up slide layout depends on this)

## Narrative arc the deck should follow

1. **The same agent, the same trace, three UIs** → visual proof platforms are interchangeable as basic tracers
2. **Zoom into a trace** → per-platform anatomy of the same data
3. **Metadata + tagging** → showing structured search works in all three
4. **The differentiated bets** → Galileo auto-evals, LangSmith Playground, Langfuse self-host
5. **Pricing / scale** → the cost story
6. **Bottom-line guidance** → "pick X if Y"

## Starting URLs (per platform)

| Platform | URL | Project (from `.env`) |
| --- | --- | --- |
| 🔵 Langfuse | `LANGFUSE_HOST` (default `http://localhost:3000`) | whatever you named the project in the UI |
| 🟢 LangSmith | <https://smith.langchain.com> | `$LANGSMITH_PROJECT` (default `observability-comparison`) |
| 🟠 Galileo | <https://app.galileo.ai> | `$GALILEO_PROJECT` (default `observability-comparison`) → log stream `$GALILEO_LOG_STREAM` (default `default`) |

Filter by tag `validation` in each to find the 3 demo traces.

## The 22-shot checklist

### Block A — Same data, three UIs (6 shots)
- [ ] **#1 — 🔵 Langfuse trace list** filtered by tag `validation` (3 rows visible)
- [ ] **#2 — 🟢 LangSmith runs list** filtered by tag `validation` (3 rows visible)
- [ ] **#3 — 🟠 Galileo trace list** in log stream `default` (3 traces visible)
- [ ] **#4 — 🔵 Langfuse `two_tools` trace detail** (full screen: tree + IO panel)
- [ ] **#5 — 🟢 LangSmith `two_tools` run detail** (full screen: tree + IO panel)
- [ ] **#6 — 🟠 Galileo `two_tools` trace detail** (Insights/Metrics panel in frame)

### Block B — Trace anatomy close-ups (6 shots)
Target: the first LLM call + the `get_ads_id` tool call inside the `two_tools` trace.
- [ ] **#7 — 🔵 Langfuse LLM span detail** (prompt + completion + tokens)
- [ ] **#8 — 🟢 LangSmith LLM run detail** (prompt + completion + tokens)
- [ ] **#9 — 🟠 Galileo LLM span detail** (prompt + completion + tokens)
- [ ] **#10 — 🔵 Langfuse tool span** (input + output JSON)
- [ ] **#11 — 🟢 LangSmith tool run** (input + output JSON)
- [ ] **#12 — 🟠 Galileo tool span** (input + output JSON)

### Block C — Metadata + tags (3 shots)
- [ ] **#13 — 🔵 Langfuse** metadata/tags panel on a trace
- [ ] **#14 — 🟢 LangSmith** metadata/tags panel on a run
- [ ] **#15 — 🟠 Galileo** metadata/tags panel on a trace

### Block D — Differentiator screenshots (5 shots)
- [ ] **#16 — 🟠 Galileo Insights panel close-up** — Tool Selection Quality, Action Completion, Context Adherence scores (deck hero shot)
- [ ] **#17 — 🟠 Galileo** trace where a metric flagged an issue OR an all-pass trace if none flagged
- [ ] **#18 — 🟢 LangSmith Playground** — replay an LLM span with editable prompt
- [ ] **#19 — 🟢 LangSmith Monitoring/Dashboard** — token usage, latency, run count over time
- [ ] **#20 — 🔵 Langfuse self-host evidence** — settings/API Keys page + `docker compose ps` in a terminal beside it

### Block E — Pricing pages (2 shots)
- [ ] **#21 — Pricing pages** of all three (separate captures OK; one slide later)
- [ ] **#22 — Free tier limits highlighted** — LangSmith Developer (5k/mo), Galileo free, Langfuse self-host $0

## Slide layout for the 3-up shots

For shots 4-6 / 7-9 / 10-12 / 13-15 — use a 3-column slide layout:

```
┌────────────────────────────────────────────────┐
│           Section title (e.g. "LLM span")      │
├──────────────┬──────────────┬──────────────────┤
│  Langfuse    │  LangSmith   │  Galileo         │
│  [shot]      │  [shot]      │  [shot]          │
├──────────────┴──────────────┴──────────────────┤
│ Caption: one-sentence "same data, X different" │
└────────────────────────────────────────────────┘
```

## After capture — decision points

When all 22 are in:
1. Which **2-3 advanced scenarios** strengthen the deck (errors? multi-turn? volume? datasets?). Add them to `shared/scenarios_advanced.py`, re-run, capture round 2.
2. Note any UI that **disappointed** in a platform — fairness data point for the talk.
3. Note any UI that **surprised** — possible second/cleaner shot.
