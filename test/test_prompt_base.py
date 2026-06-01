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

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {"input_text": "default text"}

    def set_prompt_predefine_value(self):
        self.prompt_predefine_value = {
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

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {}

    def set_prompt_predefine_value(self):
        self.prompt_predefine_value = {
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
        assert "input_text" in metadata["default_prompt_pieces"]
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

    def test_missing_required_piece(self):
        """Test that missing required pieces raise an error."""
        prompt = PromptWithMacros()
        with pytest.raises(ValueError, match="Prompt piece 'user_name' required"):
            prompt({})

    def test_invalid_piece_warning(self, caplog):
        """Test that invalid pieces trigger warnings."""
        prompt = SimplePrompt()
        prompt({"invalid_key": "value", "input_text": "test"})
        assert "Unknown piece 'invalid_key'" in caplog.text

    def test_default_version(self):
        """Test that version defaults to '0'."""
        prompt = SimplePrompt()
        assert prompt.version == "0"

    def test_direct_instantiation_with_all_args(self):
        """Test direct instantiation with all parameters."""
        prompt = PromptBase(
            description="Test prompt",
            prompt="Hello {name}",
            prompt_pieces_available=["name"],
            prompt_pieces_default_value={"name": "World"},
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
            prompt_pieces_available=["name"],
            prompt_pieces_default_value={"name": "World"},
            version="1.0",
        )
        # Name should default to class name
        assert prompt.name == "PromptBase"

    def test_missing_prompt_raises_error(self):
        """Test that missing prompt raises an error."""
        with pytest.raises(ValueError, match="'prompt' must be set for"):
            PromptBase(
                name="TestPrompt",
                version="1.0",
                prompt_pieces_available=[],
                prompt_pieces_default_value={},
            )

    def test_str_method(self):
        """Test __str__ method returns prompt."""
        prompt = SimplePrompt()
        result = str(prompt)
        assert "Simple prompt" in result

    def test_add_prompt_predefine_value(self):
        """Test adding predefined values dynamically."""
        prompt = SimplePrompt()
        prompt.add_prompt_predefine_value("<<CUSTOM>>", "custom_value")
        assert "<<CUSTOM>>" in prompt.prompt_predefine_value
        assert prompt.prompt_predefine_value["<<CUSTOM>>"] == "custom_value"

    def test_add_prompt_piece_default_value(self):
        """Test adding default values for prompt pieces."""
        prompt = SimplePrompt()
        prompt.add_prompt_piece_default_value("new_piece", "new_default")
        assert "new_piece" in prompt.prompt_pieces_default_value
        assert prompt.prompt_pieces_default_value["new_piece"] == "new_default"

    def test_verbose_mode(self):
        """Test verbose mode can be enabled without errors."""
        class VerbosePrompt(PromptBase):
            def __init__(self):
                super().__init__(verbose=True)

            def set_prompt(self):
                return "Test"


            def set_prompt_pieces_default_value(self):
                pass

            def set_prompt_predefine_value(self):
                pass

            def set_name(self):
                self.name = "VerbosePrompt"

            def set_tools(self):
                pass

        prompt = VerbosePrompt()
        # Should work without errors
        assert prompt.verbose is True
        assert prompt.name == "VerbosePrompt"

    def test_example_field(self):
        """Test that example field is present in metadata."""
        prompt = SimplePrompt()
        metadata = prompt.get_metadata()
        assert "example" in metadata
        assert isinstance(metadata["example"], dict)


class TestPromptBasePieceExtraction:
    """Test automatic extraction of prompt pieces from template."""

    def test_auto_extract_pieces_from_prompt(self):
        """Test automatic extraction of pieces from prompt."""

        class AutoExtractPrompt(PromptBase):
            def set_prompt(self):
                return "Hello {name}, you are {age} years old."


            def set_prompt_pieces_default_value(self):
                self.set_prompt_pieces_default_value_empty()

            def set_prompt_predefine_value(self):
                pass

            def set_name(self):
                self.name = "AutoExtractPrompt"

            def set_tools(self):
                pass

        prompt = AutoExtractPrompt()
        assert "name" in prompt.prompt_pieces_available
        assert "age" in prompt.prompt_pieces_available

    def test_auto_extract_pieces_from_system(self):
        """Test automatic extraction of pieces from prompt (system-style example)."""

        class AutoExtractSystemPrompt(PromptBase):
            def set_prompt(self):
                return "You are {assistant_type} in {domain}."
            
            def set_prompt_pieces_default_value(self):
                self.set_prompt_pieces_default_value_empty()

            def set_prompt_predefine_value(self):
                pass

            def set_name(self):
                self.name = "AutoExtractSystemPrompt"

            def set_tools(self):
                pass

        prompt = AutoExtractSystemPrompt()
        assert "assistant_type" in prompt.prompt_pieces_available
        assert "domain" in prompt.prompt_pieces_available


class TestPromptBaseValidation:
    """Test validation logic in PromptBase."""

    def test_default_not_in_available_raises_error(self):
        """Test that defaults not in available pieces raise an error."""

        class InvalidDefaultPrompt(PromptBase):
            def set_prompt(self):
                return "Hello {name}"


            def set_prompt_pieces_default_value(self):
                # This is invalid - 'age' is not in available pieces
                self.prompt_pieces_default_value = {"age": "25"}

            def set_prompt_predefine_value(self):
                pass

            def set_name(self):
                self.name = "InvalidDefaultPrompt"

            def set_tools(self):
                pass

        with pytest.raises(ValueError, match="not in prompt_pieces_available"):
            InvalidDefaultPrompt()

    def test_invalid_metadata_types_raise_error(self):
        """Test that invalid metadata types raise errors."""

        class InvalidMetadataPrompt(PromptBase):
            def set_prompt(self):
                return "Test"


            def set_prompt_pieces_default_value(self):
                self.prompt_pieces_default_value = {}

            def set_prompt_predefine_value(self):
                pass

            def set_name(self):
                self.name = "InvalidMetadataPrompt"

            def set_tools(self):
                # This should be a list, not a dict
                self.tools = {"invalid": "type"}

        prompt = InvalidMetadataPrompt()
        with pytest.raises(ValueError, match="tools must be of type list"):
            prompt.get_metadata()
