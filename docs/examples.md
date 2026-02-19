# Examples

Real-world usage examples for gs_prompt_manager.

## Basic Usage

### Simple Prompt

```python
from gs_prompt_manager import PromptBase

class ChatbotPrompt(PromptBase):
    def set_prompt_chat(self):
        return "User: {user_message}\nAssistant:"

    def set_prompt_system(self):
        return "You are a helpful AI assistant."

    def set_name(self):
        self.name = "ChatbotPrompt"

# Use it
prompt = ChatbotPrompt()
user_msg = prompt.get_prompt_chat({"user_message": "What is Python?"})
system_msg = prompt.get_prompt_system()
```

### Prompt with Defaults

````python
from gs_prompt_manager import PromptBase

class CodeReviewPrompt(PromptBase):
    def set_prompt_chat(self):
        return """Review this {language} code:

```{language}
{code}
```"""

   def set_prompt_pieces_available(self):
        self.prompt_pieces_available = ["language", "code"]

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {
            "language": "python",
            "code": ""
        }

    def set_name(self):
        self.name = "CodeReviewPrompt"

prompt = CodeReviewPrompt()
review = prompt.get_prompt_chat({"code": "def add(a, b): return a + b"})
````

## LLM Integration

### OpenAI Example

```python
from gs_prompt_manager import PromptBase
import openai

class AssistantPrompt(PromptBase):
    def set_prompt_chat(self):
        return "{user_input}"

    def set_prompt_system(self):
        return "You are a helpful assistant specialized in {domain}."

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {
            "user_input": "",
            "domain": "general knowledge"
        }

    def set_name(self):
        self.name = "AssistantPrompt"

client = openai.OpenAI(api_key="your-api-key")
prompt = AssistantPrompt()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": prompt.get_prompt_system({"domain": "programming"})},
        {"role": "user", "content": prompt.get_prompt_chat({"user_input": "Explain decorators"})}
    ]
)

print(response.choices[0].message.content)
```

### Anthropic Claude Example

```python
from gs_prompt_manager import PromptBase
import anthropic

class AnalysisPrompt(PromptBase):
    def set_prompt_chat(self):
        return "Analyze: {content}"

    def set_prompt_system(self):
        return "You are an expert analyst."

    def set_name(self):
        self.name = "AnalysisPrompt"

client = anthropic.Anthropic(api_key="your-api-key")
prompt = AnalysisPrompt()

message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    system=prompt.get_prompt_system(),
    messages=[{
        "role": "user",
        "content": prompt.get_prompt_chat({"content": "Market data..."})
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
    def set_prompt_chat(self):
        return "Hello! {message}"

    def set_name(self):
        self.name = "FriendlyChat"

class ProfessionalChat(PromptBase):
    def set_prompt_chat(self):
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

class ResearcherPrompt(PromptBase):
    def set_prompt_system(self):
        return "You are a research analyst."

    def set_prompt_chat(self):
        return "Research: {topic}"

    def set_name(self):
        self.name = "ResearcherPrompt"

class WriterPrompt(PromptBase):
    def set_prompt_system(self):
        return "You are a technical writer."

    def set_prompt_chat(self):
        return "Write documentation for: {research}"

    def set_name(self):
        self.name = "WriterPrompt"

def create_documentation(topic):
    client = openai.OpenAI(api_key="your-api-key")

    # Agent 1: Research
    researcher = ResearcherPrompt()
    research = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": researcher.get_prompt_system()},
            {"role": "user", "content": researcher.get_prompt_chat({"topic": topic})}
        ]
    ).choices[0].message.content

    # Agent 2: Write
    writer = WriterPrompt()
    draft = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": writer.get_prompt_system()},
            {"role": "user", "content": writer.get_prompt_chat({"research": research})}
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
    def set_prompt_chat(self):
        return "Process {input} and save to {output} in {format}"

    def set_prompt_pieces_available(self):
        super().set_prompt_pieces_available()  # Auto-extracts variables

    def set_prompt_pieces_default_value(self):
        self.set_prompt_pieces_default_value_empty()

    def set_name(self):
        self.name = "SmartPrompt"

prompt = SmartPrompt()
result = prompt.get_prompt_chat({
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
    def set_prompt_chat(self):
        return "[<<TIMESTAMP>>] {level}: {message}"

    def set_prompt_predefine_value(self):
        self.prompt_predefine_value = {
            "<<TIMESTAMP>>": datetime.datetime.now().isoformat()
        }

    def set_name(self):
        self.name = "LogPrompt"

log = LogPrompt()
print(log.get_prompt_chat({"level": "ERROR", "message": "Failed"}))
# [2024-01-15T14:30:00] ERROR: Failed
```

### Error Handling

```python
from gs_prompt_manager import PromptManager

try:
    manager = PromptManager(prompt_paths="./prompts")

    if "MyPrompt" in manager.get_prompt_names():
        prompt = manager.get_prompt("MyPrompt")
        result = prompt.get_prompt_chat({"var": "value"})
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
    def set_prompt_chat(self):
        return "Hello, {name}!"

    def set_name(self):
        self.name = "GreetingPrompt"

def test_prompt():
    prompt = GreetingPrompt()
    assert prompt.get_prompt_chat({"name": "Alice"}) == "Hello, Alice!"
    assert prompt.name == "GreetingPrompt"
```

---

See the [User Guide](user-guide.md) for detailed documentation.
