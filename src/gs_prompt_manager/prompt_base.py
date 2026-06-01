import regex
import logging
from abc import abstractmethod
from typing import Optional
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
        variables: Optional[list] = None,
        variable_defaults: Optional[dict] = None,
        macros: Optional[dict] = None,
        name: str = "",
        tags: Optional[list] = None,
        author: str = "",
        version: str = "",
        timestamp: str = "",
        tools: Optional[list] = None,
        expected_config: Optional[dict] = None,
        example: Optional[dict] = None,
        verbose: bool = False,
    ):
        self.verbose = verbose

        self.description = description
        self.description_long = description_long

        self.prompt = prompt
        self.variables = variables if variables is not None else []
        self.variable_defaults = variable_defaults if variable_defaults is not None else {}
        self.macros = macros if macros is not None else {}

        self.name = name
        self.tags = tags if tags is not None else []
        self.author = author
        self.version = version or "0"
        self.timestamp = timestamp
        self.tools = tools if tools is not None else []
        self.expected_config = expected_config if expected_config is not None else {}
        self.example = example if example is not None else {"sample_variable": "", "sample_response": ""}

        # Delegate to subclass "set_*" logic if not given in init
        self.set_tools()

        if not self.prompt:
            set_val = self.set_prompt()
            if set_val:
                self.prompt = set_val

        if not self.name:
            set_val = self.set_name()
            if set_val:
                self.name = set_val

        if not self.variables:
            set_val = self.set_variables()
            if set_val:
                self.variables = set_val

        if not self.variable_defaults:
            set_val = self.set_variable_defaults()
            if set_val:
                self.variable_defaults = set_val

        if not self.macros:
            set_val = self.set_macros()
            if set_val:
                self.macros = set_val

        self._check_variable_defaults()
        self._check_required_fields()

    ###### Abstract set_* methods for subclass implementation #######

    @abstractmethod
    def set_prompt(self) -> Optional[str]:
        """
        Subclass defines self.prompt (template str). Return the template, or
        set self.prompt directly and return None.
        """
        pass

    @abstractmethod
    def set_macros(self) -> Optional[dict]:
        """
        Subclass defines self.macros (dict mapping <<KEY>> to replacement value).
        Return the dict, or set self.macros directly and return None.
        """
        return {
            "<<DATETIME>>": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def add_macro(self, key: str, value: str):
        """Add a macro substitution (<<key>> → value)."""
        self.macros[key] = value

    @abstractmethod
    def set_variable_defaults(self) -> Optional[dict]:
        """
        Subclass defines self.variable_defaults (dict of default values for variables).
        Return the dict, or set the attribute directly and return None.
        """
        for var in self.variables:
            if var not in self.variable_defaults:
                if self.verbose:
                    logger.warning(
                        f"Default for '{var}' not set in class, consider using `set_variable_defaults_empty`"
                    )
        return None

    def add_variable_default(self, name: str, value: str):
        """Add a default value for a specific prompt variable."""
        self.variable_defaults[name] = value

    def set_variable_defaults_empty(self):
        """Set any variable that has no default to an empty string."""
        for var in self.variables:
            if var not in self.variable_defaults:
                self.variable_defaults[var] = ""
                if self.verbose:
                    logger.warning(
                        f"Default for '{var}' not set in class '{self.name}'; using empty string."
                    )

    @abstractmethod
    def set_variables(self) -> Optional[list]:
        """
        Subclass defines self.variables as a list of placeholder names. Return
        the list, or set the attribute directly and return None.
        Default: auto-extract {key} names from prompt.
        """
        try:
            self.variables = regex.findall(r"\{(.*?)\}", self.prompt)
        except Exception as e:
            logger.error(
                (
                    f"Error extracting variables from prompt in class '{self.name}':\n",
                    f"Prompt: {self.prompt}",
                    f"Exception: {e}",
                )
            )
            raise e
        if self.verbose:
            logger.info(f"Variables for {self.name}: {self.variables}")
        return None

    @abstractmethod
    def set_name(self) -> Optional[str]:
        """
        Subclass sets self.name. Return the name, or set self.name directly
        and return None. Default: class name.
        """
        self.name = self.__class__.__name__
        if self.verbose:
            logger.info(f"No name set; using class name: {self.name}")
        return None

    @abstractmethod
    def set_tools(self) -> None:
        """
        Subclass sets self.tools (identifiers of allowed tools). Return value
        is ignored — set self.tools on the instance.
        """
        self.tools = []

    ###### Validation logic #######

    def _check_variable_defaults(self):
        """Ensure every key in variable_defaults is declared in self.variables."""
        for key in self.variable_defaults.keys():
            if key not in self.variables:
                raise ValueError(
                    f"Variable '{key}' in variable_defaults, but not in variables. "
                    f"Allowed: {self.variables}"
                )

    def _check_required_fields(self):
        """Ensure all mandatory fields are set."""
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
        """Return a (JSON serializable) dictionary describing this PromptBase."""
        for attr, expected in [
            ("expected_config", dict),
            ("example", dict),
            ("tags", list),
            ("tools", list),
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
            "variable_defaults": self.variable_defaults,
            "macros": self.macros,
            "tags": self.tags,
            "author": self.author,
            "version": self.version,
            "timestamp": self.timestamp,
            "tools": self.tools,
            "expected_config": self.expected_config,
            "example": self.example,
        }

    def _get_prompt(
        self, base: str, variables: dict = {}, no_warning: bool = False
    ) -> str:
        """Fill the prompt string's placeholders with provided (or default) variables and macros."""
        for key in variables:
            if key not in self.variables:
                logger.warning(
                    f"Unknown variable '{key}' in prompt input for {self.name}. \n"
                    f"Allowed: {list(self.variables)}"
                )

        result = base

        for key in self.variables:
            if key in variables and variables[key] is not None:
                value = str(variables[key])
            elif (
                key in self.variable_defaults
                and self.variable_defaults[key] is not None
            ):
                value = str(self.variable_defaults[key])
            else:
                error_message = (
                    f"Variable '{key}' required in prompt input for {self.name}; "
                    f"none given and no default."
                )
                logger.error(error_message, exc_info=True)
                raise ValueError(error_message)
            result = result.replace(f"{{{key}}}", value)

        for key, v in self.macros.items():
            result = result.replace(key, str(v))

        if not no_warning:
            for unmatched in regex.findall(r"<<(.*?)>>", result):
                if f"<<{unmatched}>>" not in self.macros:
                    logger.warning(
                        f"Unresolved macro '<<{unmatched}>>' in rendered prompt for {self.name}."
                    )
        return result

    def get_prompt(self, variables: dict = {}, no_warning: bool = False) -> str:
        """Get the filled prompt string with provided (or default) variables and macros."""
        return self._get_prompt(self.prompt, variables, no_warning=no_warning)

    def __str__(self) -> str:
        result = self.prompt

        for key in self.variables:
            if (
                key in self.variable_defaults
                and self.variable_defaults[key] is not None
            ):
                result = result.replace(f"{{{key}}}", str(self.variable_defaults[key]))

        for key, v in (self.macros or {}).items():
            result = result.replace(key, str(v))

        return result

    def __call__(self, variables: dict = {}, no_warning: bool = False) -> str:
        """Allow prompt instances to be called like a function to render the prompt."""
        return self.get_prompt(variables, no_warning=no_warning)

    @staticmethod
    def _escape_braces(line: str) -> str:
        """Make unmatched { or } into double braces for safe formatting."""
        escaped = regex.sub(r"(?<!{){(?!{)", "{{", line)
        escaped = regex.sub(r"(?<!})}(?!})", "}}", escaped)
        return escaped
