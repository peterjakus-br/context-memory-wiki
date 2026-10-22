---
title: "Actor-Gatherer documentation (docs page)"
type: source
created: 2026-10-22
updated: 2026-10-22
tags: [actor-gatherer, documentation, context-management, harness]
source: raw/2026-10-22-actor-gatherer-docs.html
---
The user and developer documentation page for [[actor-gatherer]], published
next to the blog post ([[actor-gatherer-framework-blog]]) by [[epic-data-lab]].
Converted text: `raw/2026-10-22-actor-gatherer-docs.md`. It describes the
`ag` CLI, configuration, and how to write new policies, pollers and harness
integrations against the code in [[repo-ucbepic-actor-gatherer]].

## Summary
The docs present Actor-Gatherer as a pip-installable package (`actor-gatherer`)
whose `ag` command launches an existing coding harness ([[claude-code]],
[[codex]], [[opencode]], [[pi-coding-agent]]) as an **Actor** connected to a
named **Gatherer** server. "Everything the Gatherer stores is an **event**";
a context-management *policy* turns those events into the context for each
model call. A single policy ships, `proactive_context_manager`, along with one
poller (`file_changes`). Harnesses are integrated either through a hook
(plugin) or through a local proxy that sits between the harness and its model
API. The page is mostly reference material: CLI, `~/.ag/config.toml`, and the
`Policy`, `Poller`, `Adaptor` and `Launcher` extension interfaces.

## Key points
- **Terms.** An Actor is "a harness plus its **adaptor**"; the adaptor "turns
  the harness's messages into events, and the Gatherer's context back into
  messages". `insert` "gives the Gatherer what the Actor has seen and done";
  `get_context` "runs before each model call, and returns the context the
  model gets". Pollers "bring in information from the environment, such as
  files changed under the working directory". A *channel* is "the session an
  event belongs to". Events without a channel (poller events) are "visible from
  every channel".
- **Shipped policy.** The default policy is `ProactiveContextManager`, which
  "searches earlier history in the background, and adds what other sessions
  asked for and what changed in the environment". It is described as "Earlier
  history as sections, built in the background; file-change notices; the
  user's requests to the other channels, shown during a task". Its building
  blocks (`ag/ag_policies/tools/`) are grouping events into turns and tasks,
  segmentation, summarization, a new-task check, ranking, and rendering to a
  token budget. Its LLM splits history into tasks, summarises and ranks them.
  It accepts eight event types: `user_message`, `agent_message`, `tool_call`,
  `tool_output`, `context`, `agent_reasoning` ("never read or counted"),
  `environment_update` and `context_stream`. See
  [[segment-based-context-policy]].
- **Token budgets** (commented `pcm_small` example variant):
  `max_context_tokens = 100000`, `all_task_tokens = 30000`,
  `parallel_index_tokens = 15000`, `keep_temporal_relevant_tokens = 7500`,
  `keep_task_relevant_tokens = 7500`, `keep_previous_task_tokens = 7500`,
  `keep_so_far_tokens = 7500`, `keep_pinned_tokens = 5000`. The budgets
  "must add up to less than its max_context_tokens".
- **Policy contract.** `Policy.read(store, read)` "runs before every model
  call" and returns `Context(items, refs)`. Slow (LLM) work should run in
  background jobs so that `read` stays fast. A gatherer's policy "cannot change
  once it is in use; to try another, start a new gatherer."
- **Gatherer LLM.** The Gatherer's model is set with `ag model provider/model`
  via LiteLLM (examples `openai/gpt-6-sol`, `gemini/gemini-3.8-flash`), or
  with a coding agent as the LLM (`claude-code/sonnet`, `codex/gpt-6-sol`),
  which runs "on that agent's own login" so that "every call counts against
  the subscription's limits". There is no default model: without one "`ag`
  warns at launch and every Gatherer call fails".
- **Harness integrations:**

  | Harness | Integration | Gatherer messages arrive as | Turned off |
  |---|---|---|---|
  | Pi | hook (extension, `-e`) | a hidden custom message | Pi's compaction |
  | OpenCode | hook (plugin via `OPENCODE_CONFIG_CONTENT`) | a synthetic user message | auto-compaction and tool-output pruning |
  | Claude Code | proxy (`ANTHROPIC_BASE_URL`) | system messages, or user-turn reminders | nothing |
  | Codex | proxy (provider `base_url`) | developer messages (or user messages with `AG_CODEX_AG_ROLE=user`) | nothing |

  "Nothing the harness reads on disk is changed". "If the Gatherer fails or
  times out, the harness sends its own messages unchanged."
- **Sharing scope.** Actors started with the same `--gatherer NAME` share one
  Gatherer (for example, `frontend` for Claude Code and Codex, and `backend`
  for another Codex). `ag codex` is the same as
  `ag --gatherer default codex`, and `--gatherer .` creates one gatherer per
  session. State lives in `~/.ag/gatherers/<name>/` (`gatherer.toml`, and
  `context.db`, a SQLite file). This is how [[multi-agent-context-sharing]]
  is set up in practice.
- **Pollers.** The default is `file_changes` (`FileChangePoller`, rooted at
  `{cwd}`). It "reports nothing and starts from now" on first ask. A poller
  that raises "is skipped, and never fails a model call". A commented
  `TicketPoller` example shows custom pollers. See
  [[environment-change-awareness]].

## Chapter guide
- **Overview**: Actor, Gatherer, `insert`/`get_context`, pollers, policy; what
  ships.
- **Install / Set the Gatherer's LLM**: pip or source install, Python 3.11+,
  `ag model`.
- **Quickstart**: `ag --gatherer NAME <harness>`, sharing a gatherer,
  `ag gatherers`.
- **`ag` CLI interface**: options (`--gatherer`, `--policy`, `--poller`,
  `--no-pollers`, `--dry-run`), commands (`model`, `config`, `status`,
  `stop`, `gatherers`, `show`, `new`, `home`), the `~/.ag` home directory.
- **Configuration**: `[policies]`, `[policies.llm]`, `[pollers]`, `[cli]`,
  `[cli.harnesses.<name>]`, `AG_*` environment variables.
- **Extending `ag`**: events, event types and properties; writing a policy
  (incl. the `GathererStore` API); writing a poller; adding a harness (hook-
  vs proxy-based, adaptor, hook, launcher).

## Entities and concepts
- [[actor-gatherer]] — the framework documented
- [[repo-ucbepic-actor-gatherer]] — the code the docs describe
- [[claude-code]], [[codex]], [[opencode]], [[pi-coding-agent]] — supported
  harnesses
- [[segment-based-context-policy]] — the shipped `proactive_context_manager`
- [[proactive-context-management]] — the design principle
- [[context-compaction]] — switched off in Pi and OpenCode while the
  Gatherer answers
- [[multi-agent-context-sharing]], [[environment-change-awareness]] — named
  gatherers and pollers

## Open questions
- The docs never use the word "segment", which is central to the blog's
  description of the policy; they speak of "turns and tasks" and
  "segmentation" as a building block. Whether the code's notion of a task
  boundary is the blog's segment boundary is checked in
  [[repo-ucbepic-actor-gatherer]].
- Model names in examples (`gpt-6-sol`, `gemini-3.8-flash`) differ from the
  models used in the blog's evaluation (gemini-3.1-pro-preview). The docs
  recommend no model for the Gatherer.
- The harness table lists "nothing" turned off for Codex, but the Codex
  launcher in the code switches Codex's automatic compaction off for the run
  (see [[repo-ucbepic-actor-gatherer]]). The docs table is incomplete on this
  point. For Claude Code, compaction does stay on, and `ag` keeps the context
  under Claude Code's auto-compact limit.
