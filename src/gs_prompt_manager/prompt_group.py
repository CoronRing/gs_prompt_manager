"""
PromptGroup system: a way to bundle related prompts (e.g. system/chat/pre/post
variants of the same logical prompt) under a single named group.

Groups can be defined three ways:

1. Explicitly via the @prompt_group decorator:
       @prompt_group("ABC")              # key derived from class name
       @prompt_group("ABC", "mykey")     # explicit key

2. Implicitly via a recognized suffix in the class name. Recognized suffixes
   (case-insensitive, with or without a leading underscore):
       system, chat, pre, post, message, prompt
   e.g. `ExampleChat` -> group `Example`, key `chat`.

3. As a solo group: any prompt without a decorator or recognized suffix becomes
   its own single-prompt group with key `default`. e.g. `SampleSpecial` -> group
   `SampleSpecial`, key `default`.
"""

from typing import Dict, List, Optional, Tuple

from gs_prompt_manager.prompt_base import PromptBase


# Recognized suffixes used for auto-detection of group membership.
# The canonical key stored in the group is the lowercased suffix itself.
RECOGNIZED_SUFFIXES: List[str] = [
    "system",
    "chat",
    "pre",
    "post",
    "message",
    "prompt",
]

# Attribute names used by the decorator to tag classes.
_GROUP_NAME_ATTR = "_gs_group_name"
_GROUP_KEY_ATTR = "_gs_group_key"


def prompt_group(name: str, key: Optional[str] = None):
    """
    Decorator that assigns a PromptBase subclass to a named group.

    Args:
        name: Group name.
        key: Optional explicit key for this prompt within the group. If omitted,
            the key is derived from the class name by stripping the group name
            prefix (case-insensitive), lowercasing, and removing underscores.
            If nothing remains, the key falls back to "default".

    Example:
        @prompt_group("ABC")
        class ABC_special(PromptBase):  # key -> "special"
            ...

        @prompt_group("ABC", "mykey")
        class ABCSpecial(PromptBase):   # key -> "mykey"
            ...
    """
    if not isinstance(name, str) or not name:
        raise ValueError("prompt_group: 'name' must be a non-empty string.")
    if key is not None and (not isinstance(key, str) or not key):
        raise ValueError("prompt_group: 'key' must be a non-empty string or None.")

    def decorator(cls):
        setattr(cls, _GROUP_NAME_ATTR, name)
        setattr(cls, _GROUP_KEY_ATTR, key)
        return cls

    return decorator


def resolve_auto_group(class_name: str) -> Optional[Tuple[str, str]]:
    """
    Try to match a recognized suffix at the end of `class_name`.

    Returns:
        (group_name, key) if a suffix matches and a non-empty stem remains,
        otherwise None.
    """
    lower = class_name.lower()
    # Try longest suffix first to handle overlap.
    for suffix in sorted(RECOGNIZED_SUFFIXES, key=len, reverse=True):
        if lower.endswith("_" + suffix):
            stem = class_name[: -(len(suffix) + 1)]
            if stem:
                return stem, suffix
        elif lower.endswith(suffix):
            stem = class_name[: -len(suffix)]
            if stem:
                return stem, suffix
    return None


def derive_decorator_key(
    class_name: str, group_name: str, explicit_key: Optional[str]
) -> str:
    """
    Derive the key for a prompt within a decorator-declared group.

    If `explicit_key` is provided, return it as-is. Otherwise strip the
    group_name prefix from class_name (case-insensitive), strip underscores,
    lowercase. Fall back to "default" if nothing remains.
    """
    if explicit_key:
        return explicit_key

    if class_name.lower().startswith(group_name.lower()):
        remainder = class_name[len(group_name):]
    else:
        remainder = class_name

    remainder = remainder.replace("_", "").lower()
    return remainder or "default"


class PromptGroup:
    """
    A named collection of related PromptBase instances, queryable by key.

    A group exposes its members three ways:
        group.get_prompt("system")    # explicit lookup
        group["system"]               # dict-style
        group.system                  # attribute-style (returns the PromptBase)

    Stringifying a group renders one of its members. Priority order:
        "default" -> "chat" -> any.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._prompts: Dict[str, PromptBase] = {}

    def add(self, key: str, prompt: PromptBase) -> None:
        if key in self._prompts:
            raise ValueError(
                f"Key '{key}' already exists in group '{self.name}' "
                f"(held by {type(self._prompts[key]).__name__})."
            )
        self._prompts[key] = prompt

    def get_prompt(self, key: str) -> PromptBase:
        if key not in self._prompts:
            raise ValueError(
                f"Key '{key}' not found in group '{self.name}'. "
                f"Available: {list(self._prompts.keys())}"
            )
        return self._prompts[key]

    def get_prompt_names(self) -> List[str]:
        return list(self._prompts.keys())

    def get_prompts(self) -> Dict[str, PromptBase]:
        return dict(self._prompts)

    def __getattr__(self, key: str) -> PromptBase:
        # Called only when normal attribute lookup fails. Dunder and private
        # names should not be treated as prompt keys.
        if key.startswith("_"):
            raise AttributeError(key)
        # Avoid recursion: _prompts may not exist yet during unpickling, etc.
        prompts = self.__dict__.get("_prompts")
        if prompts is not None and key in prompts:
            return prompts[key]
        raise AttributeError(
            f"PromptGroup '{self.__dict__.get('name', '?')}' has no prompt '{key}'. "
            f"Available: {list(prompts.keys()) if prompts else []}"
        )

    def __getitem__(self, key: str) -> PromptBase:
        return self.get_prompt(key)

    def __contains__(self, key: str) -> bool:
        return key in self._prompts

    def __iter__(self):
        return iter(self._prompts)

    def __len__(self) -> int:
        return len(self._prompts)

    def __str__(self) -> str:
        if "default" in self._prompts:
            return str(self._prompts["default"])
        if "chat" in self._prompts:
            return str(self._prompts["chat"])
        if self._prompts:
            return str(next(iter(self._prompts.values())))
        return f"<PromptGroup '{self.name}' (empty)>"

    def __repr__(self) -> str:
        return f"PromptGroup(name={self.name!r}, keys={list(self._prompts.keys())})"
