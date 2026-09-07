<div align="center" markdown="1">

<img src="https://raw.githubusercontent.com/CoronRing/gs_prompt_manager/main/docs/assets/banner.svg" alt="gs_prompt_manager — one home for every prompt in your LLM app: found on disk, grouped by variant, rendered on call" width="820">

<h1>gs_prompt_manager</h1>

<p><strong>One home for every prompt in your LLM app.</strong><br>
Write prompts as plain Python classes. Point the manager at the folder. Call them by name.</p>

[![PyPI version](https://img.shields.io/pypi/v/gs-prompt-manager?color=ea580c&label=pypi)](https://pypi.org/project/gs-prompt-manager/)
[![Python versions](https://img.shields.io/pypi/pyversions/gs-prompt-manager?color=b45309)](https://pypi.org/project/gs-prompt-manager/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-92400e)](https://github.com/CoronRing/gs_prompt_manager/blob/main/LICENSE)
[![Tests](https://github.com/CoronRing/gs_prompt_manager/actions/workflows/tests.yml/badge.svg)](https://github.com/CoronRing/gs_prompt_manager/actions/workflows/tests.yml)
[![Docs](https://img.shields.io/readthedocs/gs-prompt-manager?color=a16207)](https://gs-prompt-manager.readthedocs.io/)
[![Downloads](https://img.shields.io/pypi/dm/gs-prompt-manager?color=a8a29e)](https://pypi.org/project/gs-prompt-manager/)

[Install](#install) · [60-second tour](#60-second-tour) · [How it works](#how-it-works) · [Prompt groups](#prompt-groups) · [Recipes](#recipes) · [API](#api-at-a-glance) · [FAQ](#faq) · [Docs](https://gs-prompt-manager.readthedocs.io/)

</div>

---

Prompts start as one f-string in a handler. Then there is a system variant, and a
terse variant for the cheap model, and a French one, and a copy someone pasted into
a notebook. By the time it matters, nobody can say which string production actually
sends.

**gs_prompt_manager** gives prompts a place to live. Each one is a small class with
its template and its metadata; a directory of them becomes a namespace you can
autocomplete. `PromptManager("./prompts")` walks the folder, imports what it finds,
instantiates every `PromptBase` subclass, and files related variants together — so
`m.Reviewer.system({"language": "Rust"})` is the whole call site.

No registry file to keep in sync, no YAML, no framework. It renders strings, and
strings work with every model provider.

<div align="center" markdown="1">
<img src="https://raw.githubusercontent.com/CoronRing/gs_prompt_manager/main/docs/assets/demo.svg" alt="Terminal recording: installing gs-prompt-manager, then a Python session where PromptManager discovers the Reviewer group and renders its system and verdict prompts" width="760">
</div>

## Why not just f-strings

| | f-strings in the handler | `gs_prompt_manager` |
|---|---|---|
| Where a prompt lives | wherever it was first needed | one directory, one class each |
| Finding every variant | grep and hope | `m.get_prompt_group_names()` |
| A variable you forgot | renders `{name}` into the API call | raises before the call is made |
| Defaults | a chain of `or ""` | `set_variable_defaults` |
| Values the caller cannot know (dates, hostnames) | threaded down through every layer | `<<MACRO>>`, filled by the prompt itself |
| Version, author, tags, examples | a comment, if you are lucky | `get_metadata()` |
| Adding a variant | new function, new import, new call site | new class, nothing else |

## Install

```bash
pip install gs-prompt-manager
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add gs-prompt-manager
```

Python 3.8+. The only dependency is `regex`.

## 60-second tour

**1. Write your prompts as classes** — `prompts/reviewer.py`:

```python
from gs_prompt_manager import PromptBase, prompt_group


class ReviewerSystem(PromptBase):
    """System prompt for the code reviewer."""

    def set_prompt(self):
        return (
            "You are a senior {language} reviewer.\n"
            "Focus on correctness first, style last.\n"
            "Session started <<DATETIME>>."
        )

    def set_variable_defaults(self):
        self.variable_defaults = {"language": "Python"}


class ReviewerChat(PromptBase):
    def set_prompt(self):
        return "Review this diff:\n\n{diff}"


@prompt_group("Reviewer", "verdict")
class ReviewerFinalCall(PromptBase):
    def set_prompt(self):
        return "Answer with exactly one word: {options}."

    def set_variable_defaults(self):
        self.variable_defaults = {"options": "approve or reject"}
```

Three classes, one group. `ReviewerSystem` and `ReviewerChat` are filed under
`Reviewer` by their name suffix; `ReviewerFinalCall` says where it belongs
explicitly.

**2. Point the manager at the folder:**

```python
from gs_prompt_manager import PromptManager

m = PromptManager("./prompts")
```

**3. Call them:**

```python
>>> m.get_prompt_group_names()
['Reviewer']
>>> m.Reviewer.get_prompt_names()
['chat', 'verdict', 'system']

>>> print(m.Reviewer.system({"language": "Rust"}))
You are a senior Rust reviewer.
Focus on correctness first, style last.
Session started 2026-09-07 01:13:24.

>>> print(m.Reviewer.verdict())
Answer with exactly one word: approve or reject.
```

`{language}` came from the caller, `{options}` from the class default, and
`<<DATETIME>>` from the prompt itself. Leave out a variable that has no default and
you get a `ValueError` naming it — before a token is spent.

All of the above is in [`examples/`](https://github.com/CoronRing/gs_prompt_manager/tree/main/examples);
clone the repo and run `python examples/quickstart.py` to watch it happen.

## How it works

<div align="center" markdown="1">
<img src="https://raw.githubusercontent.com/CoronRing/gs_prompt_manager/main/docs/assets/how-it-works.svg" alt="Diagram: prompt classes in your files are discovered by PromptManager, which instantiates them and resolves them into named groups keyed by variant" width="1000">
</div>

Discovery is a directory walk, so the folder layout is yours to choose — nest by
feature, by agent, by language, however you like. A prompt that fails to import or
fails validation is logged and skipped; one broken template does not take the rest
of your app down with it.

Pass a list to load several trees at once:

```python
m = PromptManager(["./prompts", "./vendor_prompts"], verbose=True)
```

Pass nothing and it searches the directory of the file that constructed it.

## Prompt groups

A group is one logical prompt and all its variants, addressed by key. Membership is
resolved three ways, in priority order:

**1. The `@prompt_group` decorator** — explicit, wins over everything:

```python
@prompt_group("Assistant")            # key derived from the class name -> "formal"
class AssistantFormal(PromptBase): ...

@prompt_group("Assistant", "polite")  # key stated outright -> "polite"
class SomeOtherName(PromptBase): ...
```

**2. A recognized class-name suffix** — `system`, `chat`, `pre`, `post`, `message`,
`prompt` (case-insensitive, optional underscore):

```python
class TranslatorSystem(PromptBase): ...   # group "Translator", key "system"
class Translator_chat(PromptBase): ...    # group "Translator", key "chat"
```

**3. Anything else** becomes a solo group named after the class, key `"default"`.

Groups read three ways, so use whichever suits the call site:

```python
group = m.get_prompt_group("Reviewer")   # explicit
group = m.Reviewer                       # attribute

group.system({"language": "Go"})         # attribute access
group["system"]({"language": "Go"})      # dict access
group.get_prompt("system")               # explicit

"system" in group                        # True
len(group)                               # 3
list(group)                              # ['chat', 'verdict', 'system']
str(group)                               # renders default -> chat -> first member
```

Two prompts claiming the same key is a warning, not a crash: the first one keeps the
key, and the collision is logged with both class names.

## Variables and macros

Two substitutions, deliberately different, because they have different owners.

| | Syntax | Filled by | If it is missing |
|---|---|---|---|
| **Variable** | `{name}` | the caller, or `variable_defaults` | `ValueError` |
| **Macro** | `<<NAME>>` | the prompt class, via `set_macros` | warning, left as-is |

```python
class AuditSystem(PromptBase):
    def set_prompt(self):
        return "Audit for {user_id}. Generated <<DATETIME>> by <<HOST>>."

    def set_macros(self):
        import socket, datetime
        self.macros = {
            "<<DATETIME>>": datetime.datetime.now().isoformat(),
            "<<HOST>>": socket.gethostname(),
        }
```

Variables are auto-extracted from the template, so you rarely write `set_variables`
yourself. Need a literal brace in the output — JSON in a few-shot example, say?
Escape it:

```python
def set_prompt(self):
    # {score} is a variable; the escaped braces are literal text
    return r'Reply as JSON: \{"score": {score}\}'
```

Use a raw string (or double the backslash) so Python itself leaves `\{` alone —
on 3.12+ a bare `'\{'` is a `SyntaxWarning`.

Defaults are validated against the template at import time: a default for a variable
the prompt does not have raises immediately, rather than silently doing nothing.

## Recipes

**Anthropic** — the group maps straight onto the request:

```python
import anthropic
from gs_prompt_manager import PromptManager

m = PromptManager("./prompts")
client = anthropic.Anthropic()

reviewer = m.Reviewer
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    system=reviewer.system({"language": "Python"}),
    messages=[{"role": "user", "content": reviewer.chat({"diff": diff})}],
)
```

**OpenAI:**

```python
messages = [
    {"role": "system", "content": m.Reviewer.system({"language": "TypeScript"})},
    {"role": "user", "content": m.Reviewer.chat({"diff": diff})},
]
```

**One group per agent, in a multi-agent system** — hand each agent its group, not a
string, and every variant travels with it:

```python
class Agent:
    def __init__(self, group):
        self.group = group

    def system_prompt(self):
        return self.group.system()

planner = Agent(m.Planner)
critic = Agent(m.Critic)
```

**Ship a prompt catalogue** — every prompt carries its own metadata, so a browsable
index is one comprehension:

```python
catalogue = {
    name: prompt.get_metadata()
    for name, prompt in m.get_prompt_instances().items()
}
```

## Works well with

- **[Emalia](https://github.com/CoronRing/GS-Emalia)** — an AI agent that lives in
  your email, plus the typed IMAP/SMTP toolkit behind it. Emalia ships its own
  prompts; once you start customising them, a prompt directory beats editing strings
  in place.
- **Anything that takes a string.** Provider-agnostic on purpose: no SDK dependency,
  no client wrapper, no opinion about how you call your model.

## API at a glance

**`PromptBase`** — subclass it, implement `set_prompt`, override whatever else you
need.

| Member | What it does |
|---|---|
| `set_prompt()` | return the template string. The one required override |
| `set_name()` | defaults to the class name |
| `set_variables()` | defaults to auto-extracting `{...}` from the template |
| `set_variable_defaults()` | per-variable fallbacks |
| `set_variable_defaults_empty()` | fall back to `""` for anything still unset |
| `set_macros()` | `<<NAME>>` substitutions the class computes itself |
| `set_tools()` | tool identifiers this prompt expects |
| `add_variable_default(name, value)` / `add_macro(key, value)` | tweak one entry at runtime |
| `get_prompt(variables)` / `prompt(variables)` | render. Instances are callable |
| `get_metadata()` | JSON-serializable dict: template, name, version, tags, author, example, tools |

**`PromptManager`** — discovery and lookup.

| Member | What it does |
|---|---|
| `PromptManager(prompt_paths=None, verbose=False)` | a `str`, a list of `str`, or `None` for the caller's directory |
| `get_prompt(name)` / `manager.Name` | one prompt instance, by class name |
| `get_prompt_group(name)` / `manager.Group` | one group. Groups win on name collisions |
| `get_prompt_names()` / `get_prompt_group_names()` | what got discovered |
| `get_prompt_instances()` / `get_prompt_groups()` | everything, as dicts |
| `search_available_prompts(path)` | the discovery step on its own, as a static method |
| `dir(manager)` | includes group and prompt names, so tab-completion works |

**`PromptGroup`** — `group.key`, `group["key"]`, `group.get_prompt("key")`,
`get_prompt_names()`, `get_prompts()`, plus `in`, `len()`, iteration and `str()`.

## FAQ

**Does it call a model?** No. It renders strings. Bring your own client.

**Do prompts have to live in files?** That is what the manager is for, but
`PromptBase` works standalone — instantiate a subclass, or pass `prompt=...` to the
constructor directly, and skip discovery entirely.

**What happens to a prompt that raises on import?** It is logged with a traceback
and skipped. Everything else still loads. Construct with `verbose=True` to see the
counts.

**Can two prompts share a name?** Class names must be unique across all discovered
paths — a duplicate raises. Group *keys* only need to be unique within their group.

**Is discovery slow?** It imports every `.py` file under the given paths, once, at
construction. Build the manager at startup and hold onto it; do not rebuild it per
request.

**Does it cope with `{}` in JSON examples?** Yes — escape them as `\{` and `\}`.
Escaped braces are excluded from variable extraction and render as literal braces.

## Documentation

Full docs at **[gs-prompt-manager.readthedocs.io](https://gs-prompt-manager.readthedocs.io/)**.

- **[User Guide](https://gs-prompt-manager.readthedocs.io/en/latest/user-guide/)** — concepts, configuration, patterns
- **[Examples](https://gs-prompt-manager.readthedocs.io/en/latest/examples/)** — OpenAI, Claude, multi-agent systems
- **[Tutorial notebook](https://github.com/CoronRing/gs_prompt_manager/blob/main/docs/tutorial.ipynb)** — run it end to end
- **[Migration guide](https://gs-prompt-manager.readthedocs.io/en/latest/migration/)** — upgrading from earlier versions
- **[Changelog](https://github.com/CoronRing/gs_prompt_manager/blob/main/CHANGELOG.md)** · **[Contributing](https://github.com/CoronRing/gs_prompt_manager/blob/main/CONTRIBUTING.md)**

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](https://github.com/CoronRing/gs_prompt_manager/blob/main/CONTRIBUTING.md).

## License

Apache License 2.0. See [LICENSE](https://github.com/CoronRing/gs_prompt_manager/blob/main/LICENSE).

<div align="center" markdown="1">
<br>
<sub>Built by <strong>Guan Huang</strong> ·
<a href="https://github.com/CoronRing/gs_prompt_manager">GitHub</a> ·
<a href="https://pypi.org/project/gs-prompt-manager/">PyPI</a> ·
<a href="https://github.com/CoronRing/gs_prompt_manager/issues">Issues</a></sub>
</div>
