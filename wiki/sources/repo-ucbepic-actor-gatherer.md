---
title: "ucbepic/actor-gatherer (code repository)"
type: source
created: 2026-10-22
updated: 2026-10-22
tags: [repository, actor-gatherer, context-management, harness]
source: raw/repos/2026-10-22-ucbepic-actor-gatherer.md
---
The **official** code for [[actor-gatherer]] by [[epic-data-lab]] (UC
Berkeley), snapshotted at commit `076c26d` (2026-10-21, branch `main`), MIT
licence. The snapshot is partial (177 of 203 files, 1.1 MB). Package
`actor-gatherer` 0.1.0, Python ≥3.11 plus TypeScript. The author listed in
`pyproject.toml` is Sepanta Zeighami. The repo also carries a copy of the blog
(`docs/index.html`, = [[actor-gatherer-framework-blog]]) and the docs source
(`docs/docs.md`, = [[actor-gatherer-docs]], much of it generated from
docstrings at build time). Paths below are relative to
`raw/repos/2026-10-22-ucbepic-actor-gatherer/`.

## Summary
The repository implements the Gatherer as a Python server, reached over stdio
JSON lines and rebuilt statelessly per request. It keeps one SQLite database
per named gatherer, in which everything the Gatherer stores is an event (per the docs). Each of four
coding harnesses is turned into an Actor: [[claude-code]] and [[codex]]
through a local HTTP proxy that rewrites the model request, [[pi-coding-agent]]
and [[opencode]] through in-process TypeScript plugins. One context policy
ships, `ProactiveContextManager`, an implementation of the blog's
[[segment-based-context-policy]]: LLM segmentation of history into tasks,
per-task summaries of what the user "established", a cheap LLM boundary
check, LLM ranking of earlier tasks (including other agents'), and a fixed
section layout from coarse to fine. One poller ships, `FileChangePoller`.
**No evaluation code, datasets or baselines are included**, so the blog's
numbers cannot be reproduced from the repo.

## Key points
- **Interface** (`ag/ag_interface/context_manager.py`): `insert(gatherer,
  event)` (idempotent by event id) and `read(gatherer, row_id, properties)`.
  `read` is the blog's `get_context`. The server adds a combined `rewrite` op
  (insert, then read) (`ag/ag_harness/server/__init__.py`).
- **Store** (`ag/ag_harness/store/schema.py`): SQLite (WAL) with `events`
  (JSON payload, type, tokens, text, `p_channel`/`p_cwd`/`p_poller`
  property columns) and audit tables `_reads`, `_read_items` and
  `_made_items`. Rows are never deleted, so every context sent can be audited.
  Eight event types: `user_message`, `agent_message`, `tool_call`,
  `tool_output`, `context`, `agent_reasoning`, `environment_update`,
  `context_stream`.
- **Request path** (`ag/ag_harness/manager.py`): each `read` first polls
  every poller, then calls the policy, then logs the read. Slow LLM work runs
  in detached background workers (`ag/ag_tools/worker.py`). A read waits up
  to `sync_seconds` = 15 s for a build it started (longer when over the
  limit). On any failure the harness sends its own messages (fail-open).
- **Segmentation** (`ag/ag_policies/tools/segmentation.py`): "A TASK is a run
  of CONSECUTIVE turns that serve one high level objective. A new task starts
  when the user's objective changes." The segmenter sees user text, the last
  agent reply and a tool-call count per turn. Tasks over 6000 tokens are
  subdivided.
- **Summaries** (`tools/summarize.py`): per finished task, the fields
  `object_handling`, `terminology`, `metadata` and `carry_forward`, rendered
  as `handling:`, `term:`, `about:` and `standing:` lines. The prompt stresses
  "MOST TASKS ESTABLISH NOTHING."
- **Boundary check** (`tools/boundary.py`): one cheap LLM call at a user
  message returning `new_task` true/false, biased toward false: "When two
  readings are equally good, answer false." Gating in
  `proactive_context_manager/config.py` and `policy.py`: no build below
  `min_context_tokens` = 15000; a check only after `boundary_cooldown` = 2
  user messages into the open task; a build is also forced when the context
  exceeds `max_context_tokens` = 200000 (scaled to `harness_limit_fraction` =
  0.9 of the harness limit).
- **Ranking** (`tools/ranking.py`): one LLM call ranks earlier tasks, from
  this channel and from parallel channels, against the last turns. It
  prioritises standing instructions: "RANK HIGHEST OF ALL a task whose
  `[carries: ...]` note shows the user gave an instruction meant to APPLY TO
  FUTURE WORK". This is the code's main mechanism against
  [[unknown-unknowns]].
- **Layout and context switch** (`proactive_context_manager/layout.py`,
  `policy.py`): the context is assembled "oldest and least detailed first":
  an index of every earlier user request (verbatim, including requests made
  in parallel sessions), earlier messages (newest first while they fit),
  ranked related tasks, the previous task in full with tool calls, the
  running task condensed if cut, pinned `context` rows, then the running task
  verbatim. Tool output is clipped to 2000 characters (`tools/render.py`).
  Between builds the sections are reused unchanged and only the tail grows
  (append-only within a segment). A ready build is adopted only at a user
  message or when over the limit, and only if it is smaller than the history
  it replaces. The context also tells the agent the SQLite path so it can
  query full history itself (`db_hint`).
- **Lateral awareness**: Actors launched with the same `--gatherer` share a
  database. Each session or thread is a `channel`. User requests made in
  other channels since the last build are injected just before this channel's
  latest user message ("For your context, message from the user in parallel
  to another agent: …"), and other channels' tasks can be ranked in. See
  [[multi-agent-context-sharing]].
- **File changes** (`ag/ag_pollers/file_changes.py`, `policy.notices`): the
  poller scans mtimes under the cwd (cap 500 files) and emits
  `environment_update` events. A notice is shown only if earlier context
  mentions the file, the event is in the same cwd, and the change was not the
  agent's own write (detected by a regex over tool calls). The notice tells
  the agent that what it read "is now out of date" and to read the file
  again. Polling happens at the next model call; nothing is pushed. See
  [[environment-change-awareness]].
- **Harness hooks** (`ag/integrations/harnesses/`):
  - Claude Code: `ANTHROPIC_BASE_URL` points at the proxy, and subagent calls
    are not managed. Claude Code's compaction stays on, and `ag` keeps the
    context below its auto-compact limit. The adaptor re-places
    `cache_control` markers.
  - Codex: `base_url` is overridden with `-c`, and Codex's automatic
    compaction is switched off for the run (`codex/setup/launch.py`).
  - Pi: an extension on Pi's `context` event that cancels compaction.
  - OpenCode: a plugin on `experimental.chat.messages.transform`, with
    compaction and pruning off.
- **Gatherer LLM**: `LiteLLMClient` (any `provider/model`) or `CLIClient`
  (`claude -p` or the Codex SDK). There is no default model.

## Code vs paper
| Blog mechanism | In code |
|---|---|
| Gatherer sets context before every LLM call; shared data layer; `insert`/`get_context`; pollers | implemented (`get_context` is `read`; one poller) |
| Segment-based policy, append-only within segment, context switch at boundary | implemented |
| LLM reasoning over all agents' histories at a switch | partial: the LLM ranks task descriptions and summaries, not raw trajectories; other agents are seen through their user requests and ranked tasks |
| Temporal inductive bias | structural only (newest-first fill, previous task in full); no explicit weighting |
| Varying granularity | implemented (request index → messages-only tasks → full previous task → verbatim tail) |
| KV-cache-friendly ordering (stable early, volatile late) | partial: section reuse between switches, cache-marker restoration; no volatility-based placement; the term "KV cache" does not occur in `ag/` |
| Environment changes | files only |
| Four harness integrations | all four present; Claude Code and Codex use a proxy, not hooks |
| Evaluation (SWE-bench variant, BirdInteract, Spider 2.0) and baselines (Mem0, RLM, CLM, Scroll) | **not in repo** |

## Entities and concepts
- [[actor-gatherer]] — what the code implements
- [[epic-data-lab]] — publisher (`github.com/ucbepic`)
- [[claude-code]], [[codex]], [[pi-coding-agent]], [[opencode]] — integrated
  harnesses
- [[segment-based-context-policy]] — `ProactiveContextManager`
- [[proactive-context-management]] — context built without agent tool calls
- [[unknown-unknowns]] — targeted by standing-instruction summaries and
  ranking
- [[context-compaction]] — switched off or bounded per harness
- [[kv-cache-aware-context-ordering]] — partially realised
- [[multi-agent-context-sharing]], [[environment-change-awareness]],
  [[longitudinal-and-lateral-awareness]] — channels, parallel requests, file
  notices
- [[tool-based-context-management]] — present only as the SQLite
  `db_hint` fallback

## Open questions
- The docs' harness table (`ag/integrations/harnesses/__init__.py`, copied
  into [[actor-gatherer-docs]]) says nothing is turned off for Codex, while
  the Codex launcher switches automatic compaction off. The code is
  internally inconsistent on this.
- The policy is tuned toward standing instructions (handling, terminology,
  carry-forward), which matches the blog's planted-specification
  benchmarks. How it behaves on workloads where the needed context is not an
  instruction is untested here.
- File-change notices are suppressed when the file was never mentioned in
  context. A change to a file the agent needs but has not yet seen is
  therefore not flagged, which is an unknown unknown of its own.
- Gatherer cost: every boundary check, segmentation, summary and ranking is
  an LLM call on the user's provider or subscription. The repo has no
  measurements of this overhead.
- The demos (`demo/cross_session/`, README examples) are illustrations, not
  benchmarks.
