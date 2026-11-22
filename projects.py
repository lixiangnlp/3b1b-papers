"""仓库里的视频项目登记表：每个项目一个源码目录（narration.py / common.py / scenes.py）。

attention 沿用最初的 build/ 布局；之后的项目各自放在 build/<name>/ 下，互不干扰。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Project:
    name: str
    src: Path        # narration.py / common.py / scenes.py 所在目录
    build: Path      # audio/、cues/、media/、成片
    output: str      # 成片文件名

    @property
    def audio_dir(self) -> Path:
        return self.build / "audio"

    @property
    def output_path(self) -> Path:
        return self.build / self.output


PROJECTS: dict[str, Project] = {
    "attention": Project("attention", ROOT / "attention", ROOT / "build",
                         "attention_is_all_you_need.mp4"),
    "riemann": Project("riemann", ROOT / "riemann", ROOT / "build" / "riemann",
                       "riemann_hypothesis_alpoge_claude.mp4"),
}
DEFAULT_PROJECT = "attention"


def get_project(name: str) -> Project:
    """返回项目配置，并把它的源码目录放到 sys.path 最前面（以便 import narration）。"""
    proj = PROJECTS[name]
    sys.path.insert(0, str(proj.src))
    return proj
