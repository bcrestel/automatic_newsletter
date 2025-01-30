import logging

from typing import Union, List
from litellm.types.utils import ModelResponse
from litellm.litellm_core_utils.streaming_handler import CustomStreamWrapper
from litellm import completion as litellm_completion

logger = logging.getLogger(__name__)


class GenAIModel:
    def __init__(self, model_type: str, system_promt: str = ""):
        self.model_type = model_type
        defaut_system_prompt = "You are a helpful assistant."
        self.system_prompt = system_promt if len(system_promt) > 0 else defaut_system_prompt
        self.catalog_models = {
            "moderation": [
                "groq/llama-guard-3-8b",
                "mistral/mistral-moderation-2411",
            ],
            "reasoning": [
                "gemini/gemini-2.0-flash-thinking-exp-01-21",
                "openrouter/google/gemini-2.0-flash-thinking-exp:free",
                "gemini/gemini-2.0-flash-thinking-exp-1219",
                "openrouter/google/gemini-2.0-flash-thinking-exp-1219:free",
                "openrouter/deepseek/deepseek-r1:free",
            ],
            "large": [
                "gemini/gemini-1.5-pro-002",
                "gemini/models/gemini-1.5-pro-exp-0827",
                "openrouter/meta-llama/llama-3.1-405b-instruct:free",
                "gemini/gemini-1.5-pro-001",
                "mistral/mistral-large-2411",
                "mistral/mistral-large-2407",
                "mistral/mistral-large-2402",
            ],
            "medium": [
                "gemini/gemini-1.5-flash-latest",
                "gemini/gemini-1.5-flash-002",
                "gemini/gemini-1.5-flash-exp-0827"
                "groq/llama-3.3-70b-versatile",
                "groq/llama-3.3-70b-specdec",
                "gemini/gemini-1.5-flash-001",
                "mistral/mistral-medium",
            ],
            "small": [
                "gemini/gemini-1.5-flash-8b-001",
                "gemini/gemini-1.5-flash-8b-latest",
                "gemini/gemini-1.5-flash-8b-exp-0924",
                "gemini/gemini-1.5-flash-8b-exp-0827",
                "mistal/ministral-8b-2410",
                "openrouter/meta-llama/llama-3.1-8b-instruct:free",
                "groq/llama-3.1-8b-instant",
                "openrouter/meta-llama/llama-3-8b-instruct:free",
            ],
        }
        self.model_list = self._map_model_type_to_model_names(self.model_type)
    
    def completion(self, user_prompt: str, parameters: dict = {}) -> Union[ModelResponse, CustomStreamWrapper]:
        for model in self.model_list:
            try:
                return litellm_completion(
                    model=model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                        ],
                    **parameters,
                    )
            except Exception as e:
                logger.warning(f"Model {model} raised an Exception")
        logger.error("All models in the list raised an Exception: {self.model_list}")
        raise ValueError(f"No more models to try")
    
    def completion_str(self, *args, **kwargs) -> str:
        return self.get_content_from_response(self.completion_str(*args, **kwargs))
    
    def get_content_from_response(self, response: Union[ModelResponse, CustomStreamWrapper]) -> str:
        return response['choices'][0].message.content
    
    def get_all_model_types(self):
        return self.catalog_models.keys()

    def _map_model_type_to_model_names(self, model_type: str) -> List[str]:
        try:
            list_of_models = self.catalog_models[model_type]
        except KeyError as e:
            logger.error(f"Values allowed for model_type are: {self.get_all_model_types()}")
            raise e
        # tmp
        if len(list_of_models) == 0:
            raise NotImplementedError
        return list_of_models
