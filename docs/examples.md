# Examples

Real-world usage examples for `gs_prompt_manager`.

## Basic Usage

### Simple Prompt

```python
from gs_prompt_manager import PromptBase

class ChatbotPrompt(PromptBase):
    def set_prompt(self):
        return "User: {user_message}\nAssistant:"

    def set_name(self):
        self.name = "ChatbotPrompt"

prompt = ChatbotPrompt()
user_msg = prompt({"user_message": "What is Python?"})
```

### Prompt with Defaults

````python
from gs_prompt_manager import PromptBase

class CodeReviewPrompt(PromptBase):
    def set_prompt(self):
        return "Review this {language} code:\n\n```{language}\n{code}\n```"

    def set_variable_defaults(self):
        self.variable_defaults = {
            "language": "python",
            "code": ""
        }

    def set_name(self):
        self.name = "CodeReviewPrompt"

prompt = CodeReviewPrompt()
review = prompt({"code": "def add(a, b): return a + b"})
````

## LLM Integration

### OpenAI — System + Chat via Prompt Group

Two related prompts named with recognized suffixes (`System`, `Chat`) are auto-grouped under one name. Calling code asks the group for the variant it needs:

```python
from gs_prompt_manager import PromptBase, PromptManager
import openai

class AssistantSystem(PromptBase):
    def set_prompt(self):
        return "You are a helpful assistant specialized in {domain}."

    def set_variable_defaults(self):
        self.variable_defaults = {"domain": "general knowledge"}

    def set_name(self):
        self.name = "AssistantSystem"


class AssistantChat(PromptBase):
    def set_prompt(self):
        return "{user_input}"

    def set_variable_defaults(self):
        self.variable_defaults = {"user_input": ""}

    def set_name(self):
        self.name = "AssistantChat"


manager = PromptManager(prompt_paths="./prompts")

# Explicit lookup
asst = manager.get_prompt_group("Assistant")

# Attribute shorthand (equivalent)
# asst = manager.Assistant

client = openai.OpenAI(api_key="your-api-key")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": asst.system({"domain": "programming"})},
        {"role": "user",   "content": asst.chat({"user_input": "Explain decorators"})},
    ],
)
print(response.choices[0].message.content)
```

### Anthropic Claude — Same Pattern

```python
from gs_prompt_manager import PromptBase, PromptManager
import anthropic

class AnalysisSystem(PromptBase):
    def set_prompt(self):
        return "You are an expert analyst."

    def set_name(self):
        self.name = "AnalysisSystem"


class AnalysisChat(PromptBase):
    def set_prompt(self):
        return "Analyze: {content}"

    def set_name(self):
        self.name = "AnalysisChat"


manager = PromptManager(prompt_paths="./prompts")
analysis = manager.get_prompt_group("Analysis")

client = anthropic.Anthropic(api_key="your-api-key")
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    system=analysis.system(),
    messages=[{"role": "user", "content": analysis.chat({"content": "Market data..."})}],
)
print(message.content[0].text)
```

## Managing Multiple Prompts

### Directory Organization

```
my_project/
├── prompts/
│   ├── chat_prompts.py
│   ├── analysis_prompts.py
│   └── code_prompts.py
└── main.py
```

**prompts/chat_prompts.py:**

```python
from gs_prompt_manager import PromptBase

class FriendlyChat(PromptBase):
    def set_prompt(self):
        return "Hello! {message}"

    def set_name(self):
        self.name = "FriendlyChat"

class ProfessionalChat(PromptBase):
    def set_prompt(self):
        return "Dear {recipient}, {message}"

    def set_name(self):
        self.name = "ProfessionalChat"
```

**main.py:**

```python
from gs_prompt_manager import PromptManager

manager = PromptManager(prompt_paths="./prompts")
print("Available prompts:", manager.get_prompt_names())
print("Available groups:", manager.get_prompt_group_names())

friendly = manager.get_prompt("FriendlyChat")
professional = manager.get_prompt("ProfessionalChat")
```

Both `FriendlyChat` and `ProfessionalChat` end with the `Chat` suffix and have no shared stem, so each one is grouped on its own (group `Friendly` → key `chat`, group `Professional` → key `chat`). Use `@prompt_group` if you'd rather keep them together — see below.

## Explicit Grouping with `@prompt_group`

When class names don't follow the suffix convention — or you want to override the auto-resolved group — use the decorator:

```python
from gs_prompt_manager import PromptBase, prompt_group

@prompt_group("Greeting")
class FormalGreeting(PromptBase):       # key derived: "formal"
    def set_prompt(self):
        return "Good day. How may I help you?"

@prompt_group("Greeting", "casual")     # key explicit: "casual"
class HiThere(PromptBase):
    def set_prompt(self):
        return "Hey! What's up?"

manager = PromptManager(prompt_paths="./prompts")
greeting = manager.get_prompt_group("Greeting")

# or using attribute access:
# greeting = manager.Greeting

print(greeting.formal())
print(greeting.casual())
```

## Multi-Agent System

Each agent has its own group of system + chat prompts. Attribute-style access keeps dispatch concise:

```python
from gs_prompt_manager import PromptBase, PromptManager
import openai

class ResearcherSystem(PromptBase):
    def set_prompt(self):
        return "You are a research analyst."
    def set_name(self):
        self.name = "ResearcherSystem"

class ResearcherChat(PromptBase):
    def set_prompt(self):
        return "Research: {topic}"
    def set_name(self):
        self.name = "ResearcherChat"

class WriterSystem(PromptBase):
    def set_prompt(self):
        return "You are a technical writer."
    def set_name(self):
        self.name = "WriterSystem"

class WriterChat(PromptBase):
    def set_prompt(self):
        return "Write documentation for: {research}"
    def set_name(self):
        self.name = "WriterChat"


def run_agent(client, group, user_variables, model="gpt-4"):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": group.system()},
            {"role": "user",   "content": group.chat(user_variables)},
        ],
    ).choices[0].message.content


def create_documentation(topic):
    client = openai.OpenAI(api_key="your-api-key")
    manager = PromptManager(prompt_paths="./prompts")

    # Attribute access — no get_prompt_group() call needed
    research = run_agent(client, manager.Researcher, {"topic": topic})
    return run_agent(client, manager.Writer, {"research": research})


docs = create_documentation("Python async/await")
```

## Advanced Patterns

### Auto-Extracted Variables

If you don't explicitly declare variables, the base class extracts them from the template by scanning for `{var}` patterns. Pair with `set_variable_defaults_empty()` to give every extracted variable an empty default:

```python
from gs_prompt_manager import PromptBase

class SmartPrompt(PromptBase):
    def set_prompt(self):
        return "Process {input} and save to {output} in {format}"

    def set_variable_defaults(self):
        self.set_variable_defaults_empty()

    def set_name(self):
        self.name = "SmartPrompt"


prompt = SmartPrompt()
result = prompt({
    "input": "data.csv",
    "output": "report.pdf",
    "format": "PDF",
})
```

### Macros

`<<MACRO>>`-style placeholders are owned by the prompt class rather than passed in by callers — useful for timestamps, environment, run IDs, etc.

```python
from gs_prompt_manager import PromptBase
import datetime

class LogPrompt(PromptBase):
    def set_prompt(self):
        return "[<<TIMESTAMP>>] {level}: {message}"

    def set_macros(self):
        self.macros = {
            "<<TIMESTAMP>>": datetime.datetime.now().isoformat()
        }

    def set_variable_defaults(self):
        self.variable_defaults = {"level": "INFO", "message": ""}

    def set_name(self):
        self.name = "LogPrompt"


log = LogPrompt()
print(log({"level": "ERROR", "message": "Failed"}))
```

Macros can also be added at runtime via `prompt.add_macro("<<RUN_ID>>", "abc123")`.

### Error Handling

```python
from gs_prompt_manager import PromptManager

try:
    manager = PromptManager(prompt_paths="./prompts")

    if "MyPrompt" in manager.get_prompt_names():
        prompt = manager.get_prompt("MyPrompt")
        result = prompt({"var": "value"})
    else:
        print("Prompt not found")
except ValueError as e:
    print(f"Validation error: {e}")
```

## Testing

```python
import pytest
from gs_prompt_manager import PromptBase

class GreetingPrompt(PromptBase):
    def set_prompt(self):
        return "Hello, {name}!"

    def set_variable_defaults(self):
        self.variable_defaults = {"name": "World"}

    def set_name(self):
        self.name = "GreetingPrompt"


def test_default_render():
    assert GreetingPrompt()() == "Hello, World!"

def test_render_with_override():
    assert GreetingPrompt()({"name": "Alice"}) == "Hello, Alice!"
```

---

See the [User Guide](user-guide.md) for the full API reference and concepts.
