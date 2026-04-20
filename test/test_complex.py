from gs_prompt_manager import PromptManager

def test_complex_prompt():
    # Create a PromptManager instance
    prompt_manager = PromptManager("test/sample_prompts")
    chat_prompt = prompt_manager.get_prompt("PromptHelloWorld")
    system_prompt = prompt_manager.get_prompt("PromptHelloWorldSystem")

    # Generate the chat prompt and system prompt
    chat_result = chat_prompt({"world": "World"})
    system_result = system_prompt({"name": "Alice"})

    # Assert that the generated prompts are correct
    assert chat_result == "Hello World", f"Expected 'Hello World', got '{chat_result}'"
    assert system_result == "Hello Alice", f"Expected 'Hello Alice', got '{system_result}'"