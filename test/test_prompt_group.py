"""
Tests for the PromptGroup system: @prompt_group decorator, suffix auto-detection,
solo groups, and PromptManager group resolution.
"""
import os
import tempfile
import shutil
import pytest

from gs_prompt_manager import PromptBase, PromptGroup, PromptManager, prompt_group
from gs_prompt_manager.prompt_group import (
    derive_decorator_key,
    resolve_auto_group,
)


# ----------------------------- unit: resolve_auto_group -----------------------------


class TestResolveAutoGroup:
    def test_camelcase_chat_suffix(self):
        assert resolve_auto_group("ExampleChat") == ("Example", "chat")

    def test_camelcase_system_suffix(self):
        assert resolve_auto_group("ExampleSystem") == ("Example", "system")

    def test_snake_case_chat_suffix(self):
        assert resolve_auto_group("Example_chat") == ("Example", "chat")

    def test_prompt_suffix(self):
        assert resolve_auto_group("SamplePrompt") == ("Sample", "prompt")

    def test_pre_suffix(self):
        assert resolve_auto_group("FooPre") == ("Foo", "pre")

    def test_post_suffix(self):
        assert resolve_auto_group("FooPost") == ("Foo", "post")

    def test_message_suffix(self):
        assert resolve_auto_group("FooMessage") == ("Foo", "message")

    def test_no_recognized_suffix(self):
        assert resolve_auto_group("SampleSpecial") is None

    def test_suffix_only_returns_none(self):
        # If the whole class name is just the suffix, there's no stem so no group.
        assert resolve_auto_group("Chat") is None

    def test_case_insensitive_match(self):
        assert resolve_auto_group("foo_CHAT") == ("foo", "chat")


# ----------------------------- unit: derive_decorator_key -----------------------------


class TestDeriveDecoratorKey:
    def test_explicit_key_passthrough(self):
        assert derive_decorator_key("ABCSpecial", "ABC", "goodname") == "goodname"

    def test_camelcase_strip(self):
        assert derive_decorator_key("ABCSpecial", "ABC", None) == "special"

    def test_underscore_strip(self):
        assert derive_decorator_key("ABC_special", "ABC", None) == "special"

    def test_case_insensitive_strip(self):
        assert derive_decorator_key("abc_special", "ABC", None) == "special"

    def test_empty_remainder_falls_back_to_default(self):
        assert derive_decorator_key("ABC", "ABC", None) == "default"

    def test_no_prefix_match_uses_full_name(self):
        # When class name does not start with group name, the full lowercased
        # name (sans underscores) becomes the key.
        assert derive_decorator_key("Other", "ABC", None) == "other"


# ----------------------------- unit: PromptGroup -----------------------------


def _make_prompt(name, prompt_text="Hello {x}", default_x="world"):
    """Build a working PromptBase instance for testing."""

    class _P(PromptBase):
        def set_prompt(self):
            return prompt_text

        def set_variable_defaults(self):
            self.variable_defaults = {"x": default_x}

        def set_macros(self):
            pass

        def set_name(self):
            self.name = name

        def set_tools(self):
            pass

    _P.__name__ = name
    return _P()


class TestPromptGroup:
    def test_add_and_get(self):
        g = PromptGroup("MyGroup")
        p = _make_prompt("P1")
        g.add("default", p)
        assert g.get_prompt("default") is p

    def test_duplicate_key_raises(self):
        g = PromptGroup("G")
        g.add("default", _make_prompt("A"))
        with pytest.raises(ValueError, match="already exists"):
            g.add("default", _make_prompt("B"))

    def test_attribute_access(self):
        g = PromptGroup("G")
        p = _make_prompt("P")
        g.add("system", p)
        assert g.system is p

    def test_getitem_access(self):
        g = PromptGroup("G")
        p = _make_prompt("P")
        g.add("chat", p)
        assert g["chat"] is p

    def test_contains(self):
        g = PromptGroup("G")
        g.add("chat", _make_prompt("P"))
        assert "chat" in g
        assert "system" not in g

    def test_iter_and_len(self):
        g = PromptGroup("G")
        g.add("chat", _make_prompt("A"))
        g.add("system", _make_prompt("B"))
        assert sorted(list(g)) == ["chat", "system"]
        assert len(g) == 2

    def test_missing_key_raises(self):
        g = PromptGroup("G")
        with pytest.raises(ValueError, match="not found in group"):
            g.get_prompt("nope")

    def test_missing_attr_raises(self):
        g = PromptGroup("G")
        with pytest.raises(AttributeError):
            _ = g.nope

    def test_str_priority_default(self):
        g = PromptGroup("G")
        g.add("chat", _make_prompt("Chat", "chat: {x}", "chat-x"))
        g.add("default", _make_prompt("Default", "default: {x}", "def-x"))
        assert str(g) == "default: def-x"

    def test_str_priority_chat_when_no_default(self):
        g = PromptGroup("G")
        g.add("chat", _make_prompt("Chat", "chat: {x}", "chat-x"))
        g.add("system", _make_prompt("Sys", "sys: {x}", "sys-x"))
        assert str(g) == "chat: chat-x"

    def test_str_priority_any_otherwise(self):
        g = PromptGroup("G")
        g.add("system", _make_prompt("Sys", "sys: {x}", "sys-x"))
        assert str(g) == "sys: sys-x"

    def test_str_empty_group(self):
        g = PromptGroup("Empty")
        assert "(empty)" in str(g)

    def test_group_call_via_attribute(self):
        g = PromptGroup("G")
        g.add("system", _make_prompt("Sys", "Hi {x}", "there"))
        assert g.system() == "Hi there"

    def test_get_prompt_names_and_get_prompts(self):
        g = PromptGroup("G")
        a = _make_prompt("A")
        b = _make_prompt("B")
        g.add("chat", a)
        g.add("system", b)
        assert sorted(g.get_prompt_names()) == ["chat", "system"]
        prompts = g.get_prompts()
        assert prompts == {"chat": a, "system": b}
        prompts.clear()
        assert "chat" in g

    def test_private_attribute_access_raises(self):
        g = PromptGroup("G")
        with pytest.raises(AttributeError):
            _ = g._anything

    def test_repr_contains_name_and_keys(self):
        g = PromptGroup("MyG")
        g.add("chat", _make_prompt("A"))
        r = repr(g)
        assert "MyG" in r
        assert "chat" in r


# ----------------------------- integration: PromptManager group resolution -----------------------------


def _write_prompt_file(dir_, filename, code):
    path = os.path.join(dir_, filename)
    with open(path, "w") as f:
        f.write(code)
    return path


@pytest.fixture
def group_prompt_dir():
    temp_dir = tempfile.mkdtemp()
    # Suffix-based auto-grouping
    _write_prompt_file(temp_dir, "example_prompts.py", """
from gs_prompt_manager import PromptBase

class ExampleChat(PromptBase):
    def set_prompt(self):
        return "Chat: {msg}"
    def set_variable_defaults(self):
        self.variable_defaults = {"msg": "hi"}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "ExampleChat"
    def set_tools(self):
        pass

class ExampleSystem(PromptBase):
    def set_prompt(self):
        return "System: {role}"
    def set_variable_defaults(self):
        self.variable_defaults = {"role": "assistant"}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "ExampleSystem"
    def set_tools(self):
        pass
""")
    # Solo (no recognized suffix)
    _write_prompt_file(temp_dir, "solo_prompts.py", """
from gs_prompt_manager import PromptBase

class SampleSpecial(PromptBase):
    def set_prompt(self):
        return "Special: {x}"
    def set_variable_defaults(self):
        self.variable_defaults = {"x": "alone"}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "SampleSpecial"
    def set_tools(self):
        pass
""")
    # Decorator-based grouping
    _write_prompt_file(temp_dir, "decorated_prompts.py", """
from gs_prompt_manager import PromptBase, prompt_group

@prompt_group("ABC")
class ABC_special(PromptBase):
    def set_prompt(self):
        return "ABC special: {x}"
    def set_variable_defaults(self):
        self.variable_defaults = {"x": "v"}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "ABC_special"
    def set_tools(self):
        pass

@prompt_group("ABC", "renamed")
class ABCSecond(PromptBase):
    def set_prompt(self):
        return "ABC second: {y}"
    def set_variable_defaults(self):
        self.variable_defaults = {"y": "v"}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "ABCSecond"
    def set_tools(self):
        pass
""")
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestPromptManagerGroupResolution:
    def test_groups_created(self, group_prompt_dir):
        manager = PromptManager(prompt_paths=group_prompt_dir)
        names = manager.get_prompt_group_names()
        assert "Example" in names
        assert "SampleSpecial" in names
        assert "ABC" in names

    def test_suffix_grouping_keys(self, group_prompt_dir):
        manager = PromptManager(prompt_paths=group_prompt_dir)
        example = manager.get_prompt_group("Example")
        assert "chat" in example
        assert "system" in example
        assert example.chat is manager.get_prompt("ExampleChat")
        assert example.system is manager.get_prompt("ExampleSystem")

    def test_solo_group_default_key(self, group_prompt_dir):
        manager = PromptManager(prompt_paths=group_prompt_dir)
        solo = manager.get_prompt_group("SampleSpecial")
        assert "default" in solo
        assert solo.default is manager.get_prompt("SampleSpecial")

    def test_decorator_derived_key(self, group_prompt_dir):
        manager = PromptManager(prompt_paths=group_prompt_dir)
        abc = manager.get_prompt_group("ABC")
        assert "special" in abc
        assert "renamed" in abc

    def test_render_through_group(self, group_prompt_dir):
        manager = PromptManager(prompt_paths=group_prompt_dir)
        example = manager.get_prompt_group("Example")
        assert example.chat({"msg": "yo"}) == "Chat: yo"
        assert example.system({"role": "tutor"}) == "System: tutor"

    def test_get_prompt_group_not_found(self, group_prompt_dir):
        manager = PromptManager(prompt_paths=group_prompt_dir)
        with pytest.raises(ValueError, match="Prompt group 'NoSuch' not found"):
            manager.get_prompt_group("NoSuch")

    def test_get_prompt_groups_returns_copy(self, group_prompt_dir):
        manager = PromptManager(prompt_paths=group_prompt_dir)
        groups = manager.get_prompt_groups()
        groups.pop("Example", None)
        assert "Example" in manager.get_prompt_group_names()

    def test_manager_getattr_group(self, group_prompt_dir):
        """manager.Example returns the PromptGroup directly."""
        manager = PromptManager(prompt_paths=group_prompt_dir)
        group = manager.Example
        assert isinstance(group, PromptGroup)
        assert group is manager.get_prompt_group("Example")

    def test_manager_getattr_prompt_fallback(self, group_prompt_dir):
        """When no group matches, attribute access falls back to the prompt instance."""
        manager = PromptManager(prompt_paths=group_prompt_dir)
        # SampleSpecial has a solo group; attribute access returns the group, not bare prompt
        result = manager.SampleSpecial
        assert isinstance(result, PromptGroup)

    def test_manager_getattr_unknown_raises(self, group_prompt_dir):
        manager = PromptManager(prompt_paths=group_prompt_dir)
        with pytest.raises(AttributeError):
            _ = manager.DoesNotExistAtAll

    def test_manager_dir_includes_names(self, group_prompt_dir):
        manager = PromptManager(prompt_paths=group_prompt_dir)
        d = dir(manager)
        assert "Example" in d
        assert "ABC" in d


class TestSampleDirGrouping:
    """The bundled sample directory: PromptHelloWorld + PromptHelloWorldSystem."""

    def test_hello_world_groups_resolved(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sample_dir = os.path.join(current_dir, "sample_prompts")
        manager = PromptManager(prompt_paths=sample_dir)

        assert "PromptHelloWorld" in manager.get_prompt_group_names()
        group = manager.get_prompt_group("PromptHelloWorld")
        assert "default" in group
        assert "system" in group
        assert group.system({"name": "Alice"}) == "Hello Alice"
        assert group.default({"world": "World"}) == "Hello World"


# ----------------------------- collision / mixed / metadata edge cases -----------------------------


@pytest.fixture
def collision_prompt_dir():
    """Two decorators target the same (group, key) -> collision."""
    temp_dir = tempfile.mkdtemp()
    _write_prompt_file(temp_dir, "collision.py", """
from gs_prompt_manager import PromptBase, prompt_group

@prompt_group("ZZ", "shared")
class ZZ_first(PromptBase):
    def set_prompt(self):
        return "first"
    def set_variable_defaults(self):
        self.variable_defaults = {}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "ZZ_first"
    def set_tools(self):
        pass

@prompt_group("ZZ", "shared")
class ZZ_second(PromptBase):
    def set_prompt(self):
        return "second"
    def set_variable_defaults(self):
        self.variable_defaults = {}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "ZZ_second"
    def set_tools(self):
        pass
""")
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def all_suffixes_dir():
    """One group with all suffix variants plus a default member."""
    temp_dir = tempfile.mkdtemp()
    _write_prompt_file(temp_dir, "full.py", """
from gs_prompt_manager import PromptBase

class Workflow(PromptBase):
    def set_prompt(self):
        return "workflow"
    def set_variable_defaults(self):
        self.variable_defaults = {}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "Workflow"
    def set_tools(self):
        pass

class WorkflowSystem(PromptBase):
    def set_prompt(self):
        return "system"
    def set_variable_defaults(self):
        self.variable_defaults = {}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "WorkflowSystem"
    def set_tools(self):
        pass

class WorkflowChat(PromptBase):
    def set_prompt(self):
        return "chat"
    def set_variable_defaults(self):
        self.variable_defaults = {}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "WorkflowChat"
    def set_tools(self):
        pass

class WorkflowPre(PromptBase):
    def set_prompt(self):
        return "pre"
    def set_variable_defaults(self):
        self.variable_defaults = {}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "WorkflowPre"
    def set_tools(self):
        pass

class WorkflowPost(PromptBase):
    def set_prompt(self):
        return "post"
    def set_variable_defaults(self):
        self.variable_defaults = {}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "WorkflowPost"
    def set_tools(self):
        pass

class WorkflowMessage(PromptBase):
    def set_prompt(self):
        return "message"
    def set_variable_defaults(self):
        self.variable_defaults = {}
    def set_macros(self):
        pass
    def set_name(self):
        self.name = "WorkflowMessage"
    def set_tools(self):
        pass
""")
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestGroupCollision:
    def test_collision_logs_warning_and_skips(self, collision_prompt_dir, caplog):
        import logging
        with caplog.at_level(logging.WARNING):
            manager = PromptManager(prompt_paths=collision_prompt_dir)
        group = manager.get_prompt_group("ZZ")
        assert len(group) == 1
        assert "shared" in group
        assert any("already has key 'shared'" in r.message for r in caplog.records)


class TestAllSuffixesInOneGroup:
    def test_all_six_keys_resolved(self, all_suffixes_dir):
        manager = PromptManager(prompt_paths=all_suffixes_dir)
        group = manager.get_prompt_group("Workflow")
        for key in ("default", "system", "chat", "pre", "post", "message"):
            assert key in group, f"missing key '{key}' in group"
        assert group.default() == "workflow"
        assert group.system() == "system"
        assert group.chat() == "chat"
        assert group.pre() == "pre"
        assert group.post() == "post"
        assert group.message() == "message"

    def test_str_picks_default_when_present(self, all_suffixes_dir):
        manager = PromptManager(prompt_paths=all_suffixes_dir)
        group = manager.get_prompt_group("Workflow")
        assert str(group) == "workflow"


class TestGetMetadataWithoutRelatedPrompt:
    """Confirm get_metadata works and uses the new key names."""

    def test_metadata_has_variable_defaults_and_macros(self):
        class _P(PromptBase):
            def set_prompt(self):
                return "Hello {x}"

            def set_variable_defaults(self):
                self.variable_defaults = {"x": "world"}

            def set_macros(self):
                pass

            def set_name(self):
                self.name = "MetaProbe"

            def set_tools(self):
                pass

        meta = _P().get_metadata()
        assert "related_prompt_names" not in meta
        assert "variable_defaults" in meta
        assert "macros" in meta
        assert meta["name"] == "MetaProbe"


class TestDecoratorOnInstance:
    """The decorator tags the class, not the instance."""

    def test_decorator_sets_class_attrs(self):
        @prompt_group("MyGrp", "k")
        class Dummy:
            pass

        assert Dummy._gs_group_name == "MyGrp"
        assert Dummy._gs_group_key == "k"

    def test_decorator_validates_name(self):
        with pytest.raises(ValueError, match="non-empty string"):
            prompt_group("")

    def test_decorator_validates_key_type(self):
        with pytest.raises(ValueError, match="non-empty string or None"):
            prompt_group("G", "")
