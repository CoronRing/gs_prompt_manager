from gs_prompt_manager import PromptBase


class ToneSystem(PromptBase):
    """Tone instructions, kept apart so any agent can borrow them."""

    def set_prompt(self):
        return "Write in a {register} register. Never exceed {max_words} words."

    def set_variable_defaults(self):
        self.variable_defaults = {"register": "plain", "max_words": 200}

    def set_name(self):
        self.name = "ToneSystem"
