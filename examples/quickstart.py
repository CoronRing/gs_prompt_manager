"""Runnable version of the tour in the README.

    python examples/quickstart.py
"""

import os

from gs_prompt_manager import PromptManager

PROMPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")


def main() -> None:
    manager = PromptManager(PROMPTS)

    print("groups:", manager.get_prompt_group_names())
    print("Reviewer keys:", manager.Reviewer.get_prompt_names())
    print("Tone keys:", manager.Tone.get_prompt_names())

    print("\n--- Reviewer.system, language overridden ---")
    print(manager.Reviewer.system({"language": "Rust"}))

    print("\n--- Reviewer.verdict, all defaults ---")
    print(manager.Reviewer.verdict())

    print("\n--- Tone.system, one override ---")
    print(manager.Tone.system({"max_words": 40}))

    print("\n--- a missing variable is caught before the API call ---")
    try:
        manager.Reviewer.chat()
    except ValueError as exc:
        print(f"ValueError: {exc}")

    print("\n--- metadata travels with the prompt ---")
    print(manager.Reviewer.system.get_metadata()["variable_defaults"])


if __name__ == "__main__":
    main()
