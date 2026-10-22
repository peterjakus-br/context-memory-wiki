<!--
generated: pandoc html -> gfm from 2026-10-22-actor-gatherer-docs.html; figures downloaded to 2026-10-22-actor-gatherer-docs_images/
note: generated companion of the raw HTML, never hand-edited.
-->

☰

[Actor-Gatherer](./)

[Blog](./)[Docs](./docs.html)[GitHub](https://github.com/ucbepic/actor-gatherer)

[Overview](#overview)

[Install](#install)

- [Set the Gatherer's LLM](#set-the-gatherers-llm)

[Quickstart](#quickstart)

[`ag` CLI interface](#cli)

- [Options](#options)
- [Commands](#commands)
- [The home directory](#home)

[Configuration](#configuration)

- [`[policies]`](#policies)
- [`[policies.llm]`](#llm)
- [`[pollers]`](#pollers)
- [`[cli]`](#cli-settings)
- [`[cli.harnesses.<name>]`](#harnesses)
- [Other environment variables](#env)

[Extending `ag`](#extending)

- [Events, event types and properties](#events)
- [Writing a new context policy](#write-policy)
- [Writing a new poller](#write-poller)
- [Adding a new harness](#write-adaptor)

# Documentation

## Overview

Actor-Gatherer is a framework for agent design where agents context is managed proactively and externally using a Gatherer component. `ag` is a cli tool that turns any coding agent (Claude Code, Codex, OpenCode or Pi) into an actor-gatherer agent. The agent performing your tasks is called an Actor, and a **Gatherer** component manages the context of all actors connected to it. The Actors share all their messages with the Gatherer, and before every LLM call, they ask the Gatherer for their context. The Gatherer decides the context the model gets based on the current conversation, plus what matters from earlier history, from other agents, and from the environment.

![Actor-Gatherer architecture: each Actor, a harness plus its adaptor, calls insert and get_context on the Gatherer, which holds the context and insertion policy and a database; pollers watch the environment and insert events.](2026-10-22-actor-gatherer-docs_images/architecture.png)

Each Actor (a harness and its adaptor) sends what it sees and does to the Gatherer, and gets its context back before each model call. Pollers bring in changes from the environment, and the Gatherer's policy decides what context each Actor gets.

The **Gatherer** is a server that many **Actors** talk to, and the Actors can come from different coding harnesses. An Actor is a harness plus its **adaptor**, which turns the harness's messages into events and the Gatherer's context back into messages. Each Actor uses two calls on the Gatherer:

- **`insert`** gives the Gatherer what the Actor has seen and done.
- **`get_context`** runs before each model call, and returns the context the model gets.

**Pollers** bring in information from the environment, such as files changed under the working directory. The Gatherer asks them for new events, and they insert those events like an Actor would. A **context management policy** inside the Gatherer then decides what context each Actor gets, using everything it has gathered from every Actor and from the environment.

`ag` currently uses:

- **Adaptors:** [`ClaudeAdaptor`](https://github.com/ucbepic/actor-gatherer/blob/main/ag/integrations/harnesses/claude/adaptor/adaptor.py), [`CodexAdaptor`](https://github.com/ucbepic/actor-gatherer/blob/main/ag/integrations/harnesses/codex/adaptor/adaptor.py), [`OpencodeAdaptor`](https://github.com/ucbepic/actor-gatherer/blob/main/ag/integrations/harnesses/opencode/adaptor/adaptor.ts) and [`PiAdaptor`](https://github.com/ucbepic/actor-gatherer/blob/main/ag/integrations/harnesses/pi/adaptor/adaptor.ts), each with the launcher `ag` uses to start that harness connected to the Gatherer.
- **Pollers:** [`FileChangePoller`](https://github.com/ucbepic/actor-gatherer/blob/main/ag/ag_pollers/file_changes.py), which reports files changed under the agent's working directory since it last looked.
- **Context Policy:** [`ProactiveContextManager`](https://github.com/ucbepic/actor-gatherer/blob/main/ag/ag_policies/proactive_context_manager/policy.py), which searches earlier history in the background, and adds what other sessions asked for and what changed in the environment.

The framework is extensible. Add a new harness by defining an adaptor for it, new context policies for context management, and pollers that track other information in the environment. See [Extending `ag`](#extending).

## Install

You need Python 3.11+ and the harness you want to run on your `PATH`. Install `ag` from PyPI:

    pip install actor-gatherer

Or from source:

    git clone https://github.com/ucbepic/actor-gatherer && cd actor-gatherer
    pip install -r requirements.txt        # `ag` from this clone, editable, with every dependency

### Set the Gatherer's LLM

The Gatherer uses LLMs to manage the context of Actors, so you must set the model the Gatherer uses. It can be an API-based model, called through [LiteLLM](https://docs.litellm.ai/docs/providers). Name it as `provider/model`, and set that provider's API key, e.g.,

    ag model openai/gpt-6-sol                    # "provider/model"; the key from OPENAI_API_KEY
    export OPENAI_API_KEY=...

    ag model gemini/gemini-3.8-flash             # or a Gemini model; the key from GEMINI_API_KEY
    export GEMINI_API_KEY=...

Or it can be a coding agent, such as Claude Code or Codex, named as

    ag model claude-code/sonnet
    ag model codex/gpt-6-sol

which runs Claude Code or Codex for the Gatherer. To use Codex, make sure OpenAI's Codex SDK is installed:

    pip install openai-codex

To check the model that is set:

    ag model

## Quickstart

Put `ag --gatherer NAME` in front of the agent command you would normally run.

    ag --gatherer demo claude                                # Claude Code
    ag --gatherer demo codex exec "fix the tests"            # Codex
    ag --gatherer demo opencode run "add a --verbose flag"   # OpenCode
    ag --gatherer demo pi                                    # Pi

Agents join the gatherer specified (`demo` above). Agents with the same gatherer share information with each other, whichever harness runs them (see the [example](https://github.com/ucbepic/actor-gatherer#awareness-across-agents)). Agents in different gatherers don't share context and each gatherer keeps its own history.

For example, the first two agents below share information; the third, in a gatherer of its own, sees neither of them:

    ag --gatherer frontend claude                            # shares with the Codex below
    ag --gatherer frontend codex                             # shares with the Claude Code above
    ag --gatherer backend codex                              # shares with neither

Without `--gatherer`, a session joins the gatherer `default`:

    ag codex                                                 # the same as: ag --gatherer default codex

Use `--gatherer .` to create a new, unnamed gatherer. Agents created this way don't share context with other agents:

    ag --gatherer . codex

To see every gatherer:

    ag gatherers                                             # each one's policy, pollers, event count, last activity

Every option and command is in [`ag` CLI interface](#cli).

## `ag` CLI interface

`ag` is the command line that runs a harness with the Gatherer, and manages the gatherers and settings it keeps. Its options go before the harness's name, and everything after the name is passed to the harness unchanged.

### Options

By default every agent you start with `ag`, from any harness, joins one shared gatherer named `default` ([`[cli] gatherer`](#cli-settings)), each session as its own channel.

| flag              | meaning                                                                            |
|-------------------|------------------------------------------------------------------------------------|
| `--gatherer NAME` | Join the named gatherer, created if it does not exist. Overrides `[cli] gatherer`. |
| `--gatherer .`    | Give each session a new gatherer of its own, named after the session.              |
| `--policy P`      | Create the gatherer with policy `P`. Refused if it exists with another policy.     |
| `--poller X`      | Create the gatherer with poller `X` (repeatable).                                  |
| `--no-pollers`    | Create the gatherer with no pollers.                                               |
| `--dry-run`       | Print the command and environment that would run, and run nothing.                 |

A new gatherer takes its policy and pollers from the defaults in `config.toml`, or from `--policy` and `--poller` when given. They are recorded in `~/.ag/gatherers/<name>/gatherer.toml`, where you can change an existing gatherer's pollers, or override its policy's options under `[options]`. A gatherer's policy cannot change once it is in use; to try another, start a new gatherer.

The gatherer is chosen on every model call; it is not stored with the session. To resume a session in a named gatherer, name it again: `ag --gatherer demo codex resume <id>`. Without `--gatherer demo`, the resumed session goes into `default`.

### Commands

| command                                                          | does                                                                |
|------------------------------------------------------------------|---------------------------------------------------------------------|
| `ag <harness> [args]`                                            | Run the harness with the Gatherer.                                  |
| `ag model [NAME] [--api-base URL] [--key-env VAR]`               | Show or set the LLM the Gatherer calls.                             |
| `ag config`                                                      | Show where the settings are, and what each harness resolves to.     |
| `ag status` / `ag stop`                                          | List / stop the proxies `ag` started.                               |
| `ag gatherers`                                                   | List every gatherer: its policy, pollers, events and last activity. |
| `ag show <gatherer>`                                             | Show a gatherer's resolved settings.                                |
| `ag new <gatherer> [--policy P] [--poller X ... | --no-pollers]` | Create a gatherer ahead of use.                                     |
| `ag home list`                                                   | List every available policy and poller, and any problem.            |
| `ag home path`                                                   | Print the home directory.                                           |

### The home directory

Everything `ag` keeps is in one directory, `~/.ag` (set `AG_HOME` to move it). Each gatherer has a directory of its own, with its settings and its database:

    ~/.ag/
    ├── config.toml                     every setting: policies, pollers, the LLM, harnesses
    ├── plugins/                        your own policies and pollers (Python files)
    ├── gatherers/<name>/               one directory per gatherer:
    │   ├── gatherer.toml               its policy, its options and its pollers
    │   └── context.db                  its database (SQLite): every event, and every context it sent
    ├── hook_server/<port>.json         the proxies ag started (Claude Code, Codex)
    └── logs/
        ├── gatherers/<name>/server.log what each model call came to
        ├── gatherers/<name>/worker.log the gatherer's background builds
        ├── <harness>_server.log        each Gatherer server's own output
        ├── hook_servers/<port>.log     each proxy's output
        └── llm/                        one JSON file per LLM call the policies make

A gatherer's database records exactly what the model was sent on every call, so any context can be audited later. `ag gatherers` lists every gatherer, and `ag show <gatherer>` shows one's settings.

## Configuration

Every setting is in `~/.ag/config.toml`, created the first time you run `ag` with every default written out. A command-line option overrides the setting it names (`--gatherer` over `[cli] gatherer`), and so does an `AG_*` environment variable (`AG_LLM_MODEL` over `[policies.llm] model`). The file has these tables:

    [policies]                     # the default policy
    [policies.llm]                 # the LLM the policies call
    [policies.available.<name>]    # the catalog: every policy a gatherer may use

    [pollers]                      # the default pollers
    [pollers.available.<name>]     # the catalog: every poller a gatherer may use

    [cli]                          # the ag command: the default gatherer
    [cli.harnesses.<name>]         # each harness ag can run

`ag config`, `ag home list` and `ag show` show how the settings resolve (see [Commands](#commands)).

### `[policies]`

This is the `[policies]` part of the `config.toml` that `ag` writes on first run. `default` names the policy a new gatherer gets. Below it is the catalog, one `[policies.available.<name>]` entry per policy a gatherer may use: the shipped `proactive_context_manager`, and two commented-out entries to copy, a variant of it with other options (`pcm_small`) and a policy of your own from `~/.ag/plugins/` (`mine`).

    [policies]
    default = "proactive_context_manager"   # the policy a new gatherer gets when none is named

    # ---------------------------------------------------------------- available policies
    # Every policy a gatherer may run.

    # Earlier history as sections, built in the background; file-change notices; the user's
    # requests to the other channels, shown during a task.
    [policies.available.proactive_context_manager]
    class = "ag.ag_policies.proactive_context_manager:ProactiveContextManager"

    # A variant: the same class, other options. Its budgets must add up to less than its
    # max_context_tokens; the rest is headroom before the next build.
    # [policies.available.pcm_small]
    # class = "ag.ag_policies.proactive_context_manager:ProactiveContextManager"
    # [policies.available.pcm_small.options]
    # max_context_tokens = 100000
    # all_task_tokens = 30000
    # parallel_index_tokens = 15000
    # keep_temporal_relevant_tokens = 7500
    # keep_task_relevant_tokens = 7500
    # keep_previous_task_tokens = 7500
    # keep_so_far_tokens = 7500
    # keep_pinned_tokens = 5000

    # Your own: a Policy subclass (or a factory) in plugins/mine.py, built with whichever of
    # format=, llm=, options= it takes.
    # [policies.available.mine]
    # file = "mine.py"
    # class = "MyPolicy"
    # options = {}

Each entry under `[policies.available.<name>]` makes a policy available under that name:

| key       | meaning                                                                                                                     |
|-----------|-----------------------------------------------------------------------------------------------------------------------------|
| `class`   | `"module:Class"` for an importable class; or just `"Class"` together with `file` or `module`. A factory function works too. |
| `file`    | A Python file in `~/.ag/plugins/` that defines `class`.                                                                     |
| `module`  | An importable module that defines `class`.                                                                                  |
| `options` | Options passed to the policy. A gatherer's own `[options]` in its `gatherer.toml` are applied on top of these.              |

Two entries can name the same class with different options; each is a separate policy, and a gatherer picks one by name (`ag --gatherer small --policy pcm_small codex`).

### `[policies.llm]`

The LLM the policy calls (to split history into tasks, summarize them, and rank them). There is no default model; set one here or with [`ag model`](#commands). The model's name decides how it is called:

- **A coding agent**, `claude-code/<model>` or `codex/<model>` (e.g. `claude-code/sonnet`): runs Claude Code (`claude -p`) or Codex for each call, on that agent's own login, with its tools and default instructions out of the way. No API key is needed, and every call counts against the subscription's limits. Codex models need OpenAI's Codex SDK: `pip install openai-codex`; `ag` refuses to run without it.
- **Any other name**, `provider/model` (e.g. `gemini/gemini-3.8-flash`): called through [LiteLLM](https://docs.litellm.ai/docs/providers), with the provider's API key.

    # The LLM the policies call. `model` is a coding agent on its own login,
    # claude-code/<model> or codex/<model>, or any other "provider/model" through LiteLLM,
    # e.g. "gemini/gemini-3.8-flash". `api_base` and `key_env` are for LiteLLM only; without
    # `key_env`, the key is the provider's own variable, e.g. GEMINI_API_KEY.
    [policies.llm]
    model = ""                              # required: no default (AG_LLM_MODEL)
    # api_base = "http://127.0.0.1:4011/v1" # a LiteLLM proxy, or any OpenAI-compatible endpoint (AG_LLM_URL)
    # key_env = "LITELLM_KEY"               # the variable holding the key (AG_LLM_KEY)

| key              | for         | default                 | meaning                                                                                                                                                                             | overridden by                 |
|------------------|-------------|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------|
| `model`          | all         | none                    | The model: claude-code/ or codex/ for a coding agent on its own login, any other "provider/model" through LiteLLM. Without one, `ag` warns at launch and every Gatherer call fails. | `AG_LLM_MODEL`                |
| `api_base`       | LiteLLM     | the provider's          | Send every call to this server instead.                                                                                                                                             | `AG_LLM_URL`                  |
| `key_env`        | LiteLLM     | the provider's variable | The environment variable that holds the API key.                                                                                                                                    | `AG_LLM_KEY` (the key itself) |
| `claude_command` | claude-code | `"claude"`              | The Claude Code executable, found on `PATH`.                                                                                                                                        |                               |
| `codex_command`  | codex       | `"codex"`               | The Codex executable, found on `PATH`.                                                                                                                                              |                               |
| `log_prompts`    | all         | `false`                 | Keep each call's system text and prompt, whole, in `~/.ag/logs/llm/`. Usage, timing and the answer are always logged.                                                               |                               |
| `class`          | your own    | none                    | An LLM implementation of your own, named like a policy's `class` (with `file` or `module` if needed), instead of the two above.                                                     |                               |

The Gatherer's own calls to Claude Code or Codex run without `ag`'s environment, so they never come back through `ag`.

### `[pollers]`

This is the `[pollers]` part of the `config.toml` that `ag` writes on first run. `default` lists the pollers a new gatherer gets. Below it is the catalog, one `[pollers.available.<name>]` entry per poller a gatherer may list: the shipped `file_changes`, and a commented-out entry to copy for a poller of your own from `~/.ag/plugins/` (`tickets`).

    [pollers]
    default = ["file_changes"]              # the pollers a new gatherer gets, whatever its policy

    # ---------------------------------------------------------------- available pollers
    # Every poller a gatherer may list: where its events come from outside the conversation.

    # Files changed under the agent's working directory, as environment_update events.
    [pollers.available.file_changes]
    class = "ag.ag_pollers.file_changes:FileChangePoller"
    args = { root = "{cwd}" }

    # Your own: a Poller in plugins/tickets.py, built with its args.
    # [pollers.available.tickets]
    # file = "tickets.py"
    # class = "TicketPoller"
    # args = { ticket = "4123", cwd = "{cwd}" }

An entry under `[pollers.available.<name>]` takes `class`, `file` and `module` as for policies, and `args`: the arguments the poller is built with. In a string argument, `{cwd}` is the agent's working directory, `{gatherer}` the gatherer's name and `{home}` the `ag` home; `~` is expanded. A poller whose arguments need `{cwd}` is skipped when the request has no working directory.

A gatherer's pollers must output event types its policy accepts; `ag` checks this before each run (see [Events, event types and properties](#events)).

### `[cli]`

    # The gatherer every run files into ("." for one per harness session); `ag --gatherer NAME`
    # (or `--gatherer .`) overrides it for one run.
    [cli]
    gatherer = "default"

`--gatherer` overrides it for one run (see [Options](#options)).

### `[cli.harnesses.<name>]`

`ag` knows a harness only from its entry here, which names its launcher and its adaptor and holds the launcher's settings. `ag <name>` runs it. How each shipped harness is connected is in [The shipped harnesses](#connection-table).

    [cli.harnesses.claude]
    launcher = "ag.integrations.harnesses.claude.setup.launch:ClaudeLauncher"
    adaptor  = "ag.integrations.harnesses.claude.adaptor.adaptor:ClaudeAdaptor"
    command  = ["claude"]       # the Claude Code to run
    upstream = ""               # where its API calls go ("": ANTHROPIC_BASE_URL as set, else Anthropic's)
    port     = 4113             # the first port a hook server tries
    log_dir  = ""               # if set, each request the hook changed, before and after
    trace_root = ""             # if set, every model call there: the request as the model got it, and its answer
    system_messages = ""        # "keep" / "user" for every request ("": chosen by each request's model)
    env      = {}               # extra environment for Claude Code (and nothing else)

| key               | harnesses     | default                          | meaning                                                                         |
|-------------------|---------------|----------------------------------|---------------------------------------------------------------------------------|
| `launcher`        | all           | each harness's own               | the launcher class, "module:Class"                                              |
| `adaptor`         | all           | each harness's own               | the adaptor class: "module:Class", or "path.ts:Export"                          |
| `command`         | all           | each harness's own               | the command that runs the harness                                               |
| `provider`        | codex         | `""`                             | the model provider to hook ("": the one codex would use)                        |
| `port`            | codex, claude | `4013` (codex) / `4113` (claude) | the first port a hook server tries                                              |
| `log_dir`         | codex, claude | `""`                             | if set, each request the hook changed, before and after                         |
| `env`             | all           | `{}`                             | extra environment for this harness only                                         |
| `upstream`        | claude        | `""`                             | where its API calls go ("": ANTHROPIC_BASE_URL as set, else Anthropic's)        |
| `trace_root`      | claude        | `""`                             | if set, every model call there: the request as the model got it, and its answer |
| `system_messages` | claude        | `""`                             | "keep" / "user" for every request ("": chosen by each request's model)          |

Environment variables for one harness, set when you run it:

| variable                 | harness  | default     | meaning                                                                                       |
|--------------------------|----------|-------------|-----------------------------------------------------------------------------------------------|
| `AG_CODEX_AG_ROLE`       | codex    | `developer` | `user`: send the Gatherer's messages to Codex as user messages instead of developer messages. |
| `AG_PI_TIMEOUT_MS`       | pi       | `300000`    | How long a model call waits for the Gatherer.                                                 |
| `AG_PI_COMPACTION`       | pi       | `off`       | `allow`: keep Pi's own compaction on.                                                         |
| `AG_OPENCODE_TIMEOUT_MS` | opencode | `300000`    | How long a model call waits for the Gatherer.                                                 |
| `AG_OPENCODE_COMPACTION` | opencode | `off`       | `allow`: keep OpenCode's own compaction on.                                                   |

### Other environment variables

| variable       | default                    | meaning                                                                                                                 |
|----------------|----------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `AG_HOME`      | `~/.ag`                    | The home directory: settings, gatherers, logs.                                                                          |
| `AG_PYTHON`    | `python3`                  | The Python that runs the Gatherer's server. The Claude Code and Codex proxies default to the Python they run in.        |
| `AG_LLM_MODEL` | `[policies.llm] model`     | The Gatherer's model.                                                                                                   |
| `AG_LLM_URL`   | `[policies.llm] api_base`  | Where the Gatherer's LiteLLM calls go.                                                                                  |
| `AG_LLM_KEY`   | the variable key_env names | The API key for those calls.                                                                                            |
| `AG_GATHERER`  | none                       | The gatherer, for the Pi extension and the OpenCode plugin when run without `ag`. Ignored under `ag`: use `--gatherer`. |
| `AG_ADAPTOR`   | set by ag                  | The adaptor the Pi extension or OpenCode plugin loads, as `"path.ts:Export"`.                                           |

## Extending `ag`

The framework is built to be extended in three places. A **context policy** decides what context each model call gets. A **poller** brings in information from the environment. An **adaptor**, with a launcher, connects a new harness. Each is a class you name in `config.toml`; nothing else in `ag` needs to change. Policies and pollers can live in `~/.ag/plugins/`, or in any importable package.

### Events, event types and properties

Everything the Gatherer stores is an **event**: a user message, the model's answer, a tool call, a tool's output, a file change. An event carries an opaque JSON *payload*, which the Gatherer stores and returns exactly as given, and has an *event type*. It may also carry an *id* (so a re-sent event is stored once), a *text* (what the policy reads of it, without the harness's metadata), and a token cost.

Event types are the contract between the three extension points. A policy declares the types it accepts (`Policy.event_types`); an adaptor and a poller each declare the types they output. `ag` refuses to run when an output is not among the policy's types.

An event type also declares **properties**: named values its events carry beside the payload, each required or not. The store keeps one column per property, refuses an event that lacks a required one or carries one its type does not declare, and filters by them when a policy asks. Three are in use:

- `channel`: the session an event belongs to. The harness side sets it on every event and on every read. An event without a channel (such as a poller's) is visible from every channel.
- `cwd`: the agent's working directory, set from the request, and by the file poller to the directory it watched.
- `poller`: which of the gatherer's pollers an event came from (its name in the catalog).

Adaptors and pollers declare which properties they set, and `ag` also checks those against the policy's event types.

The types `proactive_context_manager` accepts are:

| type                       | events of this type                                                                                                                                                         |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `user_message`             | A request from the user; opens a turn.                                                                                                                                      |
| `agent_message`            | The model's answer.                                                                                                                                                         |
| `tool_call`, `tool_output` | A request to run a tool, and its result.                                                                                                                                    |
| `context`                  | Text the harness puts in front of the model (instructions, injected context, compaction summaries). Kept verbatim.                                                          |
| `agent_reasoning`          | The model's own reasoning: sent back as it was, never read or counted.                                                                                                      |
| `environment_update`       | Something in the environment changed. Payload: `subject` (what changed, named as the agent would name it), `what` (a sentence saying what happened), `timestamp`, `source`. |
| `context_stream`           | A message from a stream the user is part of (a chat channel, a ticket). Payload: `stream`, `author`, `text`, `timestamp`.                                                   |

The first five are the standard types (ag_policies/tools/groups.py). The two outside types are defined here; a poller that makes them defines its own copy, and any poller that returns one feeds this policy. In a gatherer running this policy the eight are ids 1 to 8, in this order (reasoning last, so the others keep their ids).

### Writing a new context policy

A policy is a subclass of `ag.ag_interface.Policy`:

    class Policy(ABC):
        # What the registry and the read log call it
        name: str
        # The event types this policy expects the harness to insert: its side of the contract
        event_types: Tuple[EventType, ...]
        # Create whatever the policy keeps in the gatherer's database beyond the shared tables
        def init(self, store) -> None: ...
        # The context to send in response to `read`, from the gatherer's database
        @abstractmethod
        def read(self, store, read: Read) -> Context: ...
        # Called after the manager stored a whole recorded history at once (`Manager.bulk_load`)
        def bulk_loaded(self, store, gatherer_id: str, properties: Dict[str, Any]) -> Any: ...

A policy imports nothing of the rest of `ag`: everything it works with is handed to it.

**Construction.** The constructor takes whichever of these keyword arguments it names (or all of them, with `**kwargs`):

| argument    | what it is                                                                                                                                                                                                                                                     |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `format`    | Makes the policy's own messages: `format.make_section(text, name)` returns an `ag` message, `{"type": "ag", "name", "text"}`, which each harness shows its own way.                                                                                            |
| `llm`       | The LLM client set in `[policies.llm]`; its model is `llm.model`.                                                                                                                                                                                              |
| `options`   | A dict: the catalog entry's `options`, then the gatherer's `[options]`.                                                                                                                                                                                        |
| `tokenizer` | Counts tokens: `tokenizer.count(text)`. Also set as `self.tokenizer` when not taken.                                                                                                                                                                           |
| `jobs`      | Starts background work: `jobs.start(gatherer, properties, "build", job_id)` calls `policy.build(gatherer, properties, job_id)` in a worker process, with the same policy built from the home. The job opens the gatherer with `self.gatherers.open(gatherer)`. |

**Reading.** `read(store, read)` is called before every model call. `read.properties` holds the call's `channel` and `cwd`, and `read.row_id` the event it responds to (normally the last one the harness sent). It returns a `Context`: the items to send, in order (stored payloads, and `ag` messages), with a `Ref` for each saying where it came from, for the read log. The `store` is the gatherer's database (`GathererStore`, in store.py), and answers the SQLite connection's own methods (`execute`, `commit`) for tables the policy creates in `init`.

**A sketch.** A policy that sends the channel's whole conversation and, before the latest request, the user's latest requests to other agents in the same gatherer:

    # ~/.ag/plugins/other_requests.py
    from ag.ag_interface import Context, Policy, Ref, TypeIds, event_text
    from ag.ag_policies.proactive_context_manager.events import EVENT_TYPES

    CONVERSATION = ("user_message", "agent_message", "tool_call", "tool_output", "context", "agent_reasoning")


    class OtherRequests(Policy):
        name = "other_requests"
        event_types = EVENT_TYPES            # the same types the shipped adaptors and pollers use

        def __init__(self, format, options=None):
            self.format = format
            self.show = int((options or {}).get("show", 5))

        def read(self, store, read):
            channel = read.properties.get("channel")
            types = TypeIds.load(store)
            mine = store.rows(type_ids=types.of(*CONVERSATION), match={"channel": channel})
            items = [r.payload for r in mine]
            refs = [Ref(row_id=r.row_id) for r in mine]

            requests = types.of("user_message")
            latest = max((i for i, r in enumerate(mine) if r.type.id in requests), default=None)
            others = store.rows(type_ids=requests, differ={"channel": channel})[-self.show:]
            if others and latest is not None:
                text = "Meanwhile, the user asked other agents:\n" + "\n".join(f"- {event_text(r)}" for r in others)
                note = self.format.make_section(text, "other_requests")
                made = store.make_item(note, self.tokenizer, properties={"channel": channel}, name="other_requests")
                items.insert(latest, note)                       # just before the latest request
                refs.insert(latest, Ref(made_id=made))
            return Context(items, refs)

Registered in config.toml, and used by a gatherer:

    [policies.available.other_requests]
    file = "other_requests.py"
    class = "OtherRequests"
    options = { show = 3 }

    ag --gatherer team --policy other_requests codex

**Keep in mind.**

- Return payloads exactly as stored: the adaptor turns them back into the harness's messages. Keep a tool call with its output, since most model APIs reject one without the other.
- A policy accepts only the event types it declares. To take a new kind of event (say, test results), add its type to `event_types` and have a poller output it; no other policy is affected.
- `read` runs before every model call, so keep it fast. Put LLM calls and other slow work in a background job (`jobs.start`), and use its result on a later read.
- The policies' building blocks are in `ag/ag_policies/tools/`: grouping events into turns and tasks, segmentation, summarization, the new-task check, ranking, and rendering to a token budget. A new policy can compose them.

A working policy: `ProactiveContextManager`, in `ag/ag_policies/proactive_context_manager/`.

#### The store

What `read` and `init` get as `store`, beside the SQLite connection's own methods:

    class GathererStore(ABC):
        # The events after `after_row` whose properties pass `match` and `differ` (module doc), of
        # `type_ids` if given, in order
        @abstractmethod
        def rows(self, after_row: int=0, type_ids: Optional[Iterable[int]]=None, *, match: Optional[Dict[str, Any]]=None, differ: Optional[Dict[str, Any]]=None, unset_matches: bool=True) -> List[Row]: ...
        # The gatherer's event types, with their ids
        @abstractmethod
        def event_types(self) -> List[EventType]: ...
        # Store an item the policy made for the model, with the properties of the read it is for;
        # its made id
        @abstractmethod
        def make_item(self, item: Any, tokenizer: Tokenizer, *, properties: Optional[Dict[str, Any]]=None, name: Optional[str]=None, source: Optional[str]=None) -> int: ...
        # made id -> (the item, its name, its tokens, ...) for `made_ids`
        @abstractmethod
        def made_items(self, made_ids) -> dict: ...
        # The last read with these properties (each given one its value, None: unset; those not
        # given: any), as the read log has it, or None
        @abstractmethod
        def last_read(self, properties: Optional[Dict[str, Any]]=None) -> Optional[dict]: ...
        # The highest row id stored
        @abstractmethod
        def high_water(self) -> int: ...

### Writing a new poller

A poller is a subclass of `ag.ag_interface.Poller`:

    class Poller(ABC):
        # Identifies the source: the manager keeps one "last asked" mark per name
        name: str
        # Which poller of the gatherer's it is, given by whoever builds it (the home: its catalog
        # name, `file_changes`); "" = not given, its `name` stands in
        id: str
        # The names of the event types it outputs (e.g. "environment_update"), and nothing else
        outputs: tuple
        # The names of the event properties it sets on its events (e.g. its id, as "poller"), and
        # nothing else: an event carrying another is dropped, and ag refuses to run a policy whose
        # types for `outputs` do not declare them all
        properties: tuple
        # The events that occurred after `since`, oldest first
        @abstractmethod
        def poll(self, since: Optional[float], types: List[EventType]) -> List[Event]: ...

Before every model call, the Gatherer asks each of the gatherer's pollers for what happened since it last asked, stores what they return, and only then lets the policy build the context.

- `since` is when this poller was last asked for this gatherer, in seconds since the epoch; `None` the first time. The poller decides what `None` means: the file poller reports nothing and starts from now, while a poller reading a log might return its backlog.
- `types` are the gatherer's event types with their ids. Return events typed by those ids (`Event(type_id, payload, id=..., properties=..., text=...)`), and nothing if the gatherer lacks your type.
- Give each event an `id` that is the same if the same occurrence is seen again: duplicates are stored once.
- Return `environment_update` or `context_stream` events when they fit, so that existing policies already know how to show them. An event of a type not in `outputs`, or with a property not in `properties`, is dropped. A poller that raises is skipped, and never fails a model call.
- A poller's events belong to no channel: every session in the gatherer sees them.

**A sketch.** A poller that turns messages appended to a JSON-lines file (say, exported from a team chat) into `context_stream` events, which `proactive_context_manager` shows to the agent where they arrived:

    # ~/.ag/plugins/chat_log.py
    import json
    import os

    from ag.ag_interface import Event, Poller


    class ChatLogPoller(Poller):
        outputs = ("context_stream",)        # one {"author", "text", "ts"} per line
        properties = ("poller",)

        def __init__(self, path, stream="#team"):
            self.path, self.stream = os.path.expanduser(path), stream
            self.name = f"chat_log:{self.path}"

        def poll(self, since, types):
            type_id = next((t.id for t in types if t.name == "context_stream"), None)
            if type_id is None or not os.path.exists(self.path):
                return []
            events = []
            with open(self.path) as fh:
                for line in fh:
                    m = json.loads(line)
                    if since is not None and m["ts"] <= since:
                        continue
                    events.append(Event(
                        type_id,
                        {"stream": self.stream, "author": m["author"], "text": m["text"], "timestamp": m["ts"]},
                        id=f"context_stream:{self.stream}:{m['ts']}",
                        properties={"poller": self.id or self.name},
                        text=f"{m['author']} in {self.stream}: {m['text']}"))
            return events

Registered in config.toml, and added to a gatherer (or to `[pollers] default`):

    [pollers.available.team_chat]
    file = "chat_log.py"
    class = "ChatLogPoller"
    args = { path = "~/team-chat.jsonl", stream = "#team" }

    ag --gatherer team --poller file_changes --poller team_chat claude

An existing gatherer's pollers can be changed at any time by editing `pollers` in its `gatherer.toml`.

A working poller: `FileChangePoller`, in `ag/ag_pollers/file_changes.py`.

### Adding a new harness

Connecting a new harness takes three pieces:

- An **adaptor** turns the harness's messages into events, and the context back into messages.
- A **hook** in the harness calls the Gatherer before each model call.
- A **launcher** starts the harness with that hook in place, for one run.

The hook is the harness's own, if it has one; otherwise a proxy stands in for it. Nothing the harness reads on disk is changed: each change (an environment variable, a flag, a local proxy) applies to that one run, and the same command without `ag` behaves as it always did. If the Gatherer fails or times out, the harness sends its own messages unchanged.

#### Hook-based harnesses

A harness with a plugin system that can change the messages before each model call is connected through a **hook**: a plugin that `ag` loads into the harness. Pi (an extension) and OpenCode (a plugin) are connected this way.

- The launcher loads the plugin for this run only: a command-line flag for Pi, and the configuration passed in the environment for OpenCode.
- Before every model call, the harness calls the plugin's hook with the messages. The plugin runs the adaptor, sends the events to the Gatherer, and gives the harness back the context to send instead.
- The gatherer is passed to the plugin as an option, and the channel is the harness's session.
- The harness's own compaction is turned off while the Gatherer answers, since the Gatherer now decides what the context holds. Set `AG_PI_COMPACTION=allow` or `AG_OPENCODE_COMPACTION=allow` to keep it on.

#### Proxy-based harnesses

A harness without such a hook is connected through a **proxy**: a local server that sits between the harness and its model's API, and changes each model call on its way there. This works for any harness that calls its model over HTTP and lets you change where those calls go. Claude Code and Codex are connected this way.

- The launcher points the harness's API base URL at the proxy, for this run only. The proxy relays to wherever the harness pointed before (the *upstream*).
- On every request that is a model call, the proxy runs the adaptor on the request's messages, sends the events to the Gatherer, and forwards the request with the context in place of the messages. Every other request passes through untouched, and the answer streams back unchanged.
- The gatherer is passed in the URL path, `/h/<gatherer>/`, and the channel is the harness's session (a Claude Code session, a Codex thread), read from the request.
- Proxies run detached: the first run with a given upstream starts one, and later runs and other sessions reuse it. `ag status` lists them and `ag stop` stops them.

#### The shipped harnesses

| harness     | type  | what the launcher does                                                                                        | gatherer                       | channel     | the Gatherer's own messages arrive as                       | turned off                              |
|-------------|-------|---------------------------------------------------------------------------------------------------------------|--------------------------------|-------------|-------------------------------------------------------------|-----------------------------------------|
| Pi          | hook  | Loads the extension with `-e`, unless Pi already has the package installed.                                   | `--ag-gatherer NAME`           | the session | a hidden custom message                                     | Pi's compaction                         |
| OpenCode    | hook  | Adds the plugin through `OPENCODE_CONFIG_CONTENT`.                                                            | the plugin's `gatherer` option | the session | a synthetic user message                                    | auto-compaction and tool-output pruning |
| Claude Code | proxy | Starts a proxy if none is running for the upstream, and points `ANTHROPIC_BASE_URL` at it.                    | URL path `/h/<gatherer>/`      | the session | system messages, or user-turn reminders (`system_messages`) | nothing                                 |
| Codex       | proxy | Starts a proxy if none is running for the upstream, and points the active provider's `base_url` at it (`-c`). | URL path `/h/<gatherer>/`      | the thread  | developer messages (`AG_CODEX_AG_ROLE=user`: user messages) | nothing                                 |

#### The adaptor

An adaptor is a Python subclass of `Adaptor`, or a TypeScript class implementing `Adaptor<M>` (adaptor.ts) with the same declarations as static fields (`adaptorName`, `outputs`, `accepts`, `properties`).

- `to_events` returns one dict per event: `type` (one of `outputs`), `id`, `payload`, and optionally `text` and `tokens`.
  - **`id`:** the harness re-sends its whole conversation on every call, so give each message a stable id. Use the harness's own id, or a hash of the message, so that a message is stored once.
  - **Splitting:** one event per unit the policy should see. If an assistant message holds both text and tool calls, split it, as the Pi adaptor does.
  - **`text`:** what the policy should read: the words, a tool call's name and arguments, a tool's output, without ids and metadata.
  - **`tokens`:** set it to 0 for opaque content such as encrypted reasoning.
- `to_messages` gets back events in the order the model should see them, and must rebuild valid messages for the harness's API. It also shows the policy's `ag` messages, as a developer, system or user message.
- The declarations are checked. `ag` refuses to run a policy that does not accept every type in `outputs`, or every property in `properties`. An event of an undeclared type makes the hook send the harness's own messages unchanged, and a context entry not in `accepts` is noted.

**A sketch** (`TYPES`, `kind_of`, `text_of` and `as_system_message` stand for the harness's own: the event type names it emits, and its logic):

    from ag.integrations.tools.ag_orchestrator.adaptor import AG, CHANNEL, CWD, Adaptor


    class MyAdaptor(Adaptor):
        name = "mine"
        outputs = TYPES                        # the event type names to_events emits
        accepts = outputs + (AG,)              # what to_messages can show: event types, and ag messages
        properties = (CHANNEL, CWD)            # the properties the hook sets

        def to_events(self, messages):
            return [{"type": kind_of(m), "id": m["id"], "payload": m, "text": text_of(m)} for m in messages]

        def to_messages(self, context, messages):
            return [as_system_message(e["text"]) if e["type"] == AG else e["payload"] for e in context]

Working adaptors: `ClaudeAdaptor` (ag/integrations/harnesses/claude/adaptor/), the smallest Python one, and `PiAdaptor` and `OpencodeAdaptor` in TypeScript.

#### The hook

The hook works out where the call belongs: the gatherer, the channel (the harness's session id) and the working directory. It then runs one call through `call_ag`, which never raises:

    from ag.integrations.tools.ag_connection.ag_client import AgClient
    from ag.integrations.tools.ag_orchestrator.adaptor import CHANNEL
    from ag.integrations.tools.ag_orchestrator.call_ag import call_ag

    client = AgClient("mine")                  # starts the Gatherer's server on first use
    messages, note = await call_ag(client, gatherer, {CHANNEL: session_id}, cwd, harness_messages, MyAdaptor())
    send(messages if messages is not None else harness_messages)   # None: the Gatherer could not answer

`call_ag` runs `to_events`, sends the events to the Gatherer, and runs `to_messages` on the context it returns. In TypeScript, `call_ag(server, {gatherer, properties, cwd}, messages, adaptor)` does the same. It holds the adaptor to what it declares: an event of a type not in its `outputs`, or a property not in its `properties`, sends nothing (None), and a context entry not in its `accepts` is noted. The working directory, when given, goes on the events and the read as the property CWD too. An adaptor that fails, a server that errors or does not answer, or a context that is not a list each give None and a note.

For a proxy-based harness, ag/integrations/tools/hook_server/hook_server.py is the proxy: it calls a given hook on every request to the model's endpoint, and relays everything else unchanged. A URL that starts with `/h/<label>/` hands the hook that label, which the shipped hooks use as the gatherer.

#### The launcher

`ag` calls `launch` with a `Run`: the harness's arguments, its command, the environment, the gatherer (`None` for one per session), the working directory, whether this is a dry run, and the adaptor named in the entry. `launch` returns the command and environment to run. A launcher may also implement `describe` (for `ag config`), and `status` and `stop` (for anything it keeps running, such as a proxy). It changes nothing the harness reads on disk: everything is passed for this run only, through flags or the environment.

**A sketch**, for a harness that loads a plugin given by a flag:

    from ag.cli.launch import Launch, Launcher


    class MyLauncher(Launcher):
        defaults = {"command": ["mine"], "env": {}}

        def launch(self, run):
            env = {**run.env, "AG_ADAPTOR": run.adaptor}          # the plugin loads the adaptor ag checked
            flags = ["--plugin", "/path/to/my_plugin"] + (["--ag-gatherer", run.gatherer] if run.gatherer else [])
            return Launch([*run.command, *flags, *run.args], env)

**Registering the harness** in config.toml:

    [cli.harnesses.mine]
    launcher = "my_pkg.launch:MyLauncher"
    adaptor  = "my_pkg.adaptor:MyAdaptor"        # or "path/to/adaptor.ts:MyAdaptor"
    command  = ["mine"]

Then `ag mine` runs it. Before every run, `ag` checks that the gatherer's policy accepts what the adaptor and the pollers output, and `ag --dry-run mine` shows the command it would run. A harness cannot be named after one of `ag`'s own commands.

Working launchers: each shipped harness's, in `ag/integrations/harnesses/<name>/setup/launch.py`.

Developed at the [EPIC Data Lab](https://epic.berkeley.edu/), UC Berkeley · [GitHub](https://github.com/ucbepic/actor-gatherer) · 2026
