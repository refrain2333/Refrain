import yaml
from pathlib import Path
from .schema import AppConfig, ModelProfile
from . import settings  # 引用基础系统配置

# 用户级别的配置目录：~/.refrain/
CONFIG_DIR = Path.home() / ".refrain"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

class ConfigManager:
    """管理用户持久化配置 (YAML)"""
    
    def __init__(self):
        self._ensure_config_exists()
        self.config = self._load()

    def _ensure_config_exists(self):
        """初始化默认配置文件"""
        if not CONFIG_FILE.exists():
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            default_config = AppConfig(
                current_model="gpt-4o",
                profiles={
                    "gpt-4o": ModelProfile(
                        name="gpt-4o",
                        provider="openai",
                        model="gpt-4o",
                        api_key_env="OPENAI_API_KEY"
                    ),
                    "deepseek": ModelProfile(
                        name="deepseek",
                        provider="deepseek",
                        model="deepseek-chat",
                        api_key_env="DEEPSEEK_API_KEY",
                        base_url="https://api.deepseek.com"
                    )
                }
            )
            self.save(default_config)

    def _load(self) -> AppConfig:
        """从磁盘加载配置"""
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return AppConfig(**data)
        except Exception:
            # 如果加载失败（格式错误等），返回一个空的但合规的配置
            return AppConfig()

    def save(self, config: AppConfig = None):
        """将配置持久化到磁盘"""
        target_config = config or self.config
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(target_config.model_dump(), f, allow_unicode=True, sort_keys=False)

    def get_active_profile(self) -> ModelProfile:
        return self.config.get_active_profile()

# 单例模式导出
user_config = ConfigManager()
