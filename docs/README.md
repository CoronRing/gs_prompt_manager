# Documentation

## User Documentation

- **[User Guide](user-guide.md)** - Complete guide covering installation, concepts, and usage
- **[Examples](examples.md)** - Real-world integration examples with OpenAI, Claude, and multi-agent systems

## Developer Documentation

- **[Contributing](../CONTRIBUTING.md)** - How to contribute to the project
- **[Publishing](../PUBLISHING.md)** - Release process for maintainers
- **[Changelog](../CHANGELOG.md)** - Version history

## Quick Start

```bash
pip install gs-prompt-manager
```

```python
from gs_prompt_manager import PromptBase

class MyPrompt(PromptBase):
    def set_prompt_chat(self):
        return "Hello, {name}!"

    def set_name(self):
        self.name = "MyPrompt"

prompt = MyPrompt()
print(prompt.get_prompt_chat({"name": "World"}))
```

See the **[User Guide](user-guide.md)** for complete documentation.
