"""Image provider 注册中心。

启动时自动扫描同目录下所有 .py 模块（除 base / __init__）并 import，
让每个 provider 文件末尾的 register() 调用生效。

新增 provider = 在本目录新建一个 .py 文件 + 末尾调 register()，无需改其他文件。
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from .base import ImageProvider, find_provider, get_providers, register

__all__ = ["ImageProvider", "register", "get_providers", "find_provider"]

# Auto-discovery：import 同目录下所有 module（除 base / __init__），触发其 register()
_pkg_dir = Path(__file__).parent
for module_info in pkgutil.iter_modules([str(_pkg_dir)]):
    if module_info.name in ("base", "__init__"):
        continue
    importlib.import_module(f".{module_info.name}", package=__package__)
