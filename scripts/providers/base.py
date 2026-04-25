"""ImageProvider 抽象 + 全局注册表。

每个 provider 是 providers/ 目录下的一个 .py 文件，文件结尾调 register(<instance>())
就被自动加入注册表。

接口设计原则：
- 主流程不依赖任何 provider，没装也能跑（card-image 渲染占位框）
- provider 自己说清楚能处理什么 source 规格 + 是否就绪可用
- 失败返回 None，不抛异常（避免 fetch 卡住整个 deck）
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ImageProvider(ABC):
    """图片来源 provider 抽象基类。"""

    name: str = "abstract"
    kinds: list[str] = []  # 'url' / 'search' / 'generate'，宣告自己处理哪些 source.kind

    @abstractmethod
    def can_handle(self, source: dict[str, Any]) -> bool:
        """判断是否能处理这个 source 规格。fetch 时会按 prefer 顺序找第一个能处理且可用的 provider。"""

    @abstractmethod
    def fetch(self, source: dict[str, Any], out_dir: Path) -> Path | None:
        """下载/生成图片到 out_dir，返回最终本地路径。失败返回 None（不抛异常）。"""

    def is_available(self) -> bool:
        """检查依赖、API key 是否就绪。默认 True（覆盖此方法以做检查）。"""
        return True


_REGISTRY: list[ImageProvider] = []


def register(provider: ImageProvider) -> None:
    """注册 provider。在 provider .py 文件结尾调用。"""
    _REGISTRY.append(provider)


def get_providers() -> list[ImageProvider]:
    """返回所有已注册的 provider（不论是否可用）。"""
    return list(_REGISTRY)


def find_provider(source: dict[str, Any]) -> ImageProvider | None:
    """按 source.prefer 顺序找第一个能处理且 is_available 的 provider。"""
    prefer = source.get("prefer") or []
    candidates = [p for p in _REGISTRY if p.is_available() and p.can_handle(source)]
    if not candidates:
        return None

    def rank(p: ImageProvider) -> int:
        if p.name in prefer:
            return prefer.index(p.name)
        return 999

    candidates.sort(key=rank)
    return candidates[0]
