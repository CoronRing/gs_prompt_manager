"""
Tests for the PromptManager class.
"""
import os
import pytest
import tempfile
import shutil
from gs_prompt_manager import PromptManager, PromptBase


class SamplePrompt1(PromptBase):
    """Sample prompt for testing."""

    def set_prompt_chat(self):
        return "This is sample prompt 1: {input}"

    def set_prompt_system(self):
        return ""

    def set_prompt_pieces_available(self):
        self.prompt_pieces_available = ["input"]

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {"input": "default"}

    def set_prompt_predefine_value(self):
        pass

    def set_name(self):
        self.name = "SamplePrompt1"

    def set_tools(self):
        pass

    def set_associated_prompt(self):
        pass


class SamplePrompt2(PromptBase):
    """Another sample prompt for testing."""

    def set_prompt_chat(self):
        return "This is sample prompt 2"

    def set_prompt_system(self):
        return "System prompt for sample 2"

    def set_prompt_pieces_available(self):
        self.prompt_pieces_available = []

    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {}

    def set_prompt_predefine_value(self):
        pass

    def set_name(self):
        self.name = "SamplePrompt2"

    def set_tools(self):
        self.tools = ["tool1", "tool2"]

    def set_associated_prompt(self):
        pass


@pytest.fixture
def temp_prompt_dir():
    """Create a temporary directory with sample prompt files."""
    temp_dir = tempfile.mkdtemp()

    # Create a sample prompt file
    prompt_file = os.path.join(temp_dir, "test_prompt.py")
    with open(prompt_file, "w") as f:
        f.write("""
from gs_prompt_manager import PromptBase

class TempPrompt(PromptBase):
    def set_prompt_chat(self):
        return "Temporary prompt"
    
    def set_prompt_system(self):
        return ""
    
    def set_prompt_pieces_available(self):
        self.prompt_pieces_available = []
    
    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {}
    
    def set_prompt_predefine_value(self):
        pass
    
    def set_name(self):
        self.name = "TempPrompt"
    
    def set_tools(self):
        pass
    
    def set_associated_prompt(self):
        pass
""")

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def multi_prompt_dir():
    """Create a temporary directory with multiple prompt files."""
    temp_dir = tempfile.mkdtemp()

    # Create multiple prompt files
    for i in range(3):
        prompt_file = os.path.join(temp_dir, f"prompt_{i}.py")
        with open(prompt_file, "w") as f:
            f.write(f"""
from gs_prompt_manager import PromptBase

class MultiPrompt{i}(PromptBase):
    def set_prompt_chat(self):
        return "Prompt {i}"
    
    def set_prompt_system(self):
        return ""
    
    def set_prompt_pieces_available(self):
        self.prompt_pieces_available = []
    
    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {{}}
    
    def set_prompt_predefine_value(self):
        pass
    
    def set_name(self):
        self.name = "MultiPrompt{i}"
    
    def set_tools(self):
        pass
    
    def set_associated_prompt(self):
        pass
""")

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


class TestPromptManager:
    """Test suite for PromptManager class."""

    def test_init_with_explicit_path(self, temp_prompt_dir):
        """Test initialization with explicit path."""
        manager = PromptManager(prompt_paths=temp_prompt_dir)
        assert len(manager.get_prompt_names()) > 0
        assert "TempPrompt" in manager.get_prompt_names()

    def test_init_with_list_of_paths(self, temp_prompt_dir, multi_prompt_dir):
        """Test initialization with multiple paths."""
        manager = PromptManager(prompt_paths=[temp_prompt_dir, multi_prompt_dir])
        prompt_names = manager.get_prompt_names()

        assert "TempPrompt" in prompt_names
        assert "MultiPrompt0" in prompt_names
        assert "MultiPrompt1" in prompt_names
        assert "MultiPrompt2" in prompt_names

    def test_get_prompt_by_name(self, temp_prompt_dir):
        """Test retrieving a prompt by name."""
        manager = PromptManager(prompt_paths=temp_prompt_dir)
        prompt = manager.get_prompt("TempPrompt")

        assert isinstance(prompt, PromptBase)
        assert prompt.name == "TempPrompt"

    def test_get_prompt_not_found_raises_error(self, temp_prompt_dir):
        """Test that getting a non-existent prompt raises an error."""
        manager = PromptManager(prompt_paths=temp_prompt_dir)

        with pytest.raises(ValueError, match="Prompt 'NonExistent' not found"):
            manager.get_prompt("NonExistent")

    def test_get_prompt_names(self, multi_prompt_dir):
        """Test getting all prompt names."""
        manager = PromptManager(prompt_paths=multi_prompt_dir)
        names = manager.get_prompt_names()

        assert isinstance(names, list)
        assert len(names) == 3
        assert "MultiPrompt0" in names
        assert "MultiPrompt1" in names
        assert "MultiPrompt2" in names

    def test_get_prompt_instances(self, temp_prompt_dir):
        """Test getting all prompt instances."""
        manager = PromptManager(prompt_paths=temp_prompt_dir)
        instances = manager.get_prompt_instances()

        assert isinstance(instances, dict)
        assert "TempPrompt" in instances
        assert isinstance(instances["TempPrompt"], PromptBase)

    def test_verbose_mode(self, temp_prompt_dir, caplog):
        """Test verbose mode produces log messages."""
        import logging

        with caplog.at_level(logging.INFO):
            _ = PromptManager(prompt_paths=temp_prompt_dir, verbose=True)
            assert "PromptManager: Loaded" in caplog.text

    def test_invalid_path_raises_error(self):
        """Test that an invalid path raises an error."""
        with pytest.raises(ValueError, match="not a directory"):
            PromptManager(prompt_paths="/nonexistent/path")

    def test_empty_directory(self):
        """Test initialization with empty directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = PromptManager(prompt_paths=temp_dir)
            assert len(manager.get_prompt_names()) == 0
        finally:
            shutil.rmtree(temp_dir)

    def test_directory_with_non_prompt_files(self):
        """Test that non-prompt Python files are ignored."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create a Python file that doesn't contain a PromptBase subclass
            non_prompt_file = os.path.join(temp_dir, "not_a_prompt.py")
            with open(non_prompt_file, "w") as f:
                f.write("""
def some_function():
    return "Not a prompt"
""")

            manager = PromptManager(prompt_paths=temp_dir)
            assert len(manager.get_prompt_names()) == 0
        finally:
            shutil.rmtree(temp_dir)

    def test_search_available_prompts_static_method(self, temp_prompt_dir):
        """Test the search_available_prompts static method."""
        found_prompts = PromptManager.search_available_prompts(temp_prompt_dir)

        assert isinstance(found_prompts, dict)
        assert "TempPrompt" in found_prompts
        assert issubclass(found_prompts["TempPrompt"], PromptBase)

    def test_get_all_prompt_metadata_static_method(self):
        """Test the get_all_prompt_metadata static method."""
        prompts_dict = {
            "SamplePrompt1": SamplePrompt1,
            "SamplePrompt2": SamplePrompt2,
        }

        metadata = PromptManager.get_all_prompt_metadata(prompts_dict)

        assert isinstance(metadata, dict)
        assert "SamplePrompt1" in metadata
        assert "SamplePrompt2" in metadata
        assert metadata["SamplePrompt1"]["name"] == "SamplePrompt1"
        assert "tool1" in metadata["SamplePrompt2"]["tools"]

    def test_init_with_default_path(self):
        """Test initialization with default path (caller's directory)."""
        # This test uses the actual test directory
        _ = PromptManager()
        # Should find prompts in the caller's directory (test/sample_prompts)
        # The actual behavior depends on where this is called from

    def test_duplicate_prompt_names_warning(self, caplog):
        """Test that duplicate prompt names trigger warnings."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create two files with the same class name
            for i in range(2):
                prompt_file = os.path.join(temp_dir, f"duplicate_{i}.py")
                with open(prompt_file, "w") as f:
                    f.write("""
from gs_prompt_manager import PromptBase

class DuplicatePrompt(PromptBase):
    def set_prompt_chat(self):
        return "Duplicate"
    
    def set_prompt_system(self):
        return ""
    
    def set_prompt_pieces_available(self):
        self.prompt_pieces_available = []
    
    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {}
    
    def set_prompt_predefine_value(self):
        pass
    
    def set_name(self):
        self.name = "DuplicatePrompt"
    
    def set_tools(self):
        pass
    
    def set_associated_prompt(self):
        pass
""")

            import logging

            with caplog.at_level(logging.WARNING):
                _ = PromptManager(prompt_paths=temp_dir)
                # Should have a warning about duplicate
                assert any("Duplicate" in record.message for record in caplog.records)
        finally:
            shutil.rmtree(temp_dir)

    def test_nested_directories(self):
        """Test that prompts in nested directories are found."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create nested directory structure
            nested_dir = os.path.join(temp_dir, "subdir", "nested")
            os.makedirs(nested_dir)

            prompt_file = os.path.join(nested_dir, "nested_prompt.py")
            with open(prompt_file, "w") as f:
                f.write("""
from gs_prompt_manager import PromptBase

class NestedPrompt(PromptBase):
    def set_prompt_chat(self):
        return "Nested prompt"
    
    def set_prompt_system(self):
        return ""
    
    def set_prompt_pieces_available(self):
        self.prompt_pieces_available = []
    
    def set_prompt_pieces_default_value(self):
        self.prompt_pieces_default_value = {}
    
    def set_prompt_predefine_value(self):
        pass
    
    def set_name(self):
        self.name = "NestedPrompt"
    
    def set_tools(self):
        pass
    
    def set_associated_prompt(self):
        pass
""")

            manager = PromptManager(prompt_paths=temp_dir)
            assert "NestedPrompt" in manager.get_prompt_names()
        finally:
            shutil.rmtree(temp_dir)

    def test_init_file_is_ignored(self):
        """Test that __init__.py files are not processed."""
        temp_dir = tempfile.mkdtemp()
        try:
            init_file = os.path.join(temp_dir, "__init__.py")
            with open(init_file, "w") as f:
                f.write("""
from gs_prompt_manager import PromptBase

class InitPrompt(PromptBase):
    # This should not be loaded
    pass
""")

            manager = PromptManager(prompt_paths=temp_dir)
            # __init__.py should be skipped
            assert "InitPrompt" not in manager.get_prompt_names()
        finally:
            shutil.rmtree(temp_dir)


class TestPromptManagerIntegration:
    """Integration tests for PromptManager with real prompt directory."""

    def test_load_sample_prompts(self):
        """Test loading the actual sample_prompts directory."""
        # Get the path to the sample_prompts directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sample_prompts_dir = os.path.join(current_dir, "sample_prompts")

        if os.path.exists(sample_prompts_dir):
            manager = PromptManager(prompt_paths=sample_prompts_dir)
            assert "PromptHelloWorld" in manager.get_prompt_names()

            prompt = manager.get_prompt("PromptHelloWorld")
            result = prompt.get_prompt_chat()
            assert result == "Hello, World!"
