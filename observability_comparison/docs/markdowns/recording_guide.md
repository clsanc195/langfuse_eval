# Screen Recording Guide — Langfuse / LangSmith / Galileo Demo

One short screen recording per platform (~3 min each) walking through every feature this repo touches. Recordings will be the primary visual asset for the comparison deck.

## Output location

Save recordings to `docs/recordings/`:

| Filename | Platform |
| --- | --- |
| `01-langfuse.mp4` | 🔵 Langfuse |
| `02-langsmith.mp4` | 🟢 LangSmith |
| `03-galileo.mp4` | 🟠 Galileo |

## Common pre-flight

Do this **once** before recording any platform — same setup keeps the three recordings visually consistent so they line up nicely in slides.

| Item | Setting |
| --- | --- |
| **Browser** | Chrome or Arc (any modern Chromium) |
| **Window size** | Maximized at **1920×1080**, OR consistent across all 3 recordings |
| **Theme** | Light mode if your projector / audience prefers; dark is fine if you're staying digital |
| **Browser zoom** | 100% — don't zoom in (the recorder captures actual pixels) |
| **Hide bookmarks bar** | `Cmd+Shift+B` (Chrome) — reduces noise above the page |
| **Close other tabs** | Just keep the target platform's tab open per recording |
| **Recorder** | macOS: QuickTime `Cmd+Shift+5 → Record Selected Portion` works fine. For better quality: [OBS](https://obsproject.com) or [Loom](https://loom.com) |
| **Audio** | Off (silent) — you'll narrate live OR add captions in post. Less to re-shoot if you fumble a word. |
| **Mouse highlight** | Optional — Loom does this natively, or use [Mouseposé](https://boinx.com/mousepose/) on macOS. Helps audience track clicks. |
| **Frame rate** | 30 fps is plenty |
| **Duration** | Aim for **~3 min per platform**. If you hit 5+ min, you're showing too much. |

## Recording tip

**Practice once before hitting record.** Click through the full flow without recording, get the muscle memory, then start recording and run it cleanly. Re-takes are cheap; editing voice-overs is not.

---

## 🔵 Recording 1 — Langfuse (`01-langfuse.mp4`)

**Goal**: show that Langfuse covers all the basics + is self-hostable + has versioned prompts + supports scoring/evaluators.

**Pre-recording setup**:
1. Open <http://localhost:3000>
2. Navigate to your project
3. Left sidebar should be visible
4. Make sure docker is running (`docker ps | grep langfuse` shows containers up)

### Scene 1 — Trace list (~20 sec)

1. Land on **Tracing → Traces**
2. Apply filter: **Session ID** = `permission-checks-demo` (or filter by tag `observability_comparison`)
3. **Hover over** the columns dropdown → enable **Scores** if not already enabled
4. Show the table: 10 demo traces (5 base + 5 scored variants)
5. Point to the Scores column → values populated on the `__scored` rows

**Voice-over (if any)**: "Langfuse Traces view. Filtered to our demo session, 10 traces total, with programmatic scores on the right."

### Scene 2 — Open a trace (~30 sec)

1. Click the `judgment_call` trace (or `three_tools` if `judgment_call` isn't there)
2. Show the **tree on the left** — agent / ToolNode / agent / etc.
3. **Pause for ~2 seconds** so viewers can read the hierarchy
4. Hover over one node → tooltip shows latency + tokens

### Scene 3 — LLM span detail (~20 sec)

1. From inside the trace, click on the **first LLM/Generation observation** in the tree
2. Right panel shows: input messages, output, model, token usage, cost
3. **Scroll** so the prompt is visible at top, completion at bottom

### Scene 4 — Tool span detail (~15 sec)

1. Click any tool observation (e.g. `get_ads_id`)
2. Right panel: input JSON (`{"employee_name": "Jane Doe"}`), output JSON (`"ADS-1001"`), latency
3. Show that errors show up here too — back to trace list, find `error_path` trace, click `get_ads_id` → output is the `ERROR:` string

### Scene 5 — Scores (~20 sec)

1. Back to trace list
2. Click a `__scored` trace (e.g. `three_tools__scored`)
3. Right panel → **Scores** section shows `tool_call_count_matches = 1.0` with comment
4. If you have the **Conciseness** LLM-as-judge evaluator running, scores from it should also appear

### Scene 6 — Sessions (~25 sec)

1. Left sidebar → **Sessions**
2. Click into `permission-checks-demo`
3. Show all the demo traces grouped together
4. **Point out**: aggregate token/cost/latency at the top of the panel

### Scene 7 — Prompts (~25 sec)

1. Left sidebar → **Prompts**
2. Show `permission-agent-system` in the list
3. Click into it
4. Show the prompt content
5. Show the **`production`** label badge
6. If multiple versions exist: click **Versions** tab → diff view

### Scene 8 — Datasets (~20 sec)

1. Left sidebar → **Datasets**
2. Show `permission-agent-scenarios` in the list
3. Click into it
4. Show the 4 items with their input/expected output

### Scene 9 — Evaluators (~30 sec) — important nuance

1. Left sidebar → **Evaluation** (or **Evaluators**)
2. Show the Conciseness LLM-as-judge evaluator you set up earlier
3. **Show evidence it's running**: back to trace list, scroll to find traces named `Execute evaluator: Conciseness` — those are Langfuse running your evaluator
4. Click into a recent demo trace → Right panel → Scores section → show the Conciseness score that was auto-applied

**Suggested narration / caption**:
> "Same mechanism as Galileo's auto-metrics — once I configure an evaluator, it runs automatically on every matching trace. The difference: I had to pick what to score. I picked Conciseness; you could pick anything. Galileo picks for you. Same automation, different defaults."

This framing is important — without it the audience thinks Langfuse can't auto-score, which is wrong. See `comparison.md` → "On evaluator automation" for the full nuance.

### Closing shot (~5 sec)

1. Back to trace list with the demo data visible — gives a clean end frame

**Total target**: ~3 minutes

---

## 🟢 Recording 2 — LangSmith (`02-langsmith.mp4`)

**Goal**: show LangSmith's polished UX, especially Threads (the killer differentiator for chat), Playground replay, and Prompt Hub.

**Pre-recording setup**:
1. Open <https://smith.langchain.com>
2. Make sure you're in the right workspace (top-left workspace switcher)
3. Navigate to project `lansmith_trial` (or whatever you set `LANGSMITH_PROJECT` to)

### Scene 1 — Runs list (~20 sec)

1. Land on the project's **Runs** tab
2. Filter: tag contains `observability_comparison` (or filter by `thread_id` = `permission-checks-demo`)
3. Show the table with demo runs

### Scene 2 — Open a run (~30 sec)

1. Click `judgment_call` run
2. Show the trace tree — **LangSmith's tree rendering is the strongest of the three**, point this out
3. Hover nodes to show latency / token rollups

### Scene 3 — LLM run detail + Playground (HERO — ~45 sec)

1. Click into the first LLM run within the trace
2. Right panel shows prompt / completion / tokens
3. **Click the "Playground" button** at the top of the LLM run panel
4. Playground opens with the prompt pre-filled
5. **Edit the prompt** (e.g. change a word) → click **Submit**
6. Show the new response below the editable prompt
7. **This is the killer LangSmith screenshot** — replay any LLM call with edits

### Scene 4 — Tool run detail (~15 sec)

1. Back to the trace
2. Click any tool-type run (e.g. `get_ads_id`)
3. Show input/output JSON

### Scene 5 — Threads (HERO for chat — ~30 sec)

1. Top nav (inside project) → **Threads** tab
2. Click into `permission-checks-demo`
3. **Show the chat-UI rendering of the 3 multi-turn turns**
4. This is the most visually distinctive thing LangSmith offers — pause for ~3 seconds

### Scene 6 — Prompts (Prompt Hub) (~25 sec)

1. **Leave the project view** — go to workspace-level top nav
2. Click **Prompts** (it's not inside the project — it's at workspace level)
3. Show `permission-agent-system` in the list
4. Click into it
5. Show the **commit hash** version model
6. If multiple commits: show the diff view between two commits

### Scene 7 — Datasets & Experiments (~20 sec)

1. Top nav → **Datasets & Experiments**
2. Show `permission-agent-scenarios`
3. Click into it → show the 4 examples
4. (No experiments yet — note "this is where the experiment-comparison UI lives, we haven't run one")

### Scene 8 — Monitoring (~20 sec)

1. Back to the project view
2. Top nav → **Monitor** tab
3. Show the time-series dashboards
4. **Mention**: "this is the most polished production dashboard of the three"

### Scene 9 — Online Evaluators (~30 sec) — important nuance

1. Top nav → **Rules** (or **Automations** / **Online Evaluators** — name varies by UI version)
2. Show the `conciseness-check` evaluator you configured (mirrors the Langfuse Conciseness evaluator)
3. Show the config: filter (is_root=true), sampling rate, target evaluator
4. Back to a recent trace in the project → Right panel → Feedback section → show the auto-applied `conciseness` score
5. **Optional**: search the project for runs with `run_name` like `LLM-Judge-Evaluator` — those are the evaluator's own runs

**Suggested narration / caption**:
> "LangSmith Online Evaluators — same mechanism as Langfuse's. Configure once, runs server-side on every matching trace forever. I set up Conciseness for parity with the Langfuse setup. Same automation pattern as Galileo, but I had to pick what to measure. All three platforms can do this — the difference is whether the defaults pick for you."

This framing keeps parity with the Langfuse Scene 9 narrative and is the most important slide-pair of the deck for the eval section. See `comparison.md` → "On evaluator automation" for the full nuance.

### Closing shot (~5 sec)

End on the Monitor or Threads view — both visually striking.

**Total target**: ~3 min 45 sec (Playground + Threads + Evaluators all worth lingering on)

---

## 🟠 Recording 3 — Galileo (`03-galileo.mp4`)

**Goal**: show Galileo's headline differentiator — **auto-metrics on every trace** + Insights panel + Protect concept.

**Pre-recording setup**:
1. Open <https://app.galileo.ai>
2. Navigate to your project (`galileo_trial` or whatever you set `GALILEO_PROJECT` to)
3. Navigate to log stream `default`
4. Confirm you can see the demo traces

### Scene 1 — Log stream view (~20 sec)

1. Land on the log stream `default`
2. Show the trace list filtered by tag `observability_comparison` (or session `permission-checks-demo`)
3. Demo traces should be visible
4. **Mention Log Streams**: "Galileo separates traffic by log stream — dev/staging/prod live as siblings within a project. The other two platforms don't have this."

### Scene 2 — Open a trace + Insights panel (HERO — ~45 sec)

1. Click the `judgment_call` trace
2. Show the trace tree
3. **Open the Insights / Metrics panel** (usually a right side panel or a tab)
4. **Point out the auto-computed metrics**:
   - Tool Selection Quality
   - Action Completion
   - Context Adherence
   - Instruction Adherence
   - Tool Error Rate
5. **Pause for 5+ seconds** so the audience can read them

**Suggested narration / caption** (honest framing — important):
> "Galileo's headline feature: this panel auto-populated. No evaluator config, no prompt template, no sampling rate to set. Compare with Langfuse and LangSmith — both can run evaluators automatically once you configure them, but you have to know which metrics to set up. Galileo picks for you. Better default for teams that don't know their rubric yet; can be noise for teams that have specific quality definitions."

This nuance matters — without it, the deck implies Langfuse/LangSmith can't auto-score, which is wrong (their Online Evaluators run on every matching trace once configured).

### Scene 3 — A flagged metric (~25 sec)

1. Find the `error_path` trace (the Nobody McNobody one)
2. Click in, show the Insights panel
3. **Tool Error Rate should reflect the failed tool call**
4. **Context Adherence should be high** (agent didn't fabricate, it acknowledged the error)

### Scene 4 — LLM span (~15 sec)

1. From a trace, click an LLM span
2. Show prompt / completion / tokens

### Scene 5 — Tool span (~15 sec)

1. Click a tool span
2. Show input / output

### Scene 6 — Sessions (~20 sec)

1. Navigate to the sessions view
2. Show `permission-checks-demo` session
3. Note: Galileo's session UX is less polished than LangSmith's Threads — be honest about it

### Scene 7 — Prompts / Templates (~25 sec)

1. Navigate to **Prompts** or **Templates** in the project
2. Show `permission-agent-system`
3. Click in, show the chat-message structure (note: Galileo prompts are chat-only)
4. Note: project-scoped (vs LangSmith's workspace-scoped)

### Scene 8 — Datasets (~15 sec)

1. Navigate to **Datasets**
2. Show `permission-agent-scenarios`
3. Click into it, show the 4 rows

### Scene 9 — (Optional) Playground (~20 sec)

1. Navigate to **Playgrounds** → `base_playground` (or whichever you have)
2. **Call out**: "Galileo Playground is separate from log streams — Playground runs don't appear in your log stream traces"
3. Quick demo of editing a prompt and running

### Scene 10 — (Optional, ambitious) Galileo Protect mention (~15 sec)

1. If your free tier shows the Protect feature in the navigation, click it
2. Show the screen even if you don't have it active
3. **Voice-over**: "Galileo Protect is the only platform that operates in the request path — real-time guardrails. The other two are post-hoc observability."

### Closing shot (~5 sec)

End on the Insights panel of a trace — the auto-metrics are Galileo's hero visual.

**Total target**: ~3 min 30 sec

---

## After recording — quick QA checklist

Before saving final files, re-watch each recording and confirm:

- [ ] **Clicks are smooth** — no fumbling, no double-click confusion
- [ ] **Mouse stays in frame** (recorder caught the whole window)
- [ ] **No sensitive info** — no API keys, no personal email visible in user menu
- [ ] **Cursor visible** — viewers can track where you're pointing
- [ ] **Resolution** — recording is at least 1080p so it doesn't pixelate on a projector
- [ ] **Length** — roughly 3 min ± 30 sec; if much longer, consider trimming dead air

## Editing tips (if you want polish)

- **Speed up dead time**: any moment > 3 sec of "page loading" or "table rendering" → speed up to 2x. Most editing tools (Loom, ScreenStudio, iMovie) let you select a clip and adjust speed.
- **Zoom into key moments**: when you reach the Insights panel (Galileo) or the Threads view (LangSmith) or the Scores column (Langfuse), a quick zoom highlights the differentiator.
- **Add captions** on hero moments — e.g. "Auto-scored by Galileo, no config" as a text overlay when showing the Insights panel. Helps for muted-playback viewers.

## What goes on the slides

In the deck:
- **Embed the recording** as a video on a slide, autoplay on muted
- OR pull **5-10 second clips** of each scene as GIFs and use as slide content (more compact)
- For the talk: play the relevant recording while you narrate — no static screenshots needed

---

## What this doesn't cover (be honest in the talk)

- We haven't run **dataset experiments** yet — those would be a 4th recording. If you decide to build them later (`notebooks/{platform}/experiment.ipynb`), come back here and add Scene 11 to each recording.
- **Galileo Protect** isn't actually configured in our free-tier setup — you can show the UI but you can't demonstrate it blocking a request. Either explain verbally or skip Scene 10.
- **Volume/streaming/PII** scenarios aren't implemented — don't pretend they are.
