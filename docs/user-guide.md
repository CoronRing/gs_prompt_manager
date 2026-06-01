# User Guide

Welcome to the gs_prompt_manager user guide! This guide will walk you through everything you need to know to use gs_prompt_manager effectively.

## Table of Contents

- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Creating Prompts](#creating-prompts)
- [Managing Prompts](#managing-prompts)
- [Prompt Groups](#prompt-groups)
- [Variable Substitution](#variable-substitution)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Installation

### From PyPI

```bash
pip install gs-prompt-manager
```

### From Source

```bash
git clone https://github.com/CoronRing/gs_prompt_manager.git
cd gs_prompt_manager
pip install -e .
```

### Verify Installation

```python
import gs_prompt_manager
print(gs_prompt_manager.__version__)
```

## Core Concepts

### PromptBase

`PromptBase` is the abstract base class for all prompts. It provides:

- Template string management
- Variable substitution
- Validation
- Metadata support

### PromptManager

`PromptManager` automatically discovers and loads prompt classes from directories, making them easy to access and use.

### PromptGroup

A `PromptGroup` is a named bundle of related `PromptBase` instances (for example, a system / chat / pre / post variant set), accessed by key. Groups are built automatically by `PromptManager` when prompts are loaded.

### Prompt Pieces

Variables in your prompts that users provide values for, denoted by `{variable_name}`.

### Predefined Macros

System-generated values that are automatically substituted, denoted by `<<MACRO_NAME>>`.

## Creating Prompts

### Minimal Prompt

The simplest prompt requires only a chat template and a name:

```python
from gs_prompt_manager import PromptBase

class SimplePrompt(PromptBase):
    def set_prompt(self):
        return "Hello, World!"

    def set_name(self):
        self.name = "SimplePrompt"

# Use it
prompt = SimplePrompt()
print(prompt())  # Output: Hello, World!
```

### Prompt with Variables

Add variables using `{variable}` syntax:

```python
class GreetingPrompt(PromptBase):
    def set_prompt(self):
        return "Hello, {name}! How are you today?"

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {"name": "Guest"}

    def set_name(self):
        self.name = "GreetingPrompt"

# Use it
prompt = GreetingPrompt()
print(prompt({"name": "Alice"}))  # Hello, Alice! How are you today?
print(prompt())  # Hello, Guest! How are you today? (uses default)
```

### Prompt with System Message

Many LLM APIs support separate system messages. Under the new API you create separate prompt classes for each variant:

```python
class AssistantChatPrompt(PromptBase):
    def set_prompt(self):
        return "Please help me with: {task}"

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {"task": "general questions"}

    def set_name(self):
        self.name = "AssistantChatPrompt"


class AssistantSystemPrompt(PromptBase):
    def set_prompt(self):
        return "You are a helpful assistant specialized in {domain}."

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {"domain": "general knowledge"}

    def set_name(self):
        self.name = "AssistantSystemPrompt"

# Use them
system = AssistantSystemPrompt()
chat = AssistantChatPrompt()
print(system({"domain": "programming"}))
# Output: You are a helpful assistant specialized in programming.
print(chat({"task": "debugging Python code"}))
# Output: Please help me with: debugging Python code
```

### Auto-Extracting Variables

Let gs_prompt_manager automatically extract variables from your template:

```python
class AutoPrompt(PromptBase):
    def set_prompt(self):
        return "Process {input} and generate {output} in {format}"


    def set_prompt_pieces_default_value(self):
        # Set empty strings as defaults
        self.set_prompt_pieces_default_value_empty()

    def set_name(self):
        self.name = "AutoPrompt"
```

### Using Predefined Macros

Add dynamic values that are automatically generated:

```python
import datetime

class LogPrompt(PromptBase):
    def set_prompt(self):
        return "Log entry at <<DATETIME>>: {message}"

    def set_prompt_predefine_value(self):
        self.prompt_predefine_value = {
            "<<DATETIME>>": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {"message": ""}

    def set_name(self):
        self.name = "LogPrompt"

# Use it
# Use it
prompt = LogPrompt()
print(prompt({"message": "User logged in"}))
# Output: Log entry at 2024-01-15 14:30:00: User logged in
```

### Adding Metadata

Enrich your prompts with metadata:

```python
class DocumentedPrompt(PromptBase):
    def __init__(self):
        super().__init__(
            description="A prompt for summarizing text",
            description_long="This prompt takes a long text and produces a concise summary",
            tags=["summarization", "text-processing"],
            author="Your Name",
            version="1.0.0",
        )

    def set_prompt(self):
        return "Summarize the following text:\n\n{text}"

    def set_name(self):
        self.name = "DocumentedPrompt"

# Access metadata
prompt = DocumentedPrompt()
metadata = prompt.get_metadata()
print(metadata["description"])  # A prompt for summarizing text
print(metadata["tags"])  # ["summarization", "text-processing"]
```

## Managing Prompts

### Using PromptManager

#### Auto-discover from Directory

```python
from gs_prompt_manager import PromptManager

# Load all prompts from a directory
manager = PromptManager(prompt_paths="./my_prompts")

# See what was loaded
print(manager.get_prompt_names())
# Output: ['GreetingPrompt', 'AssistantPrompt', 'LogPrompt', ...]
```

#### Multiple Directories

```python
manager = PromptManager(prompt_paths=[
    "./prompts/general",
    "./prompts/specialized",
    "./prompts/experimental"
])
```

#### Getting Prompts

```python
# Get a specific prompt
greeting = manager.get_prompt("GreetingPrompt")

# Use it
result = greeting({"name": "Alice"})

# Get all prompt instances
all_prompts = manager.get_prompt_instances()
for name, prompt in all_prompts.items():
    print(f"{name}: {prompt.description}")
```

### Directory Structure Example

Organize your prompts:

```
my_project/
├── prompts/
│   ├── __init__.py  (not needed but recommended)
│   ├── greeting_prompts.py
│   ├── task_prompts.py
│   └── specialized/
│       ├── code_prompts.py
│       └── data_prompts.py
└── main.py
```

**greeting_prompts.py:**

```python
from gs_prompt_manager import PromptBase

class WelcomePrompt(PromptBase):
    def set_prompt(self):
        return "Welcome, {name}!"

    def set_name(self):
        self.name = "WelcomePrompt"

class GoodbyePrompt(PromptBase):
    def set_prompt(self):
        return "Goodbye, {name}! See you soon."

    def set_name(self):
        self.name = "GoodbyePrompt"
```

**main.py:**

```python
from gs_prompt_manager import PromptManager

manager = PromptManager(prompt_paths="./prompts")
welcome = manager.get_prompt("WelcomePrompt")
print(welcome({"name": "Alice"}))
```

## Prompt Groups

Related prompt variants — system / chat / pre / post / message — often go together. A `PromptGroup` bundles them under one name so callers can pick the variant they need: `group.system(...)`, `group.chat(...)`, etc.

When you load prompts via `PromptManager`, groups are built automatically using one of three rules. The first matching rule wins, in this order:

1. **`@prompt_group` decorator** — explicit group name (and optional explicit key).
2. **Class-name suffix** — recognized suffix maps the prompt into a group automatically.
3. **Solo** — a prompt that matches neither becomes its own one-member group with key `"default"`.

### Auto-Grouping by Suffix

These suffixes (case-insensitive, with or without a leading underscore) trigger auto-grouping:

| Suffix       | Key in group |
|--------------|--------------|
| `System`     | `system`     |
| `Chat`       | `chat`       |
| `Pre`        | `pre`        |
| `Post`       | `post`       |
| `Message`    | `message`    |
| `Prompt`     | `prompt`     |

Example:

```python
from gs_prompt_manager import PromptBase

class AssistantSystem(PromptBase):
    def set_prompt(self):
        return "You are a helpful assistant in {domain}."

class AssistantChat(PromptBase):
    def set_prompt(self):
        return "{user_message}"
```

After loading via `PromptManager`, both end up in the group `Assistant`:

```python
asst = manager.get_prompt_group("Assistant")
system_text = asst.system({"domain": "biology"})
user_text   = asst.chat({"user_message": "Explain mitosis."})
```

If a class name *is* the suffix (e.g. `Chat` on its own), it does not strip to an empty group — it becomes a solo group instead.

### Explicit Grouping with `@prompt_group`

When the class name doesn't follow the suffix convention, decorate it:

```python
from gs_prompt_manager import PromptBase, prompt_group

@prompt_group("Assistant")
class FormalAssistantGreeting(PromptBase):
    def set_prompt(self):
        return "Good day. How may I help?"

@prompt_group("Assistant", "casual")
class HiThere(PromptBase):
    def set_prompt(self):
        return "Hey! What's up?"
```

Key derivation (when no explicit key is given): the group-name prefix is stripped from the class name (case-insensitive), underscores are removed, and the rest is lowercased. If nothing remains, the key falls back to `"default"`.

| Class name             | Decorator                      | Resulting key |
|------------------------|--------------------------------|---------------|
| `ABC_special`          | `@prompt_group("ABC")`         | `special`     |
| `ABCFancy`             | `@prompt_group("ABC")`         | `fancy`       |
| `ABC`                  | `@prompt_group("ABC")`         | `default`     |
| `ABCWhatever`          | `@prompt_group("ABC", "main")` | `main`        |

### Solo Groups

A prompt with no decorator and no recognized suffix becomes its own group:

```python
class SampleSpecial(PromptBase):  # group "SampleSpecial", key "default"
    def set_prompt(self):
        return "Just me."
```

This means every loaded prompt is reachable via `get_prompt_group` even if you don't use grouping deliberately.

### Querying Groups

```python
manager = PromptManager(prompt_paths="./prompts")

manager.get_prompt_group_names()           # list of group names
manager.get_prompt_groups()                # dict[str, PromptGroup] (copy)
group = manager.get_prompt_group("Assistant")

group.get_prompt_names()                   # ["system", "chat", ...]
group.system                               # PromptBase instance (attribute access)
group["chat"]                              # PromptBase instance (dict-style)
"system" in group                          # True / False
len(group)                                 # member count

# Render a member directly:
group.system({"domain": "law"})
group["chat"]({"user_message": "hi"})
```

Converting a group to a string renders one of its members. Priority: `default` → `chat` → first available.

### Collisions

If two prompts would land on the same `(group, key)` pair, the first one wins and the second emits a warning. To resolve, give one of them an explicit key with `@prompt_group(group_name, "unique_key")`.

## Variable Substitution

### Prompt Pieces (User Variables)

Variables provided by users at runtime:

```python
class EmailPrompt(PromptBase):
    def set_prompt(self):
        return """
        To: {recipient}
        From: {sender}
        Subject: {subject}

        {body}
        """

    def set_name(self):
        self.name = "EmailPrompt"

# Use it
prompt = EmailPrompt()
email = prompt({
    "recipient": "alice@example.com",
    "sender": "bob@example.com",
    "subject": "Meeting Tomorrow",
    "body": "Let's meet at 2pm."
})
```

### Default Values

Provide fallback values:

```python
def set_prompt_pieces_default_value(self):
    self.prompt_pieces_default_value = {
        "recipient": "team@example.com",
        "sender": "noreply@example.com",
        "subject": "No Subject",
        "body": ""
    }
```

### Predefined Macros (System Variables)

Values automatically generated by the system:

```python
import datetime
import os

class ContextPrompt(PromptBase):
    def set_prompt(self):
        return """
        Timestamp: <<DATETIME>>
        User: <<USERNAME>>
        Environment: <<ENVIRONMENT>>

        Task: {task}
        """

    def set_prompt_predefine_value(self):
        self.prompt_predefine_value = {
            "<<DATETIME>>": datetime.datetime.now().isoformat(),
            "<<USERNAME>>": os.getenv("USER", "unknown"),
            "<<ENVIRONMENT>>": os.getenv("ENV", "development")
        }

    def set_name(self):
        self.name = "ContextPrompt"
```

### Dynamic Macro Values

Update macros at runtime:

```python
prompt = ContextPrompt()

# Add new macro
prompt.add_prompt_predefine_value("<<CONFIG>>", "production")

# Use it
result = prompt({"task": "Process data"})
```

## Best Practices

### 1. Organize by Purpose

```
prompts/
├── customer_service/
│   ├── greeting.py
│   ├── support.py
│   └── farewell.py
├── data_processing/
│   ├── validation.py
│   └── transformation.py
└── reporting/
    └── summary.py
```

### 2. Use Descriptive Names

```python
class CustomerSupportGreetingPrompt(PromptBase):  # Good
    pass

class Prompt1(PromptBase):  # Bad
    pass
```

### 3. Document Your Prompts

```python
class WellDocumentedPrompt(PromptBase):
    """
    A prompt for processing customer inquiries.

    This prompt handles initial customer requests and
    routes them to appropriate handlers.
    """

    def __init__(self):
        super().__init__(
            description="Customer inquiry processor",
            tags=["customer-service", "routing"],
            version="2.0.0"
        )

    # ... rest of implementation
```

### 4. Validate Inputs

```python
def set_prompt_pieces_default_value(self):
    # Always provide defaults
    self.prompt_pieces_default_value = {
        "user_input": "",
        "context": "general"
    }
```

### 5. Version Your Prompts

```python
class DataProcessorPromptV2(PromptBase):
    def __init__(self):
        super().__init__(version="2.0.0")

    def set_name(self):
        self.name = "DataProcessorPromptV2"
```

### 6. Use Inheritance for Variations

```python
class BaseAssistantPrompt(PromptBase):
    def set_prompt(self):
        return "You are a helpful assistant."

class TechnicalAssistantPrompt(BaseAssistantPrompt):
    def set_prompt(self):
        return "You are a helpful technical assistant specialized in programming."

    def set_name(self):
        self.name = "TechnicalAssistantPrompt"
```

## Troubleshooting

### Prompt Not Found

**Error:** `ValueError: Prompt 'MyPrompt' not found`

**Solutions:**

1. Check the prompt name matches the class name
2. Verify the prompt file is in the search path
3. Ensure the class inherits from `PromptBase`

```python
# Check what was loaded
manager = PromptManager(prompt_paths="./prompts")
print(manager.get_prompt_names())
```

### Missing Required Variable

**Error:** `ValueError: Prompt piece 'name' required`

**Solution:** Provide the required variable or set a default:

```python
# Option 1: Provide the variable
prompt({"name": "Alice"})

# Option 2: Set a default
def set_prompt_pieces_default_value(self):
    self.prompt_pieces_default_value = {"name": "Guest"}
```

### Invalid Path

**Error:** `ValueError: Provided path is not a directory`

**Solution:** Check the path exists:

```python
import os

path = "./prompts"
if not os.path.exists(path):
    os.makedirs(path)

manager = PromptManager(prompt_paths=path)
```

### Prompt Group Not Found

**Error:** `ValueError: Prompt group 'X' not found`

**Solutions:**

1. Check the suffix on your class names — recognized suffixes are listed in the [Prompt Groups](#prompt-groups) section. `ExampleChat` becomes group `Example`, not `ExampleChat`.
2. If you used `@prompt_group("Foo")`, the group name is `Foo`, not the class name.
3. Inspect what was loaded:

```python
print(manager.get_prompt_group_names())
print({n: g.get_prompt_names() for n, g in manager.get_prompt_groups().items()})
```

### Duplicate Prompt Names

**Warning:** `Duplicate prompt class 'MyPrompt' found`

**Solution:** Ensure each prompt class has a unique name:

```python
# Instead of having two classes named 'HelperPrompt':
class GeneralHelperPrompt(PromptBase):
    def set_name(self):
        self.name = "GeneralHelperPrompt"

class SpecializedHelperPrompt(PromptBase):
    def set_name(self):
        self.name = "SpecializedHelperPrompt"
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'gs_prompt_manager'`

**Solution:**

```bash
pip install gs-prompt-manager
# or for development
pip install -e .
```

## Next Steps

- Check out the [API Reference](api-reference.md) for detailed method documentation
- See [Examples](examples.md) for real-world usage patterns
- Read [Contributing Guide](../CONTRIBUTING.md) to contribute to the project
