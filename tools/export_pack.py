"""
Zip a pack folder for handing round.

A datapack or a resource pack is installed as a zip as often as a folder, and the zip the game
wants is the folder's CONTENTS at the root - pack.mcmeta beside data/ or assets/ - not the folder
inside the zip. This writes exactly that, skipping the things that are never part of a pack: version
control, editor scratch, Python caches, and the plugin's own temporary files. The build makes the
mod's two zips the same way; the Blockbench plugin's Export Pack... calls this.

Usage:
    python tools/export_pack.py <pack dir> [<out.zip>]     # default: <pack dir>.zip beside it
    python tools/export_pack.py <pack dir> <out.zip> --reproducible   # same bytes for same files

`--reproducible` fixes every member's timestamp, so that two packs holding the same files zip to
the same bytes - which is what lets a site keep one file for one selection, however often it is
asked for.

A pack says which mod version it needs in its own pack.mcmeta, in a section the game ignores and
the library, the editor and pack_manifest.py read:

    { "pack": { ... }, "armorpieces": { "requires": "0.4.0" } }

The export notes a pack that does not say so, and exports it anyway.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

SKIP_DIRS = {".git", ".svn", "__pycache__", ".idea", ".vscode", "node_modules"}
# `.armorpieces-checkout.json` marks a folder as one piece checked out of a library
# (docs/plans/editor-client.md section 2). It is the editor's bookkeeping, not pack content:
# the site would drop it at ingest anyway, and a pack handed round should not carry it.
SKIP_FILES = {".DS_Store", "Thumbs.db", "desktop.ini", ".armorpieces-checkout.json"}


# ZIP's epoch; a member cannot be dated earlier.
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def requires_of(mcmeta: Path) -> str | None:
    """The mod version a pack.mcmeta says its pack needs (`armorpieces.requires`), or None."""
    try:
        with mcmeta.open(encoding="utf-8") as handle:
            requires = json.load(handle).get("armorpieces", {}).get("requires")
    except (OSError, ValueError, AttributeError):
        return None
    return requires if isinstance(requires, str) and requires.strip() else None


def export(pack: Path, out: Path, reproducible: bool = False) -> int:
    pack = pack.resolve()
    if not pack.is_dir():
        sys.exit(f"error: no pack folder at {pack}")
    if not (pack / "pack.mcmeta").is_file():
        print(f"note: {pack.name} has no pack.mcmeta; the game will not list it as a pack", file=sys.stderr)
    elif requires_of(pack / "pack.mcmeta") is None:
        # Not refused: a zip handed round still works. But the library and the editor read this
        # to say which mod a pack needs, and a pack that does not say is offered to everyone.
        print(f"note: {pack.name}/pack.mcmeta declares no \"armorpieces\": {{\"requires\": ...}} - "
              "the library cannot say which mod version it needs", file=sys.stderr)
    written = 0
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(pack.rglob("*")):
            relative = file.relative_to(pack)
            if any(part in SKIP_DIRS for part in relative.parts) or file.name in SKIP_FILES:
                continue
            if file.is_file() and file.resolve() != out.resolve():
                if reproducible:
                    info = zipfile.ZipInfo(relative.as_posix(), date_time=FIXED_TIME)
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o644 << 16
                    zf.writestr(info, file.read_bytes())
                else:
                    zf.write(file, relative.as_posix())
                written += 1
    return written


def main() -> None:
    reproducible = "--reproducible" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--reproducible"]
    if not args:
        sys.exit(__doc__)
    pack = Path(args[0])
    out = Path(args[1]) if len(args) > 1 else pack.resolve().with_name(pack.resolve().name + ".zip")
    written = export(pack, out, reproducible)
    print(f"wrote {written} files -> {out}")


if __name__ == "__main__":
    main()
