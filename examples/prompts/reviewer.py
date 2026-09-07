from gs_prompt_manager import PromptBase, prompt_group


class ReviewerSystem(PromptBase):
    """System prompt for the code reviewer."""

    def set_prompt(self):
        return (
            "You are a senior {language} reviewer.\n"
            "Focus on correctness first, style last.\n"
            "Session started <<DATETIME>>."
        )

    def set_variable_defaults(self):
        self.variable_defaults = {"language": "Python"}


class ReviewerChat(PromptBase):
    def set_prompt(self):
        return "Review this diff:\n\n{diff}"


@prompt_group("Reviewer", "verdict")
class ReviewerFinalCall(PromptBase):
    def set_prompt(self):
        return "Answer with exactly one word: {options}."

    def set_variable_defaults(self):
        self.variable_defaults = {"options": "approve or reject"}
