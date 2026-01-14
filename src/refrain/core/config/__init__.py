from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "Refrain"
    DEBUG: bool = False
    ENV: Literal["development", "production", "test"] = "development"
    
    # 路径配置
    # 自动计算项目根目录 (src/refrain/core/config/__init__.py -> 往上推 4 层到项目根)
    PROJECT_ROOT: str = str(Path(__file__).resolve().parents[4])
    
    # LLM 相关配置
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4o"
    
    OPENAI_API_KEY: str = "sk-xxx"
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com"

    # 日志配置
    LOG_LEVEL: str = "INFO"

    @property
    def is_local(self) -> bool:
        return self.ENV == "development"

    # 自动读取 .env 文件
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# 导出单例
settings = Settings()

# 延迟导入以避免循环依赖
from .manager import user_config
