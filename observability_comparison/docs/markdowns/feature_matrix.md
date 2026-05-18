# Feature Matrix — Langfuse vs LangSmith vs Galileo

Comprehensive feature comparison across ~120 capabilities, split into 19 sub-categories (A–S) for readability. Companion to [`comparison.md`](comparison.md), which has the narrative analysis, decision guidance, and scenario coverage discussion.

## Legend

| Symbol | Meaning |
| --- | --- |
| ✅ | supported, parity with the others |
| ⭐ | supported AND best-in-class implementation |
| ⚠️ | partial support / with notable caveat — see Notes below each table |
| ❌ | not supported / requires you to build it yourself |

## Table of contents

- [A. Core observability](#a-core-observability)
- [B. Instrumentation surfaces](#b-instrumentation-surfaces)
- [C. Multi-turn / sessions / threads](#c-multi-turn--sessions--threads)
- [D. Filtering & search](#d-filtering--search)
- [E. Scoring & feedback primitives](#e-scoring--feedback-primitives)
- [F. Automated / LLM-as-judge evaluation](#f-automated--llm-as-judge-evaluation)
- [G. Datasets](#g-datasets)
- [H. Experiments](#h-experiments)
- [I. Prompt management](#i-prompt-management)
- [J. Playground / span replay](#j-playground--span-replay)
- [K. Production monitoring](#k-production-monitoring)
- [L. In-request guardrails](#l-in-request-guardrails)
- [M. Production routing](#m-production-routing)
- [N. Access control & multi-tenancy](#n-access-control--multi-tenancy)
- [O. Compliance](#o-compliance)
- [P. Hosting](#p-hosting)
- [Q. Pricing & onboarding](#q-pricing--onboarding)
- [R. SDK / DX](#r-sdk--dx)
- [S. Ecosystem](#s-ecosystem)

---

## A. Core observability

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Trace capture | ✅ | ✅ | ✅ |
| Hierarchical span tree | ✅ | ⭐ | ✅ |
| LLM call detail | ✅ | ✅ | ✅ |
| Tool call detail | ✅ | ✅ | ✅ |
| Streaming response capture | ✅ | ⭐ | ✅ |
| Error / exception capture | ✅ | ✅ | ✅ |
| Latency p50/p95/p99 rollups | ✅ | ⭐ | ✅ |
| Cost in USD (built-in pricing) | ✅ | ✅ | ✅ |
| Custom model pricing | ✅ | ✅ | ✅ |
| Multi-modal: images | ✅ | ✅ | ✅ |
| Multi-modal: audio/video | ⚠️ | ⚠️ | ⚠️ |

**Notes**
- *Multi-modal audio/video (all three ⚠️)*: basic ingestion as attached files / data URLs works, but none of the three has a dedicated audio/video viewer or analytics. Plays okay for logging, weak for inspection.

## B. Instrumentation surfaces

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| LangChain / LangGraph integration | ✅ callback | ⭐ zero-config | ✅ callback |
| Generic function decorator | ✅ `@observe` | ✅ `@traceable` | ✅ `@log` |
| OpenAI SDK wrapper | ✅ | ✅ | ✅ |
| Anthropic SDK wrapper | ✅ via OTEL | ✅ | ✅ |
| LlamaIndex | ✅ | ✅ | ⚠️ |
| LiteLLM | ✅ | ✅ | ✅ |
| DSPy | ✅ via OTEL | ✅ | ⚠️ |
| CrewAI | ✅ | ✅ | ✅ |
| OTEL ingestion | ⭐ most mature | ✅ | ✅ |
| OTEL export to external | ✅ | ✅ | ⚠️ |
| REST API for all operations | ✅ | ✅ | ✅ |

**Notes**
- *LlamaIndex on Galileo (⚠️)*: integration exists but less battle-tested than on Langfuse/LangSmith; expect occasional missing span fields.
- *DSPy on Galileo (⚠️)*: newer integration; some span types may not render perfectly.
- *OTEL export Galileo (⚠️)*: Galileo ingests OTEL but its outbound OTEL export to third-party backends is more limited than the other two.

## C. Multi-turn / sessions / threads

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Session/thread grouping by metadata | ✅ | ✅ | ✅ |
| Dedicated multi-turn UI view | ✅ Sessions | ⭐ Threads (chat UI) | ✅ Sessions |
| Per-session aggregates | ✅ | ✅ | ✅ |
| Session-level scoring | ✅ | ✅ via run | ⚠️ |

**Notes**
- *Session-level scoring Galileo (⚠️)*: scores primarily attach to traces, not sessions as a first-class entity. You can aggregate trace-level scores per session, but there's no "score this whole session" primitive.

## D. Filtering & search

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Tags + metadata | ✅ | ✅ | ✅ |
| Filter UI | ✅ | ⭐ | ✅ |
| Saved filter views | ✅ | ✅ | ✅ |
| Filter by score value | ✅ | ✅ | ⭐ |
| Boolean / regex expressions | ⚠️ | ✅ | ⚠️ |

**Notes**
- *Boolean / regex on Langfuse (⚠️)*: supports filter chips with key/value matching but not complex boolean expressions or regex patterns in a single filter.
- *Boolean / regex on Galileo (⚠️)*: same limitation — filters are field/value pairs combined with AND, no regex.

## E. Scoring & feedback primitives

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Programmatic SDK scoring | ✅ | ✅ | ✅ |
| Numeric / boolean / categorical | ✅ | ✅ | ✅ |
| Multiple scores per trace | ✅ | ✅ | ✅ |
| Score attaches to sub-span | ✅ | ✅ | ⚠️ |
| Score attaches to session | ✅ | ✅ | ⚠️ |
| Manual UI annotation | ✅ | ✅ | ✅ |
| Annotation queues | ✅ | ⭐ | ✅ |
| Inter-rater agreement | ✅ | ✅ | ⚠️ |

**Notes**
- *Score attaches to sub-span Galileo (⚠️)*: Galileo's primary scoring target is the trace; span-level score attachment is less developed in the SDK than on Langfuse/LangSmith.
- *Score attaches to session Galileo (⚠️)*: sessions aren't a first-class scoring target — see note in section C.
- *Inter-rater agreement Galileo (⚠️)*: annotation queues exist but agreement-metric reporting is less polished than LangSmith/Langfuse.

## F. Automated / LLM-as-judge evaluation

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| LLM-as-judge (configurable) | ✅ | ✅ | ✅ |
| **Auto-metrics on every trace, no config** | ❌ | ❌ | ⭐ |
| Pre-built faithfulness / grounding | ⚠️ build it | ✅ | ⭐ ChainPoll |
| Pre-built tool-selection-quality | ❌ | ⚠️ | ⭐ |
| Pre-built action-completion | ❌ | ⚠️ | ⭐ |
| Pre-built helpfulness / correctness | ✅ | ⭐ | ✅ |
| Heuristic evaluators (regex / JSON / exact) | ⚠️ | ⭐ largest library | ⚠️ |
| Pre-built toxicity / safety | ✅ | ✅ | ⭐ |
| Pre-built PII detection | ⚠️ | ⚠️ | ⭐ |
| Online (auto on production) eval | ✅ | ⭐ formalized | ⭐ |
| Offline (against dataset) eval | ✅ | ✅ | ✅ |
| Continuous learning on metrics | ❌ | ⚠️ | ⭐ |

**Notes**
- *Faithfulness Langfuse (⚠️ build it)*: not provided as a turnkey evaluator template — you write your own LLM-as-judge prompt against the trace's tool/retrieval outputs.
- *Tool-selection-quality LangSmith (⚠️)*: you build a custom evaluator with a prompt that compares chosen tools vs. expected. No drop-in template.
- *Action-completion LangSmith (⚠️)*: same — assemble it yourself from a multi-criteria LLM-as-judge.
- *Heuristic evaluators Langfuse (⚠️)*: has a smaller library than LangSmith; some heuristics (regex, exact match) are easy to implement as scoring functions but not pre-packaged.
- *Heuristic evaluators Galileo (⚠️)*: similarly leaner — Galileo's focus is the LLM-judged auto-metrics suite, not the heuristic library.
- *PII detection Langfuse (⚠️)*: no built-in PII evaluator; configure an LLM-as-judge or use an external service.
- *PII detection LangSmith (⚠️)*: same.
- *Continuous learning LangSmith (⚠️)*: some adaptive evaluator capabilities exist but not as mature as Galileo's continuous-learning feature loop.

## G. Datasets

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Create datasets via SDK | ✅ | ✅ | ✅ |
| Item / Example structure | ✅ free-form | ✅ typed | ✅ flat row |
| Bulk import (CSV / JSON) | ✅ | ✅ | ✅ |
| Trace → dataset promotion | ✅ | ⭐ one-click UI | ✅ |
| **Splits (train / test / eval)** | ❌ | ⭐ unique | ❌ |
| Item-level immutable versioning | ⚠️ | ⭐ | ⚠️ |
| Dataset-level versioning | ❌ | ✅ | ✅ |
| **Synthetic dataset generation** | ❌ | ❌ | ⭐ unique |

**Notes**
- *Item-level versioning Langfuse (⚠️)*: dataset items are mutable; editing one overwrites it. No per-item version history (only LangSmith offers immutable example versions).
- *Item-level versioning Galileo (⚠️)*: dataset-level versioning exists but per-row versioning isn't a first-class concept.

## H. Experiments

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Run agent against dataset | ✅ | ⭐ `client.evaluate()` | ✅ |
| Auto-score each row | ✅ | ✅ | ⭐ auto-metrics |
| Experiment-level aggregates | ✅ | ✅ | ✅ |
| Experiment comparison view | ✅ | ⭐ | ✅ |
| **Pairwise A/B comparison UI** | ⚠️ | ⭐ unique | ⚠️ |
| Regression detection | ⚠️ | ⭐ | ⚠️ |

**Notes**
- *Pairwise comparison Langfuse (⚠️)*: you can pick two experiments and view them side by side, but there's no dedicated "diff two runs" UI like LangSmith's.
- *Pairwise comparison Galileo (⚠️)*: similar — experiment-comparison view exists but isn't optimized for run-level A/B inspection.
- *Regression detection Langfuse (⚠️)*: you can compare baseline vs. new experiment scores manually; no automatic "this regressed" callouts.
- *Regression detection Galileo (⚠️)*: same — manual comparison only.

## I. Prompt management

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Versioned prompt registry | ✅ | ✅ | ✅ |
| Pull from SDK | ✅ string | ⭐ LangChain Runnable | ⚠️ JSON-parse needed |
| Versioning model | Sequential + labels | ⭐ Git-style commits | Sequential only |
| **Mutable label pointers** (e.g. `production`) | ⭐ unique | ⚠️ via tags | ❌ |
| Idempotent push on no-change | ❌ | ⭐ 409 native | ❌ |
| Raw-string AND chat formats | ⭐ both | ⚠️ Runnable-only | ❌ chat only |
| Variable templating | ✅ Mustache | ✅ LangChain | ✅ |
| Prompt → trace auto-linkage | ✅ | ✅ | ⚠️ |
| Diff view between versions | ✅ | ✅ | ⚠️ |
| **Public sharing / Prompt Hub** | ❌ | ⭐ unique | ❌ |
| SDK caching | ⭐ | ✅ | ⚠️ |

**Notes**
- *Pull from SDK Galileo (⚠️ JSON-parse needed)*: `get_prompt()` returns a `PromptTemplate` whose `template` field is a JSON string of message dicts. You must `json.loads()` and walk the structure to extract content. We hit this bug in our `fetch_system_prompt("galileo")` and fixed it explicitly.
- *Mutable label pointers LangSmith (⚠️ via tags)*: LangSmith doesn't expose mutable named pointers like Langfuse's `production` label. You simulate by tagging commits and pulling by tag — workable but less ergonomic for promotion workflows.
- *Raw-string format LangSmith (⚠️)*: all prompts are LangChain `Runnable` objects (typically `ChatPromptTemplate`). Plain-string prompts work only by wrapping them as a single-message ChatPromptTemplate.
- *Prompt → trace auto-linkage Galileo (⚠️)*: traces don't automatically record which prompt template version was used; you'd attach prompt id manually as metadata.
- *Diff view Galileo (⚠️)*: version history visible in the UI but a visual two-pane diff is less polished than Langfuse/LangSmith.
- *SDK caching Galileo (⚠️)*: less mature client-side cache; each `get_prompt` call typically hits the API.

## J. Playground / span replay

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Edit & re-run an LLM span | ✅ | ⭐ best UX | ⚠️ |
| Free-form prompt sandbox | ✅ | ✅ | ⭐ |
| Side-by-side model compare | ✅ | ⭐ | ✅ |
| Save run → dataset example | ✅ | ⭐ | ✅ |
| Playground runs flow to log stream | ✅ | ✅ | ❌ separate concept |

**Notes**
- *Edit & re-run an LLM span Galileo (⚠️)*: Galileo's Playground is a separate top-level area, not a trace-replay tool. You can copy a prompt from a trace into the Playground manually, but there's no "open this trace's LLM call in Playground" button like LangSmith offers.

## K. Production monitoring

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Time-series volume / latency / errors | ✅ | ⭐ | ✅ |
| Per-model breakdowns | ✅ | ✅ | ✅ |
| Per-user / per-tag breakdowns | ✅ | ✅ | ✅ |
| Custom dashboards | ✅ | ✅ | ⚠️ |
| Metric distribution histograms | ⚠️ | ✅ | ⭐ |
| Threshold alerts | ✅ | ⭐ | ✅ |
| Slack / PagerDuty routing | ✅ | ✅ | ✅ (PD Enterprise) |
| Datadog metric export | ✅ Enterprise | ✅ Enterprise | ✅ Enterprise |
| Period-over-period comparison | ✅ | ⭐ | ⚠️ |

**Notes**
- *Custom dashboards Galileo (⚠️)*: standard dashboards are present (volume, latency, metric distribution) but a custom dashboard builder is less mature than on Langfuse/LangSmith.
- *Metric distribution histograms Langfuse (⚠️)*: you can see score distributions per dataset but not as prominently surfaced as Galileo's per-trace metric histograms.
- *PagerDuty Galileo (⚠️ Enterprise)*: PagerDuty integration is Enterprise-tier only; Slack works on lower tiers.
- *Period-over-period comparison Galileo (⚠️)*: time-range comparison less developed than LangSmith's monitoring tab.

## L. In-request guardrails

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| **Real-time block / modify requests** | ❌ | ❌ | ⭐ **Galileo Protect** |
| Hallucination block in-flight | ❌ | ❌ | ⭐ |
| PII redaction at gateway | ❌ | ❌ | ⭐ |
| Toxicity guardrails | ❌ | ❌ | ⭐ |
| Custom guardrail rules | ❌ | ❌ | ⭐ |

**Notes**: no ⚠️ in this section. Entire category is Galileo's home turf — the other two are post-hoc observability and don't sit in the request path.

## M. Production routing

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| **Log Stream within project** (dev/staging/prod) | ⚠️ Environments (newer) | ❌ separate projects | ⭐ |
| A/B prompts via labels | ⭐ | ✅ via tags | ⚠️ |
| Platform-managed traffic splitting | ❌ | ⚠️ Enterprise | ❌ |

**Notes**
- *Log Stream Langfuse (⚠️ Environments newer)*: Langfuse's Environments feature is converging on the Log Streams concept but is more recently introduced and less established.
- *A/B prompts Galileo (⚠️)*: possible via Experiments comparing prompt A vs prompt B, but no in-production label-pointer mechanism like Langfuse for live A/B.
- *Traffic splitting LangSmith (⚠️ Enterprise)*: managed traffic-splitting between prompt versions is an Enterprise-tier feature, not in Developer/Plus.

## N. Access control & multi-tenancy

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Organizations / workspaces | ✅ | ✅ | ✅ |
| Projects | ✅ | ✅ | ✅ |
| Basic RBAC | ✅ | ✅ | ✅ |
| Granular RBAC | ⚠️ Ent | ⭐ Ent | ⚠️ Ent |
| SSO (SAML / OIDC) | ✅ Ent | ✅ Plus+ | ✅ Ent |
| Scoped API tokens | ✅ | ⭐ service tokens | ✅ |

**Notes**
- *Granular RBAC Langfuse (⚠️ Ent)*: fine-grained per-resource roles exist but require an Enterprise plan; lower tiers have basic Admin/Member/Viewer only.
- *Granular RBAC Galileo (⚠️ Ent)*: same situation — paid tier gates the granular permission model.

## O. Compliance

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| SOC 2 Type 2 | ✅ Cloud | ✅ | ✅ |
| GDPR | ✅ | ✅ | ✅ |
| HIPAA | ⭐ self-host gives full control | Ent | Ent / VPC |
| EU data residency | ✅ | ✅ | ⚠️ on request |
| Data residency anywhere (self-host) | ⭐ free | ❌ | ⭐ VPC paid |

**Notes**
- *EU data residency Galileo (⚠️ on request)*: not a self-serve region toggle — you must contact sales to provision an EU deployment. Langfuse Cloud and LangSmith Cloud both offer a one-click EU region.

## P. Hosting

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| SaaS managed | ✅ | ⭐ | ✅ |
| **OSS free self-host** | ⭐ unique | ❌ | ❌ |
| Enterprise self-host (k8s) | ✅ | ✅ Helm | ✅ VPC |
| Air-gapped | ✅ Ent | ⚠️ | ✅ Ent |
| Free local dev | ⭐ docker | ❌ | ❌ |

**Notes**
- *Air-gapped LangSmith (⚠️)*: technically possible via the Self-Hosted Helm deployment but requires significant support engagement; not packaged as a turnkey air-gapped distribution like Langfuse/Galileo offer at the Enterprise tier.

## Q. Pricing & onboarding

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Free entry (no credit card) | ⭐ self-host OR Hobby | ✅ Developer | ✅ free tier |
| Personal email signup | ✅ | ✅ | ❌ work email required |
| Transparent published pricing | ✅ | ✅ | ⚠️ some tiers require sales |
| Free-tier retention | ⭐ self-host forever | 14 days | varies |
| Volume cap clarity | varies | ⭐ 5k/mo clear | varies |

**Notes**
- *Pricing transparency Galileo (⚠️)*: free + Developer tiers list pricing publicly, but Pro/Enterprise pricing requires a sales conversation. Langfuse and LangSmith publish all tier prices.

## R. SDK / DX

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| Python SDK maturity | ✅ | ✅ | ⚠️ churn |
| TypeScript SDK | ✅ | ✅ | ⚠️ less mature |
| API stability | ✅ | ✅ | ⚠️ |
| Documentation quality | ✅ | ⭐ | ✅ |
| Async / background flush | ✅ | ✅ | ✅ |
| OSS contributions | ⭐ | n/a | n/a |

**Notes**
- *Python SDK maturity Galileo (⚠️ churn)*: API surface has shifted noticeably between releases — for example, the prompt-template return shape changed from typed Message objects to a JSON string. Upgrades may require code adjustments.
- *TypeScript SDK Galileo (⚠️ less mature)*: TS SDK exists but lags the Python SDK in feature coverage and stability.
- *API stability Galileo (⚠️)*: follows from the SDK churn — semver isn't strictly respected across minor versions.

## S. Ecosystem

| Capability | 🔵 Langfuse | 🟢 LangSmith | 🟠 Galileo |
| --- | --- | --- | --- |
| **Public prompt marketplace** | ❌ | ⭐ Hub | ❌ |
| Webhooks on alerts | ✅ | ✅ | ✅ |
| Bulk export to warehouse | ✅ Ent | ✅ Ent | ✅ Ent |

**Notes**: no ⚠️ in this section.

---

## Where to next

- **For the narrative analysis and decision guidance**: see [`comparison.md`](comparison.md)
- **For unique strengths per platform**: see "Where each platform uniquely wins" in [`comparison.md`](comparison.mdhere-each-platform-uniquely-wins)
- **For "is our demo enough?"**: see "Scenario sufficiency analysis" in [`comparison.md`](comparison.mdcenario-sufficiency-analysis)
