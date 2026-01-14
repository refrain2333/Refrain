from functools import lru_cache
from typing import Type
from .base import BaseLLM
from .openai_provider import OpenAIProvider
from refrain.core.config import user_config
from refrain.core.logger import log

# 驱动映射表
PROVIDER_MAP: dict[str, Type[BaseLLM]] = {
    "openai": OpenAIProvider,
    "deepseek": OpenAIProvider,  # DeepSeek 兼容 OpenAI 协议
}

@lru_cache()
def get_llm_backend(
    alias: str | None = None,
    provider: str | None = None,
    api_key: str | None = None, 
    base_url: str | None = None, 
    model: str | None = None
) -> BaseLLM:
    """
    LLM 实例工厂：
    1. 如果指定了 alias (别名)，则从用户配置中加载对应的 Profile。
    2. 如果未指定任何参数，则加载当前激活的默认 Profile。
    3. 如果指定了 provider/api_key 等参数，则构建自定义实例。
    """
    
    # 逻辑 A：如果没有任何参数，或仅指定了别名，尝试从用户配置加载
    if not any([provider, api_key, base_url, model]) or alias:
        # 获取 Profile (如果 alias 为 None，manager 会返回当前激活的默认 Profile)
        profile = user_config.config.profiles.get(alias) if alias else user_config.get_active_profile()
        
        if profile:
            provider_cls = PROVIDER_MAP.get(profile.provider, OpenAIProvider)
            log.info(f"从配置加载 LLM | 别名: {profile.name} | 模型: {profile.model}")
            return provider_cls(
                api_key=api_key, # 如果手动传了 key，则覆盖配置
                api_key_env=profile.api_key_env,
                base_url=base_url or profile.base_url,
                default_model=model or profile.model,
                timeout=profile.timeout,
                **profile.extra_params
            )

    # 逻辑 B：手动构建模式
    p_key = (provider or "openai").lower()
    provider_cls = PROVIDER_MAP.get(p_key, OpenAIProvider)
    
    log.info(f"手动构建 LLM 实例 | Provider: {p_key} | 模型: {model or '默认'}")
        
    return provider_cls(
        api_key=api_key,
        base_url=base_url,
        default_model=model
    )
