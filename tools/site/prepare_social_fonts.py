"""Seed Material for MkDocs' social-card font cache with pinned local files."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FONT_SOURCE_DIR = ROOT / "tools/site/fonts/source-serif-4"
PINNED_FONTS = {
    "Regular.ttf": "e5a4ee6a3d87bb9024796be390c6771e2a0eb1883dae25effaf57ca01668e24b",
    "Bold.ttf": "7cf4f4e1ad74f45058d5bc61716b82560442fbdcd9d3654d2dea96bf6c683d86",
}
DEFAULT_CACHE_DIR = ROOT / ".cache/plugin/social"


def prepare(cache_dir: Path = DEFAULT_CACHE_DIR) -> Path:
    """Verify and copy the pinned font files into the plugin's expected cache."""
    target_dir = cache_dir / "fonts/Source Serif 4"
    target_dir.mkdir(parents=True, exist_ok=True)

    for target_name, expected_sha256 in PINNED_FONTS.items():
        source_name = "SourceSerif4-" + target_name
        source = FONT_SOURCE_DIR / source_name
        if not source.is_file():
            raise FileNotFoundError(f"Pinned social font is missing: {source}")

        actual_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
        if actual_sha256 != expected_sha256:
            raise ValueError(f"Pinned social font hash mismatch: {source.name}")

        shutil.copyfile(source, target_dir / target_name)

    return target_dir


if __name__ == "__main__":
    location = prepare()
    print(f"Prepared pinned Source Serif 4 files for social cards: {location}")
