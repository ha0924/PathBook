"""跨域共享 - i18n 多语言支持.

基于 python-i18n 包，提供统一翻译入口。
翻译文件位于 shared/locales/ 目录下。
"""

import i18n
from pathlib import Path

_LOCALES_DIR = Path(__file__).parent / "locales"

# python-i18n 配置
i18n.set("file_format", "json")
i18n.set("locale", "zh_CN")
i18n.set("fallback", "en_US")
i18n.set("enable_memoization", True)
i18n.set("filename_format", "{namespace}.{locale}.{format}")
i18n.load_path.append(str(_LOCALES_DIR))


def t(key: str, locale: str | None = None, **kwargs: object) -> str:
    """统一翻译入口.

    用法：
        t("errors.40001")                    → "用户名已存在"
        t("errors.40001", locale="en_US")    → "Username already exists"
        t("errors.40004", count=6)           → 支持占位符
    """
    if locale:
        return i18n.t(key, locale=locale, **kwargs)
    return i18n.t(key, **kwargs)
