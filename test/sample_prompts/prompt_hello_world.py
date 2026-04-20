from gs_prompt_manager import PromptBase

class PromptHelloWorld(PromptBase):
    """
    Chat variant: says hello to the provided `world` piece.
    """

    def set_prompt(self) -> str:
        return "Hello {world}"


class PromptHelloWorldSystem(PromptBase):
    """
    System variant: says hello to the provided `name` piece.
    """

    def set_prompt(self) -> str:
        return "Hello {name}"
    