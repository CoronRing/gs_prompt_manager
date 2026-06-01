# Documentation

## User Documentation

- **[User Guide](user-guide.md)** — installation, core concepts (PromptBase, PromptManager, PromptGroup), and configuration patterns.
- **[Examples](examples.md)** — real-world integrations with OpenAI, Claude, multi-agent systems, and advanced patterns.

## Developer Documentation

- **[Migration Guide](migration.md)** — upgrading from an earlier version
- **[Contributing](../CONTRIBUTING.md)** — how to contribute to the project
- **[Publishing](../PUBLISHING.md)** — release process for maintainers
- **[Changelog](../CHANGELOG.md)** — version history

## Quick Start

```bash
pip install gs-prompt-manager
```

```python
from gs_prompt_manager import PromptBase

class MyPrompt(PromptBase):
    def set_prompt(self):
        return "Hello, {name}!"

    def set_name(self):
        self.name = "MyPrompt"

prompt = MyPrompt()
print(prompt({"name": "World"}))
```

Bundle related variants — system / chat / pre / post / message — into a single `PromptGroup`:

```python
from gs_prompt_manager import PromptBase, PromptManager

class GreeterSystem(PromptBase):
    def set_prompt(self):
        return "You are a friendly greeter."

class GreeterChat(PromptBase):
    def set_prompt(self):
        return "Greet {name} in one sentence."

manager = PromptManager(prompt_paths="./prompts")
greeter = manager.get_prompt_group("Greeter")
print(greeter.system())
print(greeter.chat({"name": "Alice"}))
```

See the **[User Guide](user-guide.md)** for the complete API and the prompt-group resolution rules.
