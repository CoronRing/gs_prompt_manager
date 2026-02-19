"""
Pytest configuration and shared fixtures for gs_prompt_manager tests.
"""
import pytest
import logging


@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@pytest.fixture
def sample_prompt_pieces():
    """Provide sample prompt pieces for testing."""
    return {
        "input_text": "This is a test input",
        "user_name": "TestUser",
        "context": "Test context",
    }


@pytest.fixture
def sample_metadata():
    """Provide sample metadata for testing."""
    return {
        "name": "TestPrompt",
        "version": "1.0",
        "author": "Test Author",
        "description": "A test prompt",
        "tags": ["test", "sample"],
    }
