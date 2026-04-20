# Changelog

All notable changes to gs_prompt_manager will be documented in this file. Only keep code changes here.

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
