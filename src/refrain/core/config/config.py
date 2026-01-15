"""
配置模块 - 统一管理用户配置和模型预设

提供：
- ModelProfile / AppConfig Pydantic 模型
- ConfigManager 配置持久化（YAML）
- 交互式配置命令（Questionary）
"""
from pathlib import Path
from typing import Any
import yaml
import keyring
from pydantic import BaseModel, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ============ 系统配置 (不可修改) ============

class Settings(BaseSettings):
    """不可修改的系统配置，从 .env 读取"""
    PROJECT_NAME: str = "Refrain"
    DEBUG: bool = False
    ENV: str = "development"
    PROJECT_ROOT: str = str(Path(__file__).resolve().parents[4])
    DEFAULT_LLM_MODEL: str = "deepseek-chat"
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# ============ 用户配置 (可修改) ============

class ModelProfile(BaseModel):
    """单个模型的配置预设"""
    name: str = Field(..., description="配置别名，如 gpt4, deepseek")
    provider: str | None = Field(None, description="供应商类型: openai, deepseek, anthropic")
    model: str = Field(..., description="具体的模型 ID，如 gpt-4o")
    api_key_env: str = Field(default="", description="API Key 环境变量名（可选）")
    base_url: str | None = Field(None, description="自定义 API 基础地址")
    temperature: float = 0.7
    timeout: float = 60.0
    extra_params: dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def litellm_id(self) -> str:
        """生成 LiteLLM 标准 ID"""
        if self.provider and "/" not in self.model:
            return f"{self.provider}/{self.model}"
        return self.model

    @computed_field
    @property
    def display_name(self) -> str:
        """友好显示名称"""
        return f"{self.model} ({self.provider or 'custom'})"


class AppConfig(BaseModel):
    """Refrain 整体应用配置"""
    current_model: str = "deepseek"

    profiles: dict[str, ModelProfile] = Field(default_factory=lambda: {
        "deepseek": ModelProfile(
            name="deepseek", provider="deepseek", model="deepseek-chat",
            api_key_env="DEEPSEEK_API_KEY", base_url="https://api.deepseek.com"
        ),
    })

    def get_active_profile(self) -> ModelProfile:
        """获取当前激活的配置"""
        if self.current_model not in self.profiles:
            available = ", ".join(self.profiles.keys())
            raise ValueError(
                f"未找到模型 '{self.current_model}'\n可用: {available}\n使用 `rf model use <name>` 切换"
            )
        return self.profiles[self.current_model]


# ============ 配置管理器 ============

class ConfigManager:
    """管理用户持久化配置 (YAML)"""

    CONFIG_DIR = Path.home() / ".refrain"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"

    def __init__(self):
        self._ensure_config_exists()
        self.config = self._load()

    def _ensure_config_exists(self):
        """初始化默认配置文件"""
        if not self.CONFIG_FILE.exists():
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            self.save(AppConfig())

    def _load(self) -> AppConfig:
        """从 YAML 加载配置"""
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return AppConfig(**data)
        except Exception:
            return AppConfig()

    def save(self, config: AppConfig | None = None):
        """保存配置到 YAML"""
        target = config or self.config
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(target.model_dump(mode="python"), f, allow_unicode=True, sort_keys=False)

    def get_active_profile(self) -> ModelProfile:
        return self.config.get_active_profile()

    @property
    def current_model_name(self) -> str:
        return self.config.current_model

    @current_model_name.setter
    def current_model_name(self, value: str):
        if value not in self.config.profiles:
            raise ValueError(f"模型 '{value}' 不存在")
        self.config.current_model = value
        self.save()


# ============ 交互式配置 (优化版) ============

PROVIDER_TEMPLATES = {
    "DeepSeek": {"provider": "deepseek", "model": "deepseek-chat", "base_url": "https://api.deepseek.com", "env": "DEEPSEEK_API_KEY"},
    "OpenAI": {"provider": "openai", "model": "gpt-4o", "base_url": "https://api.openai.com/v1", "env": "OPENAI_API_KEY"},
    "Anthropic (Claude)": {"provider": "openai", "model": "claude-3-5-sonnet-20240620", "base_url": "http://43.160.243.8:8000/v1", "env": "ANTHROPIC_API_KEY"},
}

async def interactive_add_model_async() -> ModelProfile | None:
    """更智能的交互式添加新模型配置"""
    try:
        import questionary
    except ImportError:
        print("[yellow]请安装 questionary: pip install questionary[/]")
        return None

    # 1. 选择供应商模板
    p_choice = await questionary.select(
        "选择供应商模板:",
        choices=list(PROVIDER_TEMPLATES.keys()) + ["Custom (自定义)"]
    ).ask_async()
    
    if not p_choice: return None
    
    tpl = PROVIDER_TEMPLATES.get(p_choice, {})
    
    # 2. 基础信息
    name = await questionary.text("配置别名 (如: my-model):", default=tpl.get("provider", "custom")).ask_async()
    model = await questionary.text("模型 ID:", default=tpl.get("model", "")).ask_async()
    base_url = await questionary.text("API Base URL:", default=tpl.get("base_url", "")).ask_async()

    # 3. 认证方式
    auth_mode = await questionary.select(
        "如何提供 API Key?",
        choices=[
            "使用环境变量 (推荐)",
            "现在输入并保存到系统钥匙串 (更安全)",
            "稍后手动设置"
        ]
    ).ask_async()

    api_key_env = ""
    if auth_mode == "使用环境变量 (推荐)":
        api_key_env = await questionary.text("环境变量名:", default=tpl.get("env", "API_KEY")).ask_async()
    elif auth_mode == "现在输入并保存到系统钥匙串 (更安全)":
        key = await questionary.password("请输入您的 API Key:").ask_async()
        if key:
            # 使用别名作为服务 ID
            save_api_key_to_keyring(name, key)
            api_key_env = "" # 留空代表使用 keyring
    
    return ModelProfile(
        name=name,
        provider=tpl.get("provider", "openai"),
        model=model,
        api_key_env=api_key_env,
        base_url=base_url or None,
    )

def interactive_add_model() -> ModelProfile | None:
    import asyncio
    try:
        return asyncio.run(interactive_add_model_async())
    except RuntimeError:
        return None


def save_api_key_to_keyring(service: str, key: str) -> bool:
    """安全保存 API Key 到系统钥匙串"""
    try:
        keyring.set_password(service, "api_key", key)
        return True
    except Exception as e:
        print(f"[red]保存到钥匙串失败: {e}[/]")
        return False


def get_api_key_from_keyring(service: str) -> str | None:
    """从系统钥匙串读取 API Key"""
    try:
        return keyring.get_password(service, "api_key")
    except Exception:
        return None


# ============ 导出 ============

settings = Settings()
user_config = ConfigManager()

__all__ = [
    "Settings", "ModelProfile", "AppConfig",
    "ConfigManager", "user_config", "settings",
    "interactive_add_model", "interactive_add_model_async",
    "save_api_key_to_keyring", "get_api_key_from_keyring",
]
