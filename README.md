# gs_prompt_manager

[![PyPI version](https://badge.fury.io/py/gs-prompt-manager.svg)](https://badge.fury.io/py/gs-prompt-manager)
[![Python Support](https://img.shields.io/pypi/pyversions/gs-prompt-manager.svg)](https://pypi.org/project/gs-prompt-manager/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://github.com/CoronRing/gs_prompt_manager/workflows/Tests/badge.svg)](https://github.com/CoronRing/gs_prompt_manager/actions)

A lightweight Python package for managing and organizing prompt templates. Automatically discovers, loads, and manages prompt classes that inherit from `PromptBase`.

## ✨ Features

- 🔍 **Auto-discovery**: Automatically finds and loads prompt classes from specified directories
- 📦 **Template Management**: Define reusable prompt templates with variable substitution
- 🎯 **Type Safety**: Built-in validation for prompt pieces and metadata
- 🔧 **Flexible**: Support for both chat and system prompts
- 📝 **Metadata**: Rich metadata support for prompts (tags, tools, examples, etc.)
- 🔄 **Predefined Macros**: Support for datetime and custom macro substitution
- 🏗️ **Extensible**: Easy to subclass and customize for specific use cases

## 🚀 Quick Start

### Installation

```bash
pip install gs-prompt-manager
```

### Basic Usage

**Step 1: Create a Prompt**

```python
from gs_prompt_manager import PromptBase

class GreetingPrompt(PromptBase):
    """A simple greeting prompt."""

    def set_prompt_chat(self):
        return "Hello, {name}! Welcome to {place}."

    def set_prompt_system(self):
        return "You are a friendly assistant."

    def set_name(self):
        self.name = "GreetingPrompt"

# Use the prompt
prompt = GreetingPrompt()
print(prompt.get_prompt_chat({"name": "Alice", "place": "Wonderland"}))
# Output: Hello, Alice! Welcome to Wonderland.
```

**Step 2: Manage Multiple Prompts**

```python
from gs_prompt_manager import PromptManager

# Auto-discover prompts in a directory
manager = PromptManager(prompt_paths="./my_prompts")

# List available prompts
print(manager.get_prompt_names())

# Get a specific prompt
greeting = manager.get_prompt("GreetingPrompt")
result = greeting.get_prompt_chat({"name": "Bob"})
```

## 📖 Documentation

- **[User Guide](docs/user-guide.md)** - Complete usage guide
- **[Examples](docs/examples.md)** - Real-world integration examples
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history

## 💡 Key Concepts

### PromptBase

The base class for all prompt templates. Subclass it to create custom prompts:

```python
class MyPrompt(PromptBase):
    def set_prompt_chat(self):
        return "Your template with {variables}"

    def set_name(self):
        self.name = "MyPrompt"
```

### PromptManager

Automatically discovers and manages multiple prompt classes:

```python
manager = PromptManager(prompt_paths=["./prompts", "./more_prompts"])
prompt = manager.get_prompt("MyPrompt")
```

### Variable Substitution

Two types of variables are supported:

1. **Prompt Pieces** - `{variable}`: User-provided values
2. **Predefined Macros** - `<<MACRO>>`: System-generated values

```python
def set_prompt_chat(self):
    return "User {name} logged in at <<DATETIME>>"
```

## 🎯 Use Cases

- **LLM Application Development**: Manage prompts for ChatGPT, Claude, etc.
- **Prompt Engineering**: Organize and version control prompt templates
- **Multi-Agent Systems**: Define prompts for different AI agents
- **A/B Testing**: Compare different prompt variations
- **Prompt Libraries**: Build reusable prompt collections

## 📊 Requirements

- Python 3.8+
- regex >= 2022.1.18

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Guan Huang**

## 🔗 Links

- **GitHub**: https://github.com/CoronRing/gs_prompt_manager
- **PyPI**: https://pypi.org/project/gs-prompt-manager/
- **Issues**: https://github.com/CoronRing/gs_prompt_manager/issues
- **Documentation**: https://github.com/CoronRing/gs_prompt_manager/tree/main/docs

## ⭐ Star History

If you find this project helpful, please consider giving it a star on GitHub!
