# gs_prompt_manager

[![PyPI version](https://badge.fury.io/py/gs-prompt-manager.svg)](https://badge.fury.io/py/gs-prompt-manager)
[![Python Support](https://img.shields.io/pypi/pyversions/gs-prompt-manager.svg)](https://pypi.org/project/gs-prompt-manager/)
[![Documentation](https://readthedocs.org/projects/gs-prompt-manager/badge/?version=latest)](https://gs-prompt-manager.readthedocs.io/en/latest/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://github.com/CoronRing/gs_prompt_manager/workflows/Tests/badge.svg)](https://github.com/CoronRing/gs_prompt_manager/actions)

A lightweight Python package for managing and organizing prompt templates. Automatically discovers, loads, and groups prompt classes that inherit from `PromptBase`.

## Features

- **Auto-discovery**: finds and loads prompt classes from specified directories
- **Template management**: define reusable prompt templates with `{variable}` and `<<MACRO>>` substitution
- **Prompt groups**: bundle related variants (system / chat / pre / post / message) under one named group with auto-detection or an explicit `@prompt_group` decorator
- **Attribute access**: `manager.Assistant` returns the group directly — no boilerplate lookup required
- **Validation**: built-in checks for variables, metadata, and required fields
- **Extensible**: subclass `PromptBase` to customize behavior

## Quick Start

### Installation

```bash
pip install gs-prompt-manager
```

### Define a Prompt

```python
from gs_prompt_manager import PromptBase

class GreetingPrompt(PromptBase):
    """A simple greeting prompt."""

    def set_prompt(self):
        return "Hello, {name}! Welcome to {place}."

    def set_name(self):
        self.name = "GreetingPrompt"

prompt = GreetingPrompt()
print(prompt({"name": "Alice", "place": "Wonderland"}))
# Hello, Alice! Welcome to Wonderland.
```

### Discover Prompts from a Directory

```python
from gs_prompt_manager import PromptManager

manager = PromptManager(prompt_paths="./my_prompts")
print(manager.get_prompt_names())

greeting = manager.get_prompt("GreetingPrompt")
result = greeting({"name": "Bob"})
```

### Bundle Variants with Prompt Groups

Variants are auto-detected by class-name suffix (`System`, `Chat`, `Pre`, `Post`, `Message`, `Prompt`) and bundled under a single group:

```python
class AssistantSystem(PromptBase):   # joins group "Assistant" with key "system"
    def set_prompt(self):
        return "You are a helpful assistant specialized in {domain}."

class AssistantChat(PromptBase):     # joins group "Assistant" with key "chat"
    def set_prompt(self):
        return "{user_message}"

manager = PromptManager(prompt_paths="./prompts")

# Explicit lookup
asst = manager.get_prompt_group("Assistant")

# Attribute shorthand (equivalent)
asst = manager.Assistant

system_msg = asst.system({"domain": "programming"})
user_msg   = asst.chat({"user_message": "Explain decorators"})
```

Need an explicit group name or key? Decorate the class:

```python
from gs_prompt_manager import PromptBase, prompt_group

@prompt_group("Assistant")
class FormalGreeting(PromptBase):   # key derived from class name -> "formalgreeting"
    ...

@prompt_group("Assistant", "polite")
class FormalGreeting2(PromptBase):  # explicit key -> "polite"
    ...
```

Solo prompts (no decorator, no recognized suffix) become their own group with key `"default"`.

## Documentation

Full documentation is hosted at **[gs-prompt-manager.readthedocs.io](https://gs-prompt-manager.readthedocs.io/)**.

- **[User Guide](https://gs-prompt-manager.readthedocs.io/en/latest/docs/user-guide/)** — concepts, configuration, and patterns
- **[Examples](https://gs-prompt-manager.readthedocs.io/en/latest/docs/examples/)** — real-world integrations with OpenAI, Claude, multi-agent systems
- **[Migration Guide](https://gs-prompt-manager.readthedocs.io/en/latest/docs/migration/)** — upgrading from earlier versions
- **[Contributing](CONTRIBUTING.md)** — how to contribute
- **[Changelog](CHANGELOG.md)** — version history

## Key Concepts

### PromptBase

The abstract base class. Subclass it and implement at minimum `set_prompt` and `set_name`:

```python
class MyPrompt(PromptBase):
    def set_prompt(self):
        return "Your template with {variables}"

    def set_name(self):
        self.name = "MyPrompt"
```

### PromptManager

Discovers and loads `PromptBase` subclasses from one or more directories:

```python
manager = PromptManager(prompt_paths=["./prompts", "./more_prompts"])
prompt = manager.get_prompt("MyPrompt")
```

Attribute-style access is also supported. Groups take priority; falls back to the bare prompt instance if no group matches:

```python
manager.Assistant          # → PromptGroup
manager.MyPrompt           # → PromptBase instance (if no group named "MyPrompt")
```

`dir(manager)` includes all group and prompt names for tab-completion.

### PromptGroup

A named collection of related prompts, queried by key:

```python
group = manager.get_prompt_group("Assistant")
group.system({"domain": "law"})            # attribute access -> renders the system variant
group["chat"]({"user_message": "hi"})      # dict-style access
list(group.get_prompt_names())             # ["system", "chat", ...]
```

### Variable Substitution

Two flavors:

1. **Variables** — `{variable}`, user-provided at call time (or via `set_variable_defaults`).
2. **Macros** — `<<MACRO>>`, generated by the prompt class itself (via `set_macros`).

```python
def set_prompt(self):
    return "User {name} logged in at <<DATETIME>>"

def set_variable_defaults(self):
    self.variable_defaults = {"name": "guest"}

def set_macros(self):
    import datetime
    self.macros = {"<<DATETIME>>": datetime.datetime.now().isoformat()}
```

## Use Cases

- **LLM application development**: organize prompts for ChatGPT, Claude, Gemini, etc.
- **Multi-variant prompts**: keep system / chat / pre / post variants together via groups.
- **Prompt engineering**: version and tag templates with rich metadata.
- **Multi-agent systems**: separate prompts per agent and per role.
- **Prompt libraries**: reusable, discoverable template collections.

## Requirements

- Python 3.8+
- regex >= 2022.1.18

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).

## Author

**Guan Huang**

## Links

- **GitHub**: https://github.com/CoronRing/gs_prompt_manager
- **PyPI**: https://pypi.org/project/gs-prompt-manager/
- **Issues**: https://github.com/CoronRing/gs_prompt_manager/issues
- **Documentation**: https://github.com/CoronRing/gs_prompt_manager/tree/main/docs
