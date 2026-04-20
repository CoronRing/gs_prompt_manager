# Examples

Real-world usage examples for gs_prompt_manager.

## Basic Usage

### Simple Prompt

```python
from gs_prompt_manager import PromptBase

class ChatbotPrompt(PromptBase):
    def set_prompt(self):
        return "User: {user_message}\nAssistant:"

    def set_name(self):
        self.name = "ChatbotPrompt"

# Use it
prompt = ChatbotPrompt()
user_msg = prompt({"user_message": "What is Python?"})
system_msg = None
```

### Prompt with Defaults

````python
from gs_prompt_manager import PromptBase

class CodeReviewPrompt(PromptBase):
    def set_prompt(self):
        return """Review this {language} code:

```{language}
{code}
```"""

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {
            "language": "python",
            "code": ""
        }

    def set_name(self):
        self.name = "CodeReviewPrompt"

prompt = CodeReviewPrompt()
review = prompt({"code": "def add(a, b): return a + b"})
````

## LLM Integration

### OpenAI Example

```python
from gs_prompt_manager import PromptBase
import openai

class AssistantChatPrompt(PromptBase):
    def set_prompt(self):
        return "{user_input}"

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {"user_input": ""}

    def set_name(self):
        self.name = "AssistantChatPrompt"


class AssistantSystemPrompt(PromptBase):
    def set_prompt(self):
        return "You are a helpful assistant specialized in {domain}."

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {"domain": "general knowledge"}

    def set_name(self):
        self.name = "AssistantSystemPrompt"

client = openai.OpenAI(api_key="your-api-key")
chat_prompt = AssistantChatPrompt()
system_prompt = AssistantSystemPrompt()

    response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt({"domain": "programming"})},
        {"role": "user", "content": chat_prompt({"user_input": "Explain decorators"})}
    ]
)

print(response.choices[0].message.content)
```

### Anthropic Claude Example

```python
from gs_prompt_manager import PromptBase
import anthropic

class AnalysisChatPrompt(PromptBase):
    def set_prompt(self):
        return "Analyze: {content}"

    def set_name(self):
        self.name = "AnalysisChatPrompt"


class AnalysisSystemPrompt(PromptBase):
    def set_prompt(self):
        return "You are an expert analyst."

    def set_name(self):
        self.name = "AnalysisSystemPrompt"

client = anthropic.Anthropic(api_key="your-api-key")
chat_prompt = AnalysisChatPrompt()
system_prompt = AnalysisSystemPrompt()

    message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    system=system_prompt(),
    messages=[{
        "role": "user",
        "content": chat_prompt({"content": "Market data..."})
    }]
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
print("Available:", manager.get_prompt_names())

    friendly = manager.get_prompt("FriendlyChat")
    professional = manager.get_prompt("ProfessionalChat")
```

## Multi-Agent System

```python
from gs_prompt_manager import PromptBase
import openai

class ResearcherChatPrompt(PromptBase):
    def set_prompt(self):
        return "Research: {topic}"

    def set_name(self):
        self.name = "ResearcherChatPrompt"


class ResearcherSystemPrompt(PromptBase):
    def set_prompt(self):
        return "You are a research analyst."

    def set_name(self):
        self.name = "ResearcherSystemPrompt"


class WriterChatPrompt(PromptBase):
    def set_prompt(self):
        return "Write documentation for: {research}"

    def set_name(self):
        self.name = "WriterChatPrompt"


class WriterSystemPrompt(PromptBase):
    def set_prompt(self):
        return "You are a technical writer."

    def set_name(self):
        self.name = "WriterSystemPrompt"

def create_documentation(topic):
    client = openai.OpenAI(api_key="your-api-key")

    # Agent 1: Research
    researcher_sys = ResearcherSystemPrompt()
    researcher_chat = ResearcherChatPrompt()
    research = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": researcher_sys()},
            {"role": "user", "content": researcher_chat({"topic": topic})}
        ]
    ).choices[0].message.content

    # Agent 2: Write
    writer_sys = WriterSystemPrompt()
    writer_chat = WriterChatPrompt()
    draft = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": writer_sys()},
            {"role": "user", "content": writer_chat({"research": research})}
        ]
    ).choices[0].message.content

    return draft

docs = create_documentation("Python async/await")
```

## Advanced Patterns

### Auto-Extract Variables

```python
from gs_prompt_manager import PromptBase

class SmartPrompt(PromptBase):
    def set_prompt(self):
        return "Process {input} and save to {output} in {format}"uto-extracts variables

    def set_prompt_pieces_default_value(self):
        self.set_prompt_pieces_default_value_empty()

    def set_name(self):
        self.name = "SmartPrompt"

    prompt = SmartPrompt()
    result = prompt({
    "input": "data.csv",
    "output": "report.pdf",
    "format": "PDF"
})
```

### Predefined Macros

```python
from gs_prompt_manager import PromptBase
import datetime

class LogPrompt(PromptBase):
    def set_prompt(self):
        return "[<<TIMESTAMP>>] {level}: {message}"

    def set_prompt_predefine_value(self):
        self.prompt_predefine_value = {
            "<<TIMESTAMP>>": datetime.datetime.now().isoformat()
        }

    def set_name(self):
        self.name = "LogPrompt"

# Note: use callable prompt instances now
log = LogPrompt()
print(log({"level": "ERROR", "message": "Failed"}))
# [2024-01-15T14:30:00] ERROR: Failed
```

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

    def set_name(self):
        self.name = "GreetingPrompt"

def test_prompt():
    prompt = GreetingPrompt()
    assert prompt({"name": "Alice"}) == "Hello, Alice!"
    assert prompt.name == "GreetingPrompt"
```

---

See the [User Guide](user-guide.md) for detailed documentation.
