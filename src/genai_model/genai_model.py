import logging
from typing import List, Union

from litellm import completion as litellm_completion
from litellm.litellm_core_utils.streaming_handler import CustomStreamWrapper
from litellm.types.utils import ModelResponse

from src.genai_model.config import MODELS_CATALOG
from src.utils.list import flatten_list_of_lists

logger = logging.getLogger(__name__)


class GenAIModel:
    def __init__(self, model_type: str, system_promt: str = ""):
        self.model_type = model_type
        defaut_system_prompt = "You are a helpful assistant."
        self.system_prompt = (
            system_promt if len(system_promt) > 0 else defaut_system_prompt
        )
        self.models_catalog = MODELS_CATALOG
        self.all_models = flatten_list_of_lists((self.models_catalog.values()))
        self.list_of_models = self._map_model_type_to_model_names(self.model_type)

    def completion(
        self, user_prompt: str, parameters: dict = {"temperature": 1.0}
    ) -> Union[ModelResponse, CustomStreamWrapper]:
        for model in self.list_of_models:
            try:
                return litellm_completion(
                    model=model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    **parameters,
                )
            except Exception as e:
                logger.warning(f"Model {model} raised an Exception.")
                logger.debug(e)
        logger.error("All models in the list raised an Exception: {self.model_list}")
        raise ValueError(f"No more models left to try.")

    def completion_str(self, *args, **kwargs) -> str:
        return self.get_content_from_response(self.completion(*args, **kwargs))

    @staticmethod
    def get_content_from_response(
        response: Union[ModelResponse, CustomStreamWrapper],
    ) -> str:
        return response["choices"][0].message.content

    def get_all_model_types(self):
        return self.models_catalog.keys()

    def _map_model_type_to_model_names(self, model_type: str) -> List[str]:
        """Collect the list of models specified by model_type. This can be done in 3 different ways:
        - specific category: 'reasoning', 'large', 'medium', 'small', 'moderation'
        - all: use all models in 'large', 'medium', 'small'
        - specific model name: will collect all models found in the entier catalog

        Args:
            model_type (str): key word to identify the targeted collection of models

        Raises:
            NotImplementedError: if model_type was incorrect

        Returns:
            List[str]: list of models corresponding to that model_type
        """
        list_of_models = []
        if model_type in self.models_catalog.keys():
            list_of_models = self.models_catalog[model_type]
        elif model_type == "all":
            list_of_models = (
                self.models_catalog["large"]
                + self.models_catalog["medium"]
                + self.models_catalog["small"]
            )
        else:
            for _, model_list in self.models_catalog.items():
                for model in model_list:
                    if model_type in model:
                        list_of_models.append(model)
        # Check we have found models for that model_type
        if len(list_of_models) == 0:
            logger.error(
                f"Could not find any models corresponding to model_type: {model_type}"
            )
            raise NotImplementedError
        else:
            logger.info(
                f"Found {len(list_of_models)} models for model_type {model_type}"
            )
            logger.info(f"List of models included: {list_of_models}")
        return list_of_models
