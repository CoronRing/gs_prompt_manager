import regex
import logging
from abc import abstractmethod
import datetime

logger = logging.getLogger(__name__)


class PromptBase:
    """
    Abstract base class for prompt templates, enforcing custom creation via several sub-methods.
    Child classes must implement the set_* methods that initialize key members and metadata.
    Instantiation directly is possible (with all args), but discouraged in favor of subclassing.
    """

    def __init__(
        self,
        description: str = "",
        description_long: str = "",
        prompt: str = "",
        prompt_pieces_available: list = None,
        prompt_pieces_default_value: dict = None,
        prompt_predefine_value: dict = None,
        name: str = "",
        tags: list = None,
        author: str = "",
        version: str = "",
        timestamp: str = "",
        tools: list = None,
        expected_config: dict = None,
        example: dict = None,
        verbose: bool = False,
    ):
        self.verbose = verbose

        # Instance field setup with safe defaults
        self.description = description
        self.description_long = description_long

        self.prompt = prompt
        self.prompt_pieces_available = (
            prompt_pieces_available if prompt_pieces_available is not None else []
        )
        self.prompt_pieces_default_value = (
            prompt_pieces_default_value
            if prompt_pieces_default_value is not None
            else {}
        )
        self.prompt_predefine_value = (
            prompt_predefine_value if prompt_predefine_value is not None else {}
        )

        self.name = name
        self.tags = tags if tags is not None else []
        self.author = author
        self.version = version or "0"
        self.timestamp = timestamp
        self.tools = tools if tools is not None else []
        self.expected_config = expected_config if expected_config is not None else {}
        self.example = (
            example
            if example is not None
            else {"sample_piece": "", "sample_response": ""}
        )

        self.associated_prompt = {}
        self.associated_prompt_names = []

        # Delegate to subclass "set_*" logic if not given in init
        self.set_tools()
        self.set_associated_prompt()
        self.associated_prompt_names = list(self.associated_prompt.keys())

        if not self.prompt:
            set_val = self.set_prompt()
            if set_val:
                self.prompt = set_val

        if not self.name:
            set_val = self.set_name()
            if set_val:
                self.name = set_val

        if not self.prompt_pieces_available:
            set_val = self.set_prompt_pieces_available()
            if set_val:
                self.prompt_pieces_available = set_val

        if not self.prompt_pieces_default_value:
            set_val = self.set_prompt_pieces_default_value()
            if set_val:
                self.prompt_pieces_default_value = set_val

        if not self.prompt_predefine_value:
            set_val = self.set_prompt_predefine_value()
            if set_val:
                self.prompt_predefine_value = set_val

        # Post-processing and required validation
        self._check_default_prompt_pieces()
        self._check_required_fields()

    ###### Abstract set_* methods for subclass implementation #######

    @abstractmethod
    def set_prompt(self):
        """
        Subclass defines self.prompt (template str).
        """
        pass
    
    @abstractmethod
    def set_prompt_predefine_value(self):
        """
        Subclass defines self.prompt_predefine_value (dict with keys to replace in prompt).
        """
        return {
            "<<DATETIME>>": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
    def add_prompt_predefine_value(self, key: str, value: str):
        """
        Add a predefine macro key-value pair.
        """
        self.prompt_predefine_value[key] = value

    @abstractmethod
    def set_prompt_pieces_default_value(self):
        """
        Subclass defines self.prompt_pieces_default_value (dict with defaults for prompt pieces).
        """
        for piece in self.prompt_pieces_available:
            if piece not in self.prompt_pieces_default_value:
                if self.verbose:
                    logger.warning(
                        f"Default for '{piece}' not set in class, consider using `set_prompt_pieces_default_value_empty`"
                    )
        pass

    def add_prompt_piece_default_value(self, piece: str, default_value: str):
        """
        Add a default value for a specific prompt piece.
        """
        self.prompt_pieces_default_value[piece] = default_value

    def set_prompt_pieces_default_value_empty(self):
        for piece in self.prompt_pieces_available:
            if piece not in self.prompt_pieces_default_value:
                self.prompt_pieces_default_value[piece] = ""
                if self.verbose:
                    logger.warning(
                        f"Default for '{piece}' not set in class '{self.name}'; using empty string."
                    )

    @abstractmethod
    def set_prompt_pieces_available(self):
        """
        Subclass defines self.prompt_pieces_available as a list.
        Default: extract {key} names from prompt.
        """
        try:
            self.prompt_pieces_available = regex.findall(r"\{(.*?)\}", self.prompt)
        except Exception as e:
            logger.error(
                (
                    f"Error extracting prompt pieces from prompt in class '{self.name}':\n",
                    f"Prompt: {self.prompt}",
                    f"Exception: {e}",
                )
            )
            raise e
        if self.verbose:
            logger.info(f"Pieces for {self.name}: {self.prompt_pieces_available}")

    @abstractmethod
    def set_name(self):
        """
        Subclass sets self.name. Default: class name.
        """
        self.name = self.__class__.__name__
        if self.verbose:
            logger.info(f"No name set; using class name: {self.name}")

    @abstractmethod
    def set_tools(self):
        """
        Subclass sets self.tools (identifiers of allowed tools).
        """
        self.tools = []

    @abstractmethod
    def set_associated_prompt(self):
        """
        Subclass sets .associated_prompt (other PromptBase instances by key).
        """
        self.associated_prompt = {}

    ###### Validation logic #######

    def _check_default_prompt_pieces(self):
        """
        Ensure default/available prompt pieces coverage and validity.
        """

        # Error if anything in defaults isn't in allowed
        for key in self.prompt_pieces_default_value.keys():
            if key not in self.prompt_pieces_available:
                raise ValueError(
                    f"Prompt piece '{key}' in defaults, but not in prompt_pieces_available. Allowed: {self.prompt_pieces_available}"
                )

    def _check_required_fields(self):
        """
        Ensure all mandatory fields are set.
        """
        for param in ["name", "version"]:
            val = getattr(self, param)
            if not val:
                raise ValueError(
                    f"Required parameter '{param}' not set for '{type(self).__name__}'."
                )
        if not self.prompt:
            raise ValueError(f"'prompt' must be set for '{self.name}'.")

    ###### API #######

    def get_metadata(self) -> dict:
        """
        Return a (JSON serializable) dictionary describing this PromptBase.
        """
        # Validate types
        for attr, expected in [
            ("expected_config", dict),
            ("example", dict),
            ("tags", list),
            ("tools", list),
            ("associated_prompt", dict),
        ]:
            if not isinstance(getattr(self, attr), expected):
                raise ValueError(
                    f"{attr} must be of type {expected.__name__} for '{self.name}'."
                )

        return {
            "prompt": self.prompt,
            "description": self.description,
            "description_long": self.description_long,
            "name": self.name,
            "default_prompt_pieces": self.prompt_pieces_default_value,
            "predefine_prompt_pieces": self.prompt_predefine_value,
            "tags": self.tags,
            "author": self.author,
            "version": self.version,
            "timestamp": self.timestamp,
            "tools": self.tools,
            "expected_config": self.expected_config,
            "example": self.example,
            "associated_prompt_names": list(self.associated_prompt.keys()),
        }

    def _get_prompt(
        self, base: str, prompt_pieces: dict = None, no_warning: bool = False
    ) -> str:
        """
        Fill the prompt string's placeholders with provided (or default) prompt_pieces and predef macros.
        """
        prompt_pieces = prompt_pieces or {}

        # Validate prompt input keys
        for key in prompt_pieces:
            if key not in self.prompt_pieces_available:
                error_message = (
                    f"Unknown piece '{key}' in prompt input for {self.name}. \n"
                    f"Allowed: {list(self.prompt_pieces_available)}"
                )
                logger.warning(
                    error_message,
                )

        result = base

        # Substitute all {var}
        for key in self.prompt_pieces_available:
            if key in prompt_pieces and prompt_pieces[key] is not None:
                value = str(prompt_pieces[key])
            elif (
                key in self.prompt_pieces_default_value
                and self.prompt_pieces_default_value[key] is not None
            ):
                value = str(self.prompt_pieces_default_value[key])
            else:
                error_message = f"Prompt piece '{key}' required in prompt input for {self.name}; none given and no default."

                logger.error(error_message, exc_info=True)
                raise ValueError(error_message)
            result = result.replace(f"{{{key}}}", value)

        # Substitute all <<VAR>>
        for key, v in self.prompt_predefine_value.items():
            result = result.replace(key, str(v))

        # Warn about remaining <<VAR>>
        if not no_warning:
            for unmatched in regex.findall(r"<<(.*?)>>", result):
                if f"<<{unmatched}>>" not in self.prompt_predefine_value:
                    logger.warning(
                        f"Unresolved macro '<<{unmatched}>>' in rendered prompt for {self.name}."
                    )
        return result

    def get_prompt(self, prompt_pieces: dict = None, no_warning: bool = False) -> str:
        """
        Get the filled prompt string with provided (or default) prompt_pieces and predef macros.
        """
        return self._get_prompt(self.prompt, prompt_pieces, no_warning=no_warning)

    def __str__(self) -> str:
        # return raw, if default exist, insert, if required, leave as is ie {item}
        # Start from the raw template
        result = self.prompt

        # Insert any available default values; leave required placeholders unchanged
        for key in self.prompt_pieces_available:
            if (
                key in self.prompt_pieces_default_value
                and self.prompt_pieces_default_value[key] is not None
            ):
                result = result.replace(f"{{{key}}}", str(self.prompt_pieces_default_value[key]))

        # Substitute predefined macros like <<DATETIME>> when available
        for key, v in (self.prompt_predefine_value or {}).items():
            result = result.replace(key, str(v))

        return result

    def __call__(self, prompt_pieces: dict = None, no_warning: bool = False) -> str:
        """
        Allow prompt instances to be called like a function to render the prompt.
        Example: prompt = manager.get_prompt('X'); result = prompt({'var':'value'})
        """
        return self.get_prompt(prompt_pieces, no_warning=no_warning)
    @staticmethod
    def _escape_braces(line: str) -> str:
        """
        Make unmatched { or } into double braces for safe formatting.
        """
        # Replace single {, unless already part of {{
        escaped = regex.sub(r"(?<!{){(?!{)", "{{", line)
        escaped = regex.sub(r"(?<!})}(?!})", "}}", escaped)
        return escaped

    ###### Example MVP usage/test #######
    # This part can be removed in production modules
