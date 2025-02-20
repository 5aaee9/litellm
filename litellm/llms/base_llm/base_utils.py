"""
Utility functions for base LLM classes.
"""

import copy
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Type, Union

from openai.lib import _parsing, _pydantic
from pydantic import BaseModel

from litellm._logger import verbose_logger
from litellm.types.llms.openai import AllMessageValues
from litellm.types.utils import ProviderSpecificModelInfo
from litellm.utils import get_model_info


class BaseLLMModelInfo(ABC):
    def get_provider_info(
        self,
        model: str,
    ) -> Optional[ProviderSpecificModelInfo]:
        return None

    @abstractmethod
    def get_models(self) -> List[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_api_key(api_key: Optional[str] = None) -> Optional[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_api_base(api_base: Optional[str] = None) -> Optional[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_base_model(model: str) -> Optional[str]:
        """
        Returns the base model name from the given model name.

        Some providers like bedrock - can receive model=`invoke/anthropic.claude-3-opus-20240229-v1:0` or `converse/anthropic.claude-3-opus-20240229-v1:0`
            This function will return `anthropic.claude-3-opus-20240229-v1:0`
        """
        pass

    @staticmethod
    def get_rerank_cost(
        model: str, num_queries: int = 1, custom_llm_provider: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Calculates the cost per query for a given rerank model.

        Input:
            - model: str, the model name without provider prefix

        Returns:
            Tuple[float, float] - prompt_cost_in_usd, completion_cost_in_usd
        """

        try:
            model_info = get_model_info(
                model=model, custom_llm_provider=custom_llm_provider
            )
        except Exception as e:
            verbose_logger.debug(f"Error getting model info for rerank model: {e}")
            model_info = None

        if (
            model_info is None
            or "input_cost_per_query" not in model_info
            or model_info["input_cost_per_query"] is None
        ):
            return 0.0, 0.0

        prompt_cost = model_info["input_cost_per_query"] * num_queries

        return prompt_cost, 0.0


def _dict_to_response_format_helper(
    response_format: dict, ref_template: Optional[str] = None
) -> dict:
    if ref_template is not None and response_format.get("type") == "json_schema":
        # Deep copy to avoid modifying original
        modified_format = copy.deepcopy(response_format)
        schema = modified_format["json_schema"]["schema"]

        # Update all $ref values in the schema
        def update_refs(schema):
            stack = [(schema, [])]
            visited = set()

            while stack:
                obj, path = stack.pop()
                obj_id = id(obj)

                if obj_id in visited:
                    continue
                visited.add(obj_id)

                if isinstance(obj, dict):
                    if "$ref" in obj:
                        ref_path = obj["$ref"]
                        model_name = ref_path.split("/")[-1]
                        obj["$ref"] = ref_template.format(model=model_name)

                    for k, v in obj.items():
                        if isinstance(v, (dict, list)):
                            stack.append((v, path + [k]))

                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            stack.append((item, path + [i]))

        update_refs(schema)
        return modified_format
    return response_format


def type_to_response_format_param(
    response_format: Optional[Union[Type[BaseModel], dict]],
    ref_template: Optional[str] = None,
) -> Optional[dict]:
    """
    Re-implementation of openai's 'type_to_response_format_param' function

    Used for converting pydantic object to api schema.
    """
    if response_format is None:
        return None

    if isinstance(response_format, dict):
        return _dict_to_response_format_helper(response_format, ref_template)

    # type checkers don't narrow the negation of a `TypeGuard` as it isn't
    # a safe default behaviour but we know that at this point the `response_format`
    # can only be a `type`
    if not _parsing._completions.is_basemodel_type(response_format):
        raise TypeError(f"Unsupported response_format type - {response_format}")

    if ref_template is not None:
        schema = response_format.model_json_schema(ref_template=ref_template)
    else:
        schema = _pydantic.to_strict_json_schema(response_format)

    return {
        "type": "json_schema",
        "json_schema": {
            "schema": schema,
            "name": response_format.__name__,
            "strict": True,
        },
    }


def map_developer_role_to_system_role(
    messages: List[AllMessageValues],
) -> List[AllMessageValues]:
    """
    Translate `developer` role to `system` role for non-OpenAI providers.
    """
    new_messages: List[AllMessageValues] = []
    for m in messages:
        if m["role"] == "developer":
            new_messages.append({"role": "system", "content": m["content"]})
        else:
            new_messages.append(m)
    return new_messages
