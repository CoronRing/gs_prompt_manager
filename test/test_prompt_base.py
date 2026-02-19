"""
Tests for the PromptBase class.
"""
import pytest
import datetime
from gs_prompt_manager import PromptBase


class SimplePrompt(PromptBase):
    """A minimal prompt for testing."""

    def set_prompt_chat(self):
        return "Simple prompt: {input_text}"

    def set_prompt_system(self):
        return "You are a helpful assistant."

    def set_prompt_pieces_available(self):
        self.prompt_pieces_available = ["input_text"]

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

    def set_associated_prompt(self):
        self.associated_prompt = {}


class PromptWithMacros(PromptBase):
    """A prompt with predefined macros."""

    def set_prompt_chat(self):
        return "Date: <<DATETIME>>, User: {user_name}"

    def set_prompt_system(self):
        return ""

    def set_prompt_pieces_available(self):
        self.prompt_pieces_available = ["user_name"]

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

    def set_associated_prompt(self):
        self.associated_prompt = {}


class TestPromptBase:
    """Test suite for PromptBase class."""

    def test_basic_instantiation(self):
        """Test that a simple prompt can be instantiated."""
        prompt = SimplePrompt()
        assert prompt.name == "SimplePrompt"
        assert prompt.prompt_chat == "Simple prompt: {input_text}"
        assert prompt.prompt_system == "You are a helpful assistant."

    def test_get_metadata(self):
        """Test metadata retrieval."""
        prompt = SimplePrompt()
        metadata = prompt.get_metadata()

        assert isinstance(metadata, dict)
        assert metadata["name"] == "SimplePrompt"
        assert metadata["prompt_chat"] == "Simple prompt: {input_text}"
        assert metadata["prompt_system"] == "You are a helpful assistant."
        assert "input_text" in metadata["default_prompt_pieces"]
        assert isinstance(metadata["tags"], list)
        assert isinstance(metadata["tools"], list)

    def test_get_prompt_chat_with_default(self):
        """Test getting prompt chat with default values."""
        prompt = SimplePrompt()
        result = prompt.get_prompt_chat()
        assert result == "Simple prompt: default text"

    def test_get_prompt_chat_with_custom_value(self):
        """Test getting prompt chat with custom values."""
        prompt = SimplePrompt()
        result = prompt.get_prompt_chat({"input_text": "custom input"})
        assert result == "Simple prompt: custom input"

    def test_get_prompt_system(self):
        """Test getting prompt system."""
        prompt = SimplePrompt()
        result = prompt.get_prompt_system()
        assert result == "You are a helpful assistant."

    def test_macro_replacement(self):
        """Test that predefined macros are replaced."""
        prompt = PromptWithMacros()
        result = prompt.get_prompt_chat({"user_name": "Alice"})
        assert "Alice" in result
        assert "<<DATETIME>>" not in result

    def test_missing_required_piece(self):
        """Test that missing required pieces raise an error."""
        prompt = PromptWithMacros()
        with pytest.raises(ValueError, match="Prompt piece 'user_name' required"):
            prompt.get_prompt_chat({})

    def test_invalid_piece_warning(self, caplog):
        """Test that invalid pieces trigger warnings."""
        prompt = SimplePrompt()
        prompt.get_prompt_chat({"invalid_key": "value", "input_text": "test"})
        assert "Unknown piece 'invalid_key'" in caplog.text

    def test_default_version(self):
        """Test that version defaults to '0'."""
        prompt = SimplePrompt()
        assert prompt.version == "0"

    def test_direct_instantiation_with_all_args(self):
        """Test direct instantiation with all parameters."""
        prompt = PromptBase(
            description="Test prompt",
            prompt_chat="Hello {name}",
            prompt_pieces_available=["name"],
            prompt_pieces_default_value={"name": "World"},
            name="TestPrompt",
            version="1.0",
        )
        assert prompt.name == "TestPrompt"
        assert prompt.version == "1.0"
        result = prompt.get_prompt_chat()
        assert result == "Hello World"

    def test_missing_name_with_version_uses_classname(self):
        """Test that missing name uses class name as fallback when version is set."""
        prompt = PromptBase(
            prompt_chat="Hello {name}",
            prompt_pieces_available=["name"],
            prompt_pieces_default_value={"name": "World"},
            version="1.0",
        )
        # Name should default to class name
        assert prompt.name == "PromptBase"

    def test_missing_both_prompts_raises_error(self):
        """Test that missing both chat and system prompts raises an error."""
        with pytest.raises(
            ValueError, match="At least one of 'prompt_chat' or 'prompt_system'"
        ):
            PromptBase(
                name="TestPrompt",
                version="1.0",
                prompt_pieces_available=[],
                prompt_pieces_default_value={},
            )

    def test_str_method(self):
        """Test __str__ method returns prompt_chat."""
        prompt = SimplePrompt()
        result = str(prompt)
        assert result == "Simple prompt: default text"

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

            def set_prompt_chat(self):
                return "Test"

            def set_prompt_system(self):
                return ""

            def set_prompt_pieces_available(self):
                pass

            def set_prompt_pieces_default_value(self):
                pass

            def set_prompt_predefine_value(self):
                pass

            def set_name(self):
                self.name = "VerbosePrompt"

            def set_tools(self):
                pass

            def set_associated_prompt(self):
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

    def test_auto_extract_pieces_from_chat(self):
        """Test automatic extraction of pieces from prompt_chat."""

        class AutoExtractPrompt(PromptBase):
            def set_prompt_chat(self):
                return "Hello {name}, you are {age} years old."

            def set_prompt_system(self):
                return ""

            def set_prompt_pieces_available(self):
                # Let parent class extract automatically
                super().set_prompt_pieces_available()

            def set_prompt_pieces_default_value(self):
                self.set_prompt_pieces_default_value_empty()

            def set_prompt_predefine_value(self):
                pass

            def set_name(self):
                self.name = "AutoExtractPrompt"

            def set_tools(self):
                pass

            def set_associated_prompt(self):
                pass

        prompt = AutoExtractPrompt()
        assert "name" in prompt.prompt_pieces_available
        assert "age" in prompt.prompt_pieces_available

    def test_auto_extract_pieces_from_system(self):
        """Test automatic extraction of pieces from prompt_system."""

        class AutoExtractSystemPrompt(PromptBase):
            def set_prompt_chat(self):
                return "User message"

            def set_prompt_system(self):
                return "You are {assistant_type} in {domain}."

            def set_prompt_pieces_available(self):
                super().set_prompt_pieces_available()

            def set_prompt_pieces_default_value(self):
                self.set_prompt_pieces_default_value_empty()

            def set_prompt_predefine_value(self):
                pass

            def set_name(self):
                self.name = "AutoExtractSystemPrompt"

            def set_tools(self):
                pass

            def set_associated_prompt(self):
                pass

        prompt = AutoExtractSystemPrompt()
        assert "assistant_type" in prompt.prompt_pieces_available
        assert "domain" in prompt.prompt_pieces_available


class TestPromptBaseValidation:
    """Test validation logic in PromptBase."""

    def test_default_not_in_available_raises_error(self):
        """Test that defaults not in available pieces raise an error."""

        class InvalidDefaultPrompt(PromptBase):
            def set_prompt_chat(self):
                return "Hello {name}"

            def set_prompt_system(self):
                return ""

            def set_prompt_pieces_available(self):
                self.prompt_pieces_available = ["name"]

            def set_prompt_pieces_default_value(self):
                # This is invalid - 'age' is not in available pieces
                self.prompt_pieces_default_value = {"age": "25"}

            def set_prompt_predefine_value(self):
                pass

            def set_name(self):
                self.name = "InvalidDefaultPrompt"

            def set_tools(self):
                pass

            def set_associated_prompt(self):
                pass

        with pytest.raises(ValueError, match="not in prompt_pieces_available"):
            InvalidDefaultPrompt()

    def test_invalid_metadata_types_raise_error(self):
        """Test that invalid metadata types raise errors."""

        class InvalidMetadataPrompt(PromptBase):
            def set_prompt_chat(self):
                return "Test"

            def set_prompt_system(self):
                return ""

            def set_prompt_pieces_available(self):
                self.prompt_pieces_available = []

            def set_prompt_pieces_default_value(self):
                self.prompt_pieces_default_value = {}

            def set_prompt_predefine_value(self):
                pass

            def set_name(self):
                self.name = "InvalidMetadataPrompt"

            def set_tools(self):
                # This should be a list, not a dict
                self.tools = {"invalid": "type"}

            def set_associated_prompt(self):
                pass

        prompt = InvalidMetadataPrompt()
        with pytest.raises(ValueError, match="tools must be of type list"):
            prompt.get_metadata()
