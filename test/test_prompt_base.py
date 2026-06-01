"""
Tests for the PromptBase class.
"""
import pytest
import datetime
from gs_prompt_manager import PromptBase


class SimplePrompt(PromptBase):
    """A minimal prompt for testing."""

    def set_prompt(self):
        return "Simple prompt: {input_text}"

    def set_variable_defaults(self):
        self.variable_defaults = {"input_text": "default text"}

    def set_macros(self):
        self.macros = {
            "<<DATETIME>>": "2024-01-01 12:00:00",
        }

    def set_name(self):
        self.name = "SimplePrompt"

    def set_tools(self):
        self.tools = []


class PromptWithMacros(PromptBase):
    """A prompt with predefined macros."""

    def set_prompt(self):
        return "Date: <<DATETIME>>, User: {user_name}"

    def set_variable_defaults(self):
        self.variable_defaults = {}

    def set_macros(self):
        self.macros = {
            "<<DATETIME>>": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def set_name(self):
        self.name = "PromptWithMacros"

    def set_tools(self):
        self.tools = []


class TestPromptBase:
    """Test suite for PromptBase class."""

    def test_basic_instantiation(self):
        """Test that a simple prompt can be instantiated."""
        prompt = SimplePrompt()
        assert prompt.name == "SimplePrompt"
        assert prompt.prompt == "Simple prompt: {input_text}"

    def test_get_metadata(self):
        """Test metadata retrieval."""
        prompt = SimplePrompt()
        metadata = prompt.get_metadata()

        assert isinstance(metadata, dict)
        assert metadata["name"] == "SimplePrompt"
        assert metadata["prompt"] == "Simple prompt: {input_text}"
        assert "input_text" in metadata["variable_defaults"]
        assert isinstance(metadata["tags"], list)
        assert isinstance(metadata["tools"], list)

    def test_get_prompt_with_default(self):
        """Test getting prompt with default values."""
        prompt = SimplePrompt()
        result = prompt()
        assert result == "Simple prompt: default text"

    def test_get_prompt_with_custom_value(self):
        """Test getting prompt with custom values."""
        prompt = SimplePrompt()
        result = prompt({"input_text": "custom input"})
        assert result == "Simple prompt: custom input"

    def test_macro_replacement(self):
        """Test that predefined macros are replaced."""
        prompt = PromptWithMacros()
        result = prompt({"user_name": "Alice"})
        assert "Alice" in result
        assert "<<DATETIME>>" not in result

    def test_missing_required_variable(self):
        """Test that missing required variables raise an error."""
        prompt = PromptWithMacros()
        with pytest.raises(ValueError, match="Variable 'user_name' required"):
            prompt({})

    def test_invalid_variable_warning(self, caplog):
        """Test that unknown variables trigger warnings."""
        prompt = SimplePrompt()
        prompt({"invalid_key": "value", "input_text": "test"})
        assert "Unknown variable 'invalid_key'" in caplog.text

    def test_default_version(self):
        """Test that version defaults to '0'."""
        prompt = SimplePrompt()
        assert prompt.version == "0"

    def test_direct_instantiation_with_all_args(self):
        """Test direct instantiation with all parameters."""
        prompt = PromptBase(
            description="Test prompt",
            prompt="Hello {name}",
            variables=["name"],
            variable_defaults={"name": "World"},
            name="TestPrompt",
            version="1.0",
        )
        assert prompt.name == "TestPrompt"
        assert prompt.version == "1.0"
        result = prompt()
        assert result == "Hello World"

    def test_missing_name_with_version_uses_classname(self):
        """Test that missing name uses class name as fallback when version is set."""
        prompt = PromptBase(
            prompt="Hello {name}",
            variables=["name"],
            variable_defaults={"name": "World"},
            version="1.0",
        )
        assert prompt.name == "PromptBase"

    def test_missing_prompt_raises_error(self):
        """Test that missing prompt raises an error."""
        with pytest.raises(ValueError, match="'prompt' must be set for"):
            PromptBase(
                name="TestPrompt",
                version="1.0",
                variables=[],
                variable_defaults={},
            )

    def test_str_method(self):
        """Test __str__ method returns prompt."""
        prompt = SimplePrompt()
        result = str(prompt)
        assert "Simple prompt" in result

    def test_add_macro(self):
        """Test adding macros dynamically."""
        prompt = SimplePrompt()
        prompt.add_macro("<<CUSTOM>>", "custom_value")
        assert "<<CUSTOM>>" in prompt.macros
        assert prompt.macros["<<CUSTOM>>"] == "custom_value"

    def test_add_variable_default(self):
        """Test adding default values for variables."""
        prompt = SimplePrompt()
        prompt.add_variable_default("new_var", "new_default")
        assert "new_var" in prompt.variable_defaults
        assert prompt.variable_defaults["new_var"] == "new_default"

    def test_verbose_mode(self):
        """Test verbose mode can be enabled without errors."""
        class VerbosePrompt(PromptBase):
            def __init__(self):
                super().__init__(verbose=True)

            def set_prompt(self):
                return "Test"

            def set_variable_defaults(self):
                pass

            def set_macros(self):
                pass

            def set_name(self):
                self.name = "VerbosePrompt"

            def set_tools(self):
                pass

        prompt = VerbosePrompt()
        assert prompt.verbose is True
        assert prompt.name == "VerbosePrompt"

    def test_example_field(self):
        """Test that example field is present in metadata."""
        prompt = SimplePrompt()
        metadata = prompt.get_metadata()
        assert "example" in metadata
        assert isinstance(metadata["example"], dict)


class TestPromptBaseVariableExtraction:
    """Test automatic extraction of prompt variables from template."""

    def test_auto_extract_variables_from_prompt(self):
        """Test automatic extraction of variables from prompt."""

        class AutoExtractPrompt(PromptBase):
            def set_prompt(self):
                return "Hello {name}, you are {age} years old."

            def set_variable_defaults(self):
                self.set_variable_defaults_empty()

            def set_macros(self):
                pass

            def set_name(self):
                self.name = "AutoExtractPrompt"

            def set_tools(self):
                pass

        prompt = AutoExtractPrompt()
        assert "name" in prompt.variables
        assert "age" in prompt.variables

    def test_auto_extract_variables_from_system(self):
        """Test automatic extraction of variables from prompt (system-style example)."""

        class AutoExtractSystemPrompt(PromptBase):
            def set_prompt(self):
                return "You are {assistant_type} in {domain}."

            def set_variable_defaults(self):
                self.set_variable_defaults_empty()

            def set_macros(self):
                pass

            def set_name(self):
                self.name = "AutoExtractSystemPrompt"

            def set_tools(self):
                pass

        prompt = AutoExtractSystemPrompt()
        assert "assistant_type" in prompt.variables
        assert "domain" in prompt.variables


class TestPromptBaseValidation:
    """Test validation logic in PromptBase."""

    def test_default_not_in_variables_raises_error(self):
        """Test that defaults not in declared variables raise an error."""

        class InvalidDefaultPrompt(PromptBase):
            def set_prompt(self):
                return "Hello {name}"

            def set_variable_defaults(self):
                # 'age' is not in variables
                self.variable_defaults = {"age": "25"}

            def set_macros(self):
                pass

            def set_name(self):
                self.name = "InvalidDefaultPrompt"

            def set_tools(self):
                pass

        with pytest.raises(ValueError, match="not in variables"):
            InvalidDefaultPrompt()

    def test_invalid_metadata_types_raise_error(self):
        """Test that invalid metadata types raise errors."""

        class InvalidMetadataPrompt(PromptBase):
            def set_prompt(self):
                return "Test"

            def set_variable_defaults(self):
                self.variable_defaults = {}

            def set_macros(self):
                pass

            def set_name(self):
                self.name = "InvalidMetadataPrompt"

            def set_tools(self):
                # should be a list, not a dict
                self.tools = {"invalid": "type"}

        prompt = InvalidMetadataPrompt()
        with pytest.raises(ValueError, match="tools must be of type list"):
            prompt.get_metadata()
