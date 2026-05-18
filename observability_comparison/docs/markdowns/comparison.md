# Langfuse vs LangSmith vs Galileo — Final Comparison Report

A side-by-side evaluation of three LLM observability + evaluation platforms, driven by hands-on usage with the demo in this repo and a comprehensive review of each platform's published feature surface (as of Q2 2026).

## Quick orientation

| | 🔵 **Langfuse** | 🟢 **LangSmith** | 🟠 **Galileo** |
| --- | --- | --- | --- |
| **Hosting** | Self-host (OSS, MIT) OR Cloud | SaaS only (Cloud or Enterprise self-host) | SaaS only (or Enterprise VPC) |
| **Pricing floor** | $0 self-host forever / Hobby cloud free | Developer free, 5k traces/mo | Free tier (work email gated) |
| **Setup for LangGraph** | 1-line CallbackHandler | 3 env vars, zero code | 1-line CallbackHandler |
| **Couples you to LangChain?** | No (OSS + OTEL-first) | Yes (same vendor) | No |
| **Headline differentiator** | OSS + self-host control | LangGraph-native UX | Auto agent-quality metrics |
| **What it does best** | Free, sovereign, framework-agnostic | LangGraph debugging + experiments + Threads | Eval-first, in-flight guardrails |
| **Worst at** | UI polish trails LangSmith | Vendor lock-in to LangChain stack | Work-email signup, SDK churn, smaller ecosystem |

## Master feature matrix

The full feature × platform matrix (120+ capabilities across 19 sub-categories A–S) lives in a dedicated file so this document stays readable:

➡️ **[feature_matrix.md](feature_matrix.md)** — go there for the side-by-side capability comparison.

Quick highlights from the matrix:

- **All three** support the basics: trace tree, LangChain integration, tagging, scoring primitives, datasets, prompt registries, OTEL ingestion.
- **Langfuse** is the only OSS / free self-host option (Hosting section P).
- **LangSmith** wins on Threads UX (C), pairwise experiments (H), Prompt Hub (I), monitoring polish (K), and dataset splits (G).
- **Galileo** wins on auto-metrics with zero config (F), in-request guardrails via Protect (L — uniquely owns this category), Log Streams (M), and synthetic dataset generation (G).

---

## Where each platform uniquely wins

### Langfuse uniquely wins on
1. **OSS + free self-host** — only option for $0 sovereign deployment
2. **Mutable label pointers** for prompt deployment (`production` label moves between versions)
3. **Both raw-string AND chat prompt formats**
4. **OTEL maturity** — longest track record, best-documented framework-agnostic story
5. **SDK-side prompt caching**
6. **Full local dev stack** via docker — work offline, fly the whole thing on a laptop
7. **HIPAA without an Enterprise contract** (self-host = your environment, your controls)

### LangSmith uniquely wins on
1. **Zero-config LangChain integration** — env vars only, the only platform with that
2. **Threads view** for chat-style multi-turn debugging
3. **Pairwise experiment comparison UI** — purpose-built A/B for runs
4. **Public Prompt Hub** — marketplace for prompts, none of the others have one
5. **Dataset splits** (train/test/eval) — only platform with first-class splits
6. **Trace-aware Playground** — click any LLM span, edit, re-run, save
7. **Production monitoring polish** — the most mature dashboards + alerts
8. **Largest heuristic evaluator library** (regex / JSON / exact / embedding distance / structured-output)
9. **Documentation quality**
10. **Git-style prompt versioning** with commit hashes

### Galileo uniquely wins on
1. **Auto-metrics on every trace** — Tool Selection Quality, Action Completion, Context Adherence, Instruction Adherence, Tool Error Rate, Conversation Quality, Hallucination, Toxicity, PII — running with **zero configuration**. (Note: Langfuse + LangSmith *also* run evaluators automatically once configured — the difference is the default. See "On evaluator automation" below.)
2. **Galileo Protect** — real-time, in-request guardrails that block / modify / redact. The other two are post-hoc observability; Galileo Protect sits in the request path. This is an **entire product category** the others don't compete in.
3. **Log Streams** — partition traffic (dev / staging / prod) within a single project. Langfuse's Environments is a newer convergence; LangSmith requires separate projects.
4. **Synthetic dataset generation** via `extend_dataset()` — turnkey SDK feature.
5. **Built-in PII detection** as a metric AND a Protect rule.
6. **ChainPoll hallucination method** — proprietary, research-backed faithfulness scoring.
7. **Metric distribution histograms** — easier to see "% of bad traces" because metrics already exist on every trace.
8. **Continuous learning** — metric rubrics refine based on accumulated feedback.

---

## Decision guidance

| If your priority is… | Pick |
| --- | --- |
| Free self-host, OSS, full data sovereignty | **Langfuse** |
| Lowest-friction LangChain/LangGraph instrumentation | **LangSmith** |
| Most polished LangGraph debugging UX (Threads, Playground) | **LangSmith** |
| Eval-first agent quality monitoring with no setup | **Galileo** |
| Real-time production guardrails in the request path | **Galileo** (no peer) |
| Air-gapped or strict data residency | **Langfuse** self-host (free) or **Galileo** VPC (paid) |
| Heavy chatbot use case | **LangSmith** Threads |
| Least vendor lock-in | **Langfuse** (OSS + OTEL) |
| Public prompt sharing / community library | **LangSmith** Prompt Hub |
| Production dashboards + alerts that look ready for an exec | **LangSmith** |
| Lowest cost at high trace volume | **Langfuse** self-host |
| Dataset/experiment workflow with splits + pairwise compare | **LangSmith** |
| Best out-of-the-box "is my agent actually doing the right thing?" | **Galileo** |
| Multi-framework (OpenAI + Anthropic + LlamaIndex + custom) without lock-in | **Langfuse** (OTEL) |

## On evaluator automation — important nuance

A common over-simplification is "Galileo auto-scores, the other two don't." That's wrong. The real difference is **what runs by default**:

| | Effort to set up | What runs |
| --- | --- | --- |
| 🔵 **Langfuse** | Configure once: pick model, write prompt template, set target filter, set sampling rate | One evaluator at a time, on the traces you scoped — but automatically once configured |
| 🟢 **LangSmith** | Same — configure an **Online Evaluator** | Same |
| 🟠 **Galileo** | **Zero config** | A whole suite of pre-built metrics on every trace |

Once you configure an evaluator in Langfuse or LangSmith, it runs **automatically on every matching incoming trace** without further intervention — server-side, no SDK calls needed. You can verify this in Langfuse by looking at traces named `Execute evaluator: <name>` in the trace list — those are the evaluator runs themselves.

So the real choice:

- **Galileo**: scoring is the *default product behavior* — opting out requires action. Generic metrics applied to every trace, tuned for typical agent quality questions.
- **Langfuse / LangSmith**: scoring is *opt-in* — you have to know what you want to measure and configure it once. Then it runs forever, on exactly the traces you scoped, scoring exactly the rubric you defined.

**Which is better depends on your team's stage**:
- Don't know your quality rubric yet, want sensible defaults to spot obvious problems → Galileo
- Have specific quality definitions that don't match generic templates → Langfuse / LangSmith
- Both can converge: Galileo lets you add custom metrics; Langfuse/LangSmith let you configure as many evaluators as you want

## Honest weaknesses to flag

- **Langfuse**: UI polish trails LangSmith. Monitoring dashboards less mature. Self-host = self-operate (cost moves from license to ops).
- **LangSmith**: SaaS-only at the community tier. No free self-host. Vendor-tied to LangChain even though it works elsewhere via `@traceable`.
- **Galileo**: **Work-email signup gate** (real evaluation friction). SDK API churn between versions. Documentation lighter than the other two. Smaller framework ecosystem. Pricing less transparent.

---

## Scenario sufficiency analysis

This section evaluates whether the **four scenarios currently in `shared/workflow.py`** are enough to demonstrate the platform differences captured in the matrix above.

### What the current 4 scenarios exercise

| Scenario | Tool calls | Exercises |
| --- | --- | --- |
| `one_tool` | 1 | Trace tree minimum case, exact-match scoring |
| `two_tools` | 2 | Dependency chain, set-comparison scoring |
| `three_tools` | 3 | Multi-step agent reasoning, boolean scoring |
| `judgment_call` | 4 | Open-ended judgment, LLM-as-judge fit, all tools used |

The current set **does cover**:
- ✅ Basic trace tree (matrix A1–A4)
- ✅ LangChain integration (B1)
- ✅ Session/thread grouping (C1)
- ✅ Tagging + metadata + filter (D1–D3)
- ✅ Programmatic scoring (E1–E3)
- ✅ LLM-as-judge fit (F1, F3)
- ✅ Dataset registry (G1–G2)
- ✅ Prompt registry (I1–I3)
- ✅ Trace ↔ prompt linkage (I8)

The current set **does NOT exercise**:
- ❌ **Error / exception handling in traces** (A6) — no scenario where a tool fails
- ❌ **Multi-turn conversation** (C2 Threads view) — all scenarios are single-turn
- ❌ **Hallucination / faithfulness scoring** (F3) — agent stays grounded in tool outputs
- ❌ **Tool Error Rate metric** (Galileo F4) — no failed tool calls
- ❌ **Streaming behavior** (A5) — using `.invoke()` not `.stream()`
- ❌ **Experiment / dataset run** (H1) — datasets exist but no experiment runs them
- ❌ **Pairwise comparison** (H5) — only one prompt version
- ❌ **Prompt versioning / diff** (I9) — single prompt version
- ❌ **PII handling** (F9, L2) — no PII in the data
- ❌ **Toxicity** (F8, L5) — no adversarial inputs
- ❌ **Long-running / high-volume traffic** (K1, K5) — only ~4 traces total
- ❌ **Cost-tier divergence at scale** — too few traces to surface differences
- ❌ **Annotation queue workflow** (E7) — no human review demonstrated

### Verdict on sufficiency

**The current 4 scenarios are sufficient for a baseline demo** of:
- "Same agent, three UIs, here's the trace"
- "Each platform has prompt registries and datasets"
- "LLM-as-judge fits open-ended scenarios"

They are **NOT sufficient** to demonstrate:
- The full evaluation-vs-observability divide between Galileo and the other two
- LangSmith's Threads / pairwise / splits advantages
- Galileo's Protect or built-in PII/hallucination metrics
- Real production scale (dashboards, alerts, monitoring tabs all look empty)

### Recommended additional scenarios

Numbered by demo value. Adding **3–4 of these** would fully exercise the matrix.

#### Tier 1 — biggest deck impact, lowest implementation cost

1. **Error path** ✅ implemented — `unknown_employee` scenario where the user asks about "Nobody McNobody" → `get_ads_id` returns an error message → agent recovers gracefully. Demonstrates A6 (error capture), F4 (Tool Error Rate metric in Galileo), how each UI renders failures. Notebooks: `notebooks/{langfuse,langsmith,galileo}/error_path.ipynb`.

2. **Multi-turn conversation** ✅ implemented — a 3-turn chat where each turn refines the question. e.g. "Tell me about Jane Doe" → "What can she access?" → "Should she keep admin?". Demonstrates C2 (Threads view in LangSmith), C4 (session-level scoring in Langfuse), how each UI renders chat. Notebooks: `notebooks/{langfuse,langsmith,galileo}/multi_turn.ipynb`.

3. ~~**Hallucination injection**~~ — **dropped after empirical testing**: with Claude as the agent model, even a deliberately loosened system prompt didn't reliably trigger fabrication on probes like "who was Jane's previous manager?". Claude's safety behavior is robust enough that hallucination is hard to demo cleanly without picking a different model or crafting unnatural prompts. Skipping this is intentional — model choice matters more than platform choice for hallucination prevention, and that's a valid takeaway on its own.

#### Tier 2 — moderate complexity, important for completeness

4. **Dataset experiment run** — take the 4-row dataset we have, call `client.evaluate(agent, data=dataset)` in LangSmith and equivalent in others. Demonstrates H1–H7 (experiments and pairwise comparison).

5. **Prompt v2 (stricter brevity)** — push a v2 system prompt that requires single-sentence answers, run the same scenarios, compare. Demonstrates I3 (versioning model), I4 (Langfuse labels), I9 (diff view), pairwise experiment compare.

6. **PII scenario** — a prompt like "Is John Smith's home address `123 Main St, Apt 4B, Seattle` correct?" — adds PII text to the trace. Demonstrates F9 (Galileo auto-PII), the absence in others.

#### Tier 3 — production simulation, higher cost

7. **Volume burst** — script that fires 100–500 traces in a few minutes. Demonstrates K1 (monitoring time-series), K5 (metric distribution histograms), K6 (threshold alerts firing). Needed if you want the dashboards to look populated.

8. **Streaming agent run** — `.astream_events()` instead of `.invoke()`. Demonstrates A5 (streaming UI rendering) in each platform.

9. **Human annotation walkthrough** — show one trace going through an annotation queue. Demonstrates E7 (queues UX), E8 (agreement metrics). UI-driven, no code.

### My recommendation for THIS deck

For a **45-min internal eng + PM/leadership** talk, **Tier 1 #1–#2 are now implemented**. The hallucination scenario was dropped after testing (see note above). Next candidate from Tier 2 is **#4 (dataset experiments)** to cover the experiment-comparison matrix rows.

Current scenario coverage:
- Baseline: 5 scenarios in `shared/workflow.py` (`one_tool`, `two_tools`, `three_tools`, `judgment_call`, `error_path`)
- Multi-turn helper: `MULTI_TURN_CONVERSATION` (3 turns)
- Per-platform scenario notebooks: 2 per platform (error_path, multi_turn) = 6 total
- Total demoable runs: 7 scenarios × 3 platforms = 21 traces, plus session/thread groupings

### Implementation status

| Scenario | Status | Files |
| --- | --- | --- |
| #1 Error path | ✅ done | `notebooks/{langfuse,langsmith,galileo}/error_path.ipynb` |
| #2 Multi-turn | ✅ done | `notebooks/{langfuse,langsmith,galileo}/multi_turn.ipynb` |
| #3 Hallucination | ⏭️ dropped (Claude too robust) | — |
| #4 Dataset experiment | ⏳ proposed | would add `notebooks/{langfuse,langsmith,galileo}/experiment.ipynb` |
