"""国际化支持：中英文切换，自动检测系统语言，支持 --lang 覆盖。"""

from __future__ import annotations

import json
import locale
import os
from pathlib import Path
from functools import lru_cache

# 翻译文件目录（兼容 PyInstaller 打包）
def _get_locales_dir() -> Path:
    import sys
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", "."))
        return base / "locales"
    return Path(__file__).resolve().parent.parent / "locales"

_LOCALES_DIR = _get_locales_dir()

# 当前语言
_current_lang: str = ""


def set_lang(lang: str) -> None:
    """手动设置语言。"""
    global _current_lang
    lang = lang.lower()
    if lang in ("zh", "cn", "zh-cn", "zh_cn", "chinese"):
        _current_lang = "zh"
    else:
        _current_lang = "en"
    # 清除缓存
    _get_translations.cache_clear()


def get_lang() -> str:
    """返回当前语言代码 ('zh' 或 'en')。"""
    global _current_lang
    if _current_lang:
        return _current_lang

    # 自动检测
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(var, "")
        if val and val.lower().startswith(("zh", "cn")):
            _current_lang = "zh"
            return _current_lang

    # 系统默认
    try:
        sys_locale = locale.getdefaultlocale()[0] or ""
        if sys_locale.lower().startswith(("zh", "cn")):
            _current_lang = "zh"
            return _current_lang
    except Exception:
        pass

    _current_lang = "en"
    return _current_lang


@lru_cache(maxsize=1)
def _get_translations() -> dict[str, str]:
    """加载当前语言的翻译文件（缓存）。"""
    lang = get_lang()
    path = _LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _(key: str, **kwargs: object) -> str:
    """翻译函数：_(key) 返回翻译文本，支持 {name} 占位符。

    Usage:
        _("status.title")           → "Bridle Status" / "Bridle 状态"
        _("init.created", n=5)     → "Created 5 files" / "已创建 5 个文件"
    """
    translations = _get_translations()
    text = translations.get(key)
    if text is None:
        # 回退到 key 本身（英文原文）
        text = key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def node_name(node_id: str) -> str:
    """返回节点的翻译名称。找不到翻译时返回原始 node_id 的美化版本。"""
    name = _(f"node.{node_id}")
    if name == f"node.{node_id}":
        # 无翻译时回退到标题化版本
        return node_id.replace("_", " ").title()
    return name
