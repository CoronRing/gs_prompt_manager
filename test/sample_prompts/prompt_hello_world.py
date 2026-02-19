from gs_prompt_manager import PromptBase

class PromptHelloWorld(PromptBase):
    """
    A simple prompt that returns "Hello, World!".
    """

    def set_prompt_chat(self) -> str:
        """
        Generate the prompt string.

        Returns:
            str: The prompt string "Hello, World!".
        """
        return "Hello, World!"
    