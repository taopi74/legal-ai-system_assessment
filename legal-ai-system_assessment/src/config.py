from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    project_root: Path
    uploads_dir: Path
    extracted_dir: Path
    web_dir: Path


def get_app_paths() -> AppPaths:
    project_root = Path(__file__).resolve().parents[1]
    uploads_dir = project_root / "data" / "sample_inputs"
    extracted_dir = project_root / "data" / "extracted"
    web_dir = project_root / "web"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    extracted_dir.mkdir(parents=True, exist_ok=True)
    return AppPaths(
        project_root=project_root,
        uploads_dir=uploads_dir,
        extracted_dir=extracted_dir,
        web_dir=web_dir,
    )
