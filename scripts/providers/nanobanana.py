"""nanobanana (Gemini Imagen) provider — AI image generation via Google Gemini API.

启用步骤:
  1. 设置 GEMINI_API_KEY=<your-key>
  2. pip install google-generativeai

未启用时 is_available() 返回 False，fetch 阶段自动跳过。
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

from .base import ImageProvider, register


class NanoBananaProvider(ImageProvider):
    name = "nanobanana"
    kinds = ["generate"]

    def is_available(self) -> bool:
        return bool(os.environ.get("GEMINI_API_KEY"))

    def can_handle(self, source: dict[str, Any]) -> bool:
        return source.get("kind") == "generate"

    def fetch(self, source: dict[str, Any], out_dir: Path) -> Path | None:
        query = source.get("query", "")
        aspect = source.get("aspect", "16:9")
        slug = hashlib.md5(query.encode()).hexdigest()[:12]

        try:
            import google.generativeai as genai  # type: ignore[import-untyped]
        except ImportError:
            print("  [nanobanana] google-generativeai not installed; run: pip install google-generativeai")
            return None

        try:
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            model = genai.ImageGenerationModel("imagen-3.0-generate-002")

            aspect_map = {"16:9": "16:9", "1:1": "1:1", "4:3": "4:3", "9:16": "9:16"}
            result = model.generate_images(
                prompt=query,
                number_of_images=1,
                aspect_ratio=aspect_map.get(aspect, "16:9"),
            )
            if not result.images:
                print(f"  [nanobanana] no images returned for: {query[:60]}...")
                return None

            out = out_dir / f"{slug}.png"
            result.images[0].save(str(out))
            print(f"  [nanobanana] generated → {out.name}")
            return out

        except Exception as e:
            print(f"  [nanobanana] generation failed: {e}")
            return None


register(NanoBananaProvider())
