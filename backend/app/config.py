"""应用配置 - 通过环境变量读取.

优先级：环境变量 > config/.env.local > .env
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（backend/）
_BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用全局配置，所有敏感信息从环境变量读取."""

    model_config = SettingsConfigDict(
        # 按优先级从低到高排列，后面的覆盖前面的
        env_file=(
            str(_BASE_DIR / ".env"),
            str(_BASE_DIR / "config" / ".env.local"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "小路书"
    debug: bool = False

    # 数据库
    database_url: str = "mysql+aiomysql://root:root@localhost:3306/pathbook"

    # JWT
    jwt_secret: str = "change-me-to-random-string"
    jwt_expire_hours: int = 168  # 7天

    # 日志
    log_level: str = "INFO"

    # LLM
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""


settings = Settings()
