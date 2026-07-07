# Changelog

All notable changes to gs_prompt_manager will be documented in this file. Only keep code changes here.

## [0.0.9]

### Added

- Brace escaping in prompt templates: `\{` / `\}` render as literal braces and are excluded from variable auto-extraction and substitution, so a `\{...\}` token never becomes a required variable. Applies to `get_prompt`, `__call__`, and `__str__`.

### Removed

- Unused `PromptBase._escape_braces` helper (dead code implementing a conflicting double-brace convention)

## [0.0.8]

### Changed

- Renamed `prompt_pieces_available` → `variables`, `prompt_pieces_default_value` → `variable_defaults`, `prompt_predefine_value` → `macros` throughout `PromptBase` (constructor params, instance attributes, abstract methods, and helpers)
- Renamed abstract methods: `set_prompt_pieces_available()` → `set_variables()`, `set_prompt_pieces_default_value()` → `set_variable_defaults()`, `set_prompt_predefine_value()` → `set_macros()`
- Renamed helpers: `add_prompt_piece_default_value(piece, value)` → `add_variable_default(name, value)`, `add_prompt_predefine_value(key, value)` → `add_macro(key, value)`, `set_prompt_pieces_default_value_empty()` → `set_variable_defaults_empty()`
- `get_prompt(prompt_pieces)` / `__call__(prompt_pieces)` parameter renamed to `variables`
- `get_metadata()` keys `"default_prompt_pieces"` → `"variable_defaults"` and `"predefine_prompt_pieces"` → `"macros"`
- Renamed internal `_check_default_prompt_pieces()` → `_check_variable_defaults()`
- Renamed `PromptManager.prompt_objects` → `prompt_classes` for clarity

### Added

- `PromptManager.__getattr__`: attribute-style access for groups and prompts (`manager.MyGroup`, `manager.MyPrompt`); groups take priority over bare prompt instances
- `PromptManager.__dir__`: includes group and prompt names in tab-completion

## [0.0.7]

### Added

- Tutorial Jupyter notebook (`docs/tutorial.ipynb`) covering every feature of the library end-to-end

### Fixed

- Added `Optional[...]` return-type annotations to all `set_*` abstract methods on `PromptBase` so subclasses that `return "..."` no longer trigger Pylance / pyright `reportIncompatibleMethodOverride` warnings

## [0.0.6]

### Added

- `PromptGroup` system: bundle related variants (system / chat / pre / post / message / prompt) under a single named group, queryable via `manager.get_prompt_group(name)` with attribute, dict, and callable access (`group.system(...)`, `group["chat"]`)
- `@prompt_group` decorator for explicit group assignment with optional explicit key
- Auto-detection of group membership from class-name suffix (case-insensitive, with or without underscore)
- `PromptManager.get_prompt_group`, `get_prompt_group_names`, `get_prompt_groups`

### Changed

- Removed the `related_prompt` system from `PromptBase` and `PromptManager` (superseded by `PromptGroup`)
- `get_metadata()` no longer returns `related_prompt_names`

### Fixed

- Fixed mutable default argument bug in `PromptBase.__init__` that caused state to leak across instances when subclasses mutated default piece dicts in place

## [0.0.5]

### Fixed

- Fixed Python 3.8 and 3.9 compatibility by using `Union[str, List[str]]` instead of `str | List[str]` syntax
- Fixed license field in pyproject.toml for compatibility with older setuptools versions
- Removed conflicting license classifier from pyproject.toml

### Changed

- Streamlined documentation from 2500+ to 687 lines, removing redundancy
- Removed api-reference.md (users can read code directly)
- Simplified docs/README.md structure

## [0.0.4]

### Added

- Validation for prompt structures
- Examples and documentation
- Support for both chat and system prompts

## [0.0.3] - Previous Release

### Added

- Initial public release
- Core functionality for prompt management

## [0.0.2] - Previous Release

### Added

- Early development version

## [0.0.1] - Initial Release

### Added

- Basic project structure
- PromptBase foundation
- Initial PromptManager implementation
