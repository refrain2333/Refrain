from functools import lru_cache
from .base import BaseLLM
from .openai_provider import OpenAIProvider

@lru_cache()
def get_llm_backend(
    api_key: str | None = None, 
    base_url: str | None = None, 
    model: str | None = None
) -> BaseLLM:
    """
    依赖注入专用函数。
    1. 不传参时：通过 @lru_cache 返回默认单例。
    2. 传参时：根据不同的参数组合返回（并缓存）对应的 LLM 实例。
    """
    return OpenAIProvider(
        api_key=api_key,
        base_url=base_url,
        default_model=model
    )

