"""
Make an unpacked pack safe to serve: keep only the file types a pack is made of, re-encode every
PNG through Pillow and re-serialise every JSON, and refuse anything over the caps.

A pack uploaded to a site is somebody else's zip, and a zip is a fine place to hide things. This
runs after import_pack.py has unpacked it (which already refuses paths outside the destination)
and before anything is stored or served: a file that is not a PNG, a JSON, a pack.mcmeta or the
credits file is deleted; a PNG that Pillow cannot decode, or that is larger than a texture has any
business being, is deleted; a JSON that does not parse is deleted; what is kept is written again
by Pillow and by json.dumps, so the bytes served are bytes this tool produced.

Usage:
    python tools/sanitize_pack.py <pack dir> [--max-files N] [--max-png-side N] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

KEEP_SUFFIXES = {".json", ".png", ".mcmeta"}
KEEP_NAMES = {"pack.mcmeta", "armorpieces-credits.json", "README.md", "LICENSE", "LICENSE.md", "LICENSE.txt"}
# A pack is JSON and textures. The largest texture the mod reads is a 64x64 skin; a pack sheet
# may be bigger, but nothing near a wallpaper.
MAX_PNG_SIDE = 1024
MAX_FILES = 5000
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_DEPTH = 12


def sanitize(pack: Path, max_files: int = MAX_FILES, max_png_side: int = MAX_PNG_SIDE) -> dict:
    pack = pack.resolve()
    if not pack.is_dir():
        raise SystemExit(f"error: no pack folder at {pack}")
    kept, removed, reasons = 0, 0, []
    files = [p for p in pack.rglob("*") if p.is_file()]
    if len(files) > max_files:
        raise SystemExit(f"error: {len(files)} files; the cap is {max_files}")
    for path in files:
        relative = path.relative_to(pack)
        why = None
        if len(relative.parts) > MAX_DEPTH:
            why = "too deep"
        elif any(part.startswith(".") for part in relative.parts):
            why = "hidden"
        elif path.name in KEEP_NAMES and path.suffix not in (".png",):
            if path.suffix == ".json" or path.name == "pack.mcmeta":
                why = _rewrite_json(path)
        elif path.suffix.lower() == ".png":
            why = _rewrite_png(path, max_png_side)
        elif path.suffix.lower() in (".json", ".mcmeta"):
            why = _rewrite_json(path)
        else:
            why = "not a pack file"
        if why:
            path.unlink()
            removed += 1
            reasons.append(f"{relative.as_posix()}: {why}")
        else:
            kept += 1
    # Empty folders left behind are noise the game does not mind and a zip would carry.
    for folder in sorted((p for p in pack.rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)):
        if not any(folder.iterdir()):
            folder.rmdir()
    return {"kept": kept, "removed": removed, "reasons": reasons}


def _rewrite_json(path: Path) -> str | None:
    if path.stat().st_size > MAX_JSON_BYTES:
        return "JSON too large"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as err:
        return f"not JSON ({err.__class__.__name__})"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return None


def _rewrite_png(path: Path, max_side: int) -> str | None:
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                return f"not a PNG ({image.format})"
            if image.width > max_side or image.height > max_side:
                return f"{image.width}x{image.height} is larger than {max_side}"
            # Decoded whole, so a truncated or hostile file fails here rather than in a client.
            image.load()
            clean = image.convert("RGBA") if image.mode not in ("RGBA", "RGB", "LA", "L", "P") else image.copy()
    except Exception as err:  # Pillow raises many things; every one means "not served"
        return f"unreadable ({err.__class__.__name__})"
    clean.save(path, format="PNG", optimize=True)
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack", type=Path)
    ap.add_argument("--max-files", type=int, default=MAX_FILES)
    ap.add_argument("--max-png-side", type=int, default=MAX_PNG_SIDE)
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    args = ap.parse_args()
    report = sanitize(args.pack, args.max_files, args.max_png_side)
    if args.json:
        print(json.dumps(report))
    else:
        print(f"kept {report['kept']}, removed {report['removed']}")
        for reason in report["reasons"]:
            print(f"  {reason}")


if __name__ == "__main__":
    main()
