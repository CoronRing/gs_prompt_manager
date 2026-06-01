# Changelog

All notable changes to gs_prompt_manager will be documented in this file. Only keep code changes here.

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
