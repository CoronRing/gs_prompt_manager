import os
import importlib.util
import inspect
from typing import Dict, List, Type, Optional
from gs_prompt_manager.prompt_base import PromptBase
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptManager:
    """
    A manager that automatically discovers, imports, and instantiates all subclasses of PromptBase
    in specified directories, making them accessible and queryable.
    """

    def __init__(
        self, prompt_paths: Optional[str | List[str]] = None, verbose: bool = False
    ) -> None:
        """
        Initialize the PromptManager, searching for subclasses of PromptBase in the provided path(s).

        Args:
            prompt_path: str or List[str], optional
                Path(s) to the directory/directories containing prompt implementations.
                If None, uses the directory containing the instantiation file.
            verbose: bool
                If True, prints summary information after initialization.
        """
        self.verbose = verbose
        self.prompt_paths: List[str] = []
        self.prompt_objects: Dict[str, Type[PromptBase]] = {}
        self.prompt_instances: Dict[str, PromptBase] = {}

        try:
            if prompt_paths is None:
                # stack()[1] is the immediate caller
                caller_frame = inspect.stack()[1]
                caller_filename = caller_frame.filename
                self.prompt_paths = [os.path.dirname(os.path.abspath(caller_filename))]
            elif isinstance(prompt_paths, list):
                self.prompt_paths = prompt_paths
            elif isinstance(prompt_paths, str):
                self.prompt_paths = [prompt_paths]
            else:
                raise ValueError("prompt_path must be a str, List[str], or None.")

            for path in self.prompt_paths:
                if not os.path.isdir(path):
                    raise ValueError(f"Provided path is not a directory: {path}")
                self.prompt_objects.update(
                    self.search_available_prompts(path, black_list=[])
                )

            # Instantiate each prompt class
            for prompt_name, prompt_class in self.prompt_objects.items():
                if prompt_name in self.prompt_instances:
                    raise ValueError(f"Duplicate prompt name found: {prompt_name}")
                try:
                    self.prompt_instances[prompt_name] = prompt_class()
                except Exception as e:
                    logger.error(
                        f"Error instantiating prompt '{prompt_name}': {e}",
                        exc_info=True,
                    )

            if self.verbose:
                logger.info(
                    f"PromptManager: Loaded {len(self.prompt_instances)} prompt classes: {list(self.prompt_instances.keys())}"
                )

        except Exception as e:
            logger.error("An error occurred during initialization", exc_info=True)
            raise e

    @staticmethod
    def search_available_prompts(
        path: str, black_list: Optional[List[Type[PromptBase]]] = None
    ) -> Dict[str, Type[PromptBase]]:
        """
        Recursively search for subclasses of PromptBase in Python files in a directory.

        Args:
            path: str
                The root directory to search.
            black_list: List[Type[PromptBase]], optional
                Classes to exclude from results.

        Returns:
            Dictionary mapping class name to class object (subclasses of PromptBase).
        """
        if black_list is None:
            black_list = []

        if not os.path.isdir(path):
            logger.error(f"Provided path is not a directory: {path}")
            raise ValueError(f"Provided path is not a directory: {path}")

        found: Dict[str, Type[PromptBase]] = {}

        for root, _, files in os.walk(path):
            for filename in files:
                if filename.endswith(".py") and filename != "__init__.py":
                    file_path = os.path.join(root, filename)
                    try:
                        module_name = os.path.splitext(os.path.basename(file_path))[0]
                        spec = importlib.util.spec_from_file_location(
                            module_name, file_path
                        )
                        if not spec or not spec.loader:
                            continue
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                    except Exception as e:
                        logger.error(
                            f"Error importing '{file_path}': {e}", exc_info=True
                        )
                        continue

                    # Inspect module members, filter classes
                    for name, candidate in inspect.getmembers(module, inspect.isclass):
                        if candidate.__module__ != module.__name__:
                            continue
                        if (
                            issubclass(candidate, PromptBase)
                            and candidate is not PromptBase
                        ):
                            if candidate in black_list:
                                continue
                            # if duplicate, throw a warning
                            if candidate.__name__ in found:
                                logger.warning(
                                    f"Duplicate prompt class '{candidate.__name__}' found in {file_path}. Skipping."
                                )
                            else:
                                found[candidate.__name__] = candidate
        return found

    @staticmethod
    def get_all_prompt_metadata(
        prompts: Dict[str, Type[PromptBase]],
    ) -> Dict[str, dict]:
        """
        Get metadata from all provided prompt classes.

        Args:
            prompts: Dict[str, Type[PromptBase]]
                Dict mapping class name to class (subclasses of PromptBase).

        Returns:
            Dict[str, dict]: Mapping from class name to metadata dictionary.
        """
        metadata_dict: Dict[str, dict] = {}

        for class_name, class_obj in prompts.items():
            try:
                instance = class_obj()
                if not hasattr(instance, "get_metadata"):
                    logger.warning(
                        f"Class '{class_name}' does not implement 'get_metadata'. Skipping."
                    )
                    continue
                meta = instance.get_metadata()
                if not isinstance(meta, dict):
                    logger.warning(
                        f"'get_metadata' in class '{class_name}' did not return a dictionary. Skipping."
                    )
                    continue
                metadata_dict[class_name] = meta
            except Exception as e:
                logger.error(
                    f"Error instantiating class '{class_name}': {e}", exc_info=True
                )

        return metadata_dict

    def get_prompt_instances(self) -> Dict[str, PromptBase]:
        """
        Returns all instantiated prompt objects.

        Returns:
            Dict[str, PromptBase]: Mapping from class name to instance.
        """
        return self.prompt_instances

    def get_prompt(
        self, name: str, no_warning: bool = False
    ) -> PromptBase:
        """
        Get an instantiated prompt by its class name.

        Args:
            name: str
                Name of the prompt class.

        Returns:
            PromptBase: The instance of the specified prompt.

        Raises:
            ValueError: If the prompt is not found.
        """
        if name not in self.prompt_instances:
            raise ValueError((
                f"Prompt '{name}' not found.\n" 
                f"  Available: {list(self.prompt_instances.keys())}\n"
                f"  Loaded from paths: {self.prompt_paths}\n"
                )
            )
        return self.prompt_instances[name]

    def get_prompt_names(self) -> List[str]:
        """
        Get the names of all available prompt classes.

        Returns:
            List[str]: List of prompt names.
        """
        return list(self.prompt_instances.keys())
