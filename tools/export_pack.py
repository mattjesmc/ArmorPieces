"""
Zip a pack folder for handing round.

A datapack or a resource pack is installed as a zip as often as a folder, and the zip the game
wants is the folder's CONTENTS at the root - pack.mcmeta beside data/ or assets/ - not the folder
inside the zip. This writes exactly that, skipping the things that are never part of a pack: version
control, editor scratch, Python caches, and the plugin's own temporary files. The build makes the
mod's two zips the same way; the Blockbench plugin's Export Pack... calls this.

Usage:
    python tools/export_pack.py <pack dir> [<out.zip>]     # default: <pack dir>.zip beside it
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

SKIP_DIRS = {".git", ".svn", "__pycache__", ".idea", ".vscode", "node_modules"}
SKIP_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def export(pack: Path, out: Path) -> int:
    pack = pack.resolve()
    if not pack.is_dir():
        sys.exit(f"error: no pack folder at {pack}")
    if not (pack / "pack.mcmeta").is_file():
        print(f"note: {pack.name} has no pack.mcmeta; the game will not list it as a pack", file=sys.stderr)
    written = 0
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(pack.rglob("*")):
            relative = file.relative_to(pack)
            if any(part in SKIP_DIRS for part in relative.parts) or file.name in SKIP_FILES:
                continue
            if file.is_file() and file.resolve() != out.resolve():
                zf.write(file, relative.as_posix())
                written += 1
    return written


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pack = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else pack.resolve().with_name(pack.resolve().name + ".zip")
    written = export(pack, out)
    print(f"wrote {written} files -> {out}")


if __name__ == "__main__":
    main()
