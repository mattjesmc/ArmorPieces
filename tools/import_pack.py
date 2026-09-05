"""
Unpack a datapack or resource pack zip into a folder.

The counterpart to export_pack.py, and the same shape of operation in reverse. Packs are handed
round as zips, so bringing somebody else's parts in - or bringing your own back onto another
machine - starts with one, and every route into the editor should end at a folder the rest of the
toolchain already understands.

Two things it does that a plain unzip does not:

  - It finds the pack inside the zip. export_pack.py writes the folder's CONTENTS at the root,
    which is what the game wants, but plenty of zips in the wild wrap everything in a single
    folder instead - sometimes two deep, sometimes with the pack beside a readme. The pack is
    wherever pack.mcmeta is, or failing that wherever data/ or assets/ is, and that is the level
    extracted from.
  - It refuses to write outside the destination. A zip is somebody else's file and a member named
    ../../something is a real thing that happens.

Usage:
    python tools/import_pack.py <pack.zip> <dest dir>
    python tools/import_pack.py <pack.zip> <dest dir> --force    # merge into a pack already there
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path, PurePosixPath

# The same exclusions export_pack.py applies, so a round trip through both is stable.
SKIP_DIRS = {".git", ".svn", "__pycache__", ".idea", ".vscode", "node_modules"}
SKIP_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}

# What makes a directory in the zip look like the pack root, best first.
MARKERS = ("pack.mcmeta", "data", "assets")


def members(zf: zipfile.ZipFile) -> list[str]:
    return [info.filename for info in zf.infolist() if not info.is_dir()]


def find_root(names: list[str]) -> str:
    """The prefix inside the zip that the pack actually starts at, '' for the zip root.

    Judged by where pack.mcmeta sits, and only then by where data/ or assets/ do - a pack with
    both a pack.mcmeta and an assets/ at different depths is one whose mcmeta is right.
    """
    for marker in MARKERS:
        candidates = set()
        for name in names:
            parts = PurePosixPath(name).parts
            for depth, part in enumerate(parts):
                if part == marker and (marker != "pack.mcmeta" or depth == len(parts) - 1):
                    candidates.add("/".join(parts[:depth]))
        if len(candidates) == 1:
            return candidates.pop()
        if candidates:
            # Several - take the shallowest, which is the outermost pack in a zip of packs.
            return min(candidates, key=lambda p: (p.count("/"), len(p)))
    return ""


def safe_target(dest: Path, relative: str) -> Path | None:
    """Where a member lands, or None if it should not be written at all."""
    parts = PurePosixPath(relative).parts
    if not parts:
        return None
    if any(part in SKIP_DIRS for part in parts) or parts[-1] in SKIP_FILES:
        return None
    if any(part in ("..", "") or part.startswith("/") or ":" in part for part in parts):
        return None
    target = (dest / Path(*parts)).resolve()
    # Belt and braces: even with the check above, the resolved path must stay inside.
    if dest.resolve() not in target.parents and target != dest.resolve():
        return None
    return target


def import_pack(zip_path: Path, dest: Path, force: bool = False) -> tuple[int, int]:
    if not zip_path.is_file():
        sys.exit(f"error: no zip at {zip_path}")
    if (dest / "pack.mcmeta").is_file() and not force:
        sys.exit(f"error: {dest} is already a pack. Pass --force to merge into it.")

    with zipfile.ZipFile(zip_path) as zf:
        names = members(zf)
        if not names:
            sys.exit(f"error: {zip_path.name} is empty")
        root = find_root(names)
        prefix = root + "/" if root else ""

        written = skipped = 0
        dest.mkdir(parents=True, exist_ok=True)
        for name in names:
            if prefix and not name.startswith(prefix):
                skipped += 1
                continue
            target = safe_target(dest, name[len(prefix):])
            if target is None:
                skipped += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(name) as source, open(target, "wb") as out:
                out.write(source.read())
            written += 1

    if not (dest / "pack.mcmeta").is_file():
        print(f"note: no pack.mcmeta in {zip_path.name}; the game will not list this as a pack",
              file=sys.stderr)
    return written, skipped


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--force"]
    if len(args) < 2:
        sys.exit(__doc__)
    written, skipped = import_pack(Path(args[0]), Path(args[1]), "--force" in sys.argv)
    note = f", skipped {skipped}" if skipped else ""
    print(f"read {written} files -> {args[1]}{note}")


if __name__ == "__main__":
    main()
