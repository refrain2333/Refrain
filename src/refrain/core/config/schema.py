from pydantic import BaseModel, Field
from typing import Any, Literal

class ModelProfile(BaseModel):
    """单个模型的配置预设"""
    name: str = Field(..., description="配置别名，如 gpt4, deepseek")
    provider: str = Field("openai", description="供应商类型: openai, deepseek, litellm 等")
    model: str = Field(..., description="具体的模型 ID，如 gpt-4o, deepseek-chat")
    api_key_env: str = Field(..., description="读取 API Key 的环境变量名")
    base_url: str | None = Field(None, description="自定义 API 基础地址")
    temperature: float = 0.2
    timeout: float = 60.0
    extra_params: dict[str, Any] = Field(default_factory=dict, description="透传给驱动的额外参数")

class AppConfig(BaseModel):
    """Refrain 整体应用配置"""
    current_model: str = "gpt-4o"  # 当前选中的模型别名
    profiles: dict[str, ModelProfile] = Field(default_factory=dict)

    def get_active_profile(self) -> ModelProfile:
        """获取当前激活的配置，如果不存在则返回一个默认的"""
        return self.profiles.get(self.current_model) or ModelProfile(
            name="gpt-4o",
            provider="openai",
            model="gpt-4o",
            api_key_env="OPENAI_API_KEY"
        )
