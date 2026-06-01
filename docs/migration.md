# Migration Guide

## 0.0.7 → 0.0.8

This release renames the core template vocabulary for clarity and adds attribute-style access on `PromptManager`. **All renames are breaking** — subclasses must update their `set_*` method names and any direct attribute access.

### Rename: prompt pieces → variables

Every occurrence of "piece" in the API is now "variable".

| Old | New |
|-----|-----|
| `set_prompt_pieces_available()` | `set_variables()` |
| `set_prompt_pieces_default_value()` | `set_variable_defaults()` |
| `set_prompt_pieces_default_value_empty()` | `set_variable_defaults_empty()` |
| `add_prompt_piece_default_value(piece, value)` | `add_variable_default(name, value)` |
| `self.prompt_pieces_available` | `self.variables` |
| `self.prompt_pieces_default_value` | `self.variable_defaults` |
| Constructor param `prompt_pieces_available` | `variables` |
| Constructor param `prompt_pieces_default_value` | `variable_defaults` |
| `get_prompt(prompt_pieces={})` | `get_prompt(variables={})` |
| `__call__(prompt_pieces={})` | `__call__(variables={})` |

### Rename: predefine value → macros

| Old | New |
|-----|-----|
| `set_prompt_predefine_value()` | `set_macros()` |
| `add_prompt_predefine_value(key, value)` | `add_macro(key, value)` |
| `self.prompt_predefine_value` | `self.macros` |
| Constructor param `prompt_predefine_value` | `macros` |

### Rename: metadata keys

`get_metadata()` now returns different keys:

| Old key | New key |
|---------|---------|
| `"default_prompt_pieces"` | `"variable_defaults"` |
| `"predefine_prompt_pieces"` | `"macros"` |

### Rename: PromptManager internal attribute

| Old | New |
|-----|-----|
| `manager.prompt_objects` | `manager.prompt_classes` |

### New: attribute-style access on PromptManager

`manager.SomeName` now works as a shorthand. Groups take priority over bare prompt instances:

```python
# Before (still works)
asst = manager.get_prompt_group("Assistant")

# New shorthand
asst = manager.Assistant
```

`dir(manager)` includes all group and prompt names for tab-completion.

### Quick find-and-replace

Run these in your editor across all prompt files:

| Find | Replace |
|------|---------|
| `set_prompt_pieces_available` | `set_variables` |
| `set_prompt_pieces_default_value_empty` | `set_variable_defaults_empty` |
| `set_prompt_pieces_default_value` | `set_variable_defaults` |
| `set_prompt_predefine_value` | `set_macros` |
| `add_prompt_piece_default_value` | `add_variable_default` |
| `add_prompt_predefine_value` | `add_macro` |
| `prompt_pieces_available` | `variables` |
| `prompt_pieces_default_value` | `variable_defaults` |
| `prompt_predefine_value` | `macros` |
| `"default_prompt_pieces"` | `"variable_defaults"` |
| `"predefine_prompt_pieces"` | `"macros"` |

---

## 0.0.6 → 0.0.7

No breaking changes. Added `Optional[...]` return-type annotations on all `set_*` abstract methods in `PromptBase` to silence Pylance `reportIncompatibleMethodOverride` warnings. No code changes required.

---

## 0.0.5 → 0.0.6

### Removed: `related_prompt` system

The `related_prompt` feature has been removed. Delete these from all subclasses:

```python
# Remove these — they no longer exist
def set_related_prompt(self):
    self.related_prompt = [OtherPrompt]
```

`get_metadata()` no longer returns `related_prompt_names`.

### Added: PromptGroup system

Related variants are now linked by naming convention or decorator rather than explicit references.

**Before** (0.0.5, no grouping):
```python
class AssistantSystem(PromptBase):
    def set_related_prompt(self):
        self.related_prompt = [AssistantChat]
    ...

class AssistantChat(PromptBase):
    ...

system = manager.get_prompt("AssistantSystem")
chat   = manager.get_prompt("AssistantChat")
```

**After** (0.0.6+, suffix auto-grouping):
```python
class AssistantSystem(PromptBase):   # no set_related_prompt needed
    ...

class AssistantChat(PromptBase):
    ...

# Both are in group "Assistant" automatically
asst = manager.get_prompt_group("Assistant")
asst.system({"domain": "..."})
asst.chat({"user_input": "..."})
```

#### Grouping rules (priority order)

1. **`@prompt_group` decorator** — explicit group and optional key.
2. **Class-name suffix** — `System`, `Chat`, `Pre`, `Post`, `Message`, `Prompt` (case-insensitive) auto-group under the stem name.
3. **Solo** — any other prompt becomes its own group with key `"default"`.

#### New PromptManager methods

```python
manager.get_prompt_group("Name")     # → PromptGroup
manager.get_prompt_group_names()     # → List[str]
manager.get_prompt_groups()          # → Dict[str, PromptGroup] (copy)
```

### Fixed: mutable default argument bug

In 0.0.5, passing a mutable default (`{}` or `[]`) to `PromptBase.__init__` would share state across instances. All constructor parameters are now `Optional[...] = None` and initialized fresh inside `__init__`. This is invisible unless you were relying on the shared-state behavior (which would have been a bug).
