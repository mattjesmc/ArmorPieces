#!/usr/bin/env python3
"""Mints and guards the lineage identifier every shipped piece, skin and cloth carries.

A `uid` is what lets a saved item find its piece again after the piece has been renamed, moved to
another pack or picked up by a different author. It is minted ONCE and then never changes - a uid
that changes is worse than no uid at all, because a stale one in somebody's save rebinds to the
wrong thing. `uids.lock` is what enforces that: an append-only record of every id-to-uid pair this
repository has ever issued, including for content that has since been removed, because a removed
piece's uid may still be sitting in a world somewhere.

    python tools/mint_uids.py            # mint one for anything that has none, update the lock
    python tools/mint_uids.py --check    # change nothing; fail if anything is wrong

The check is what runs in the gate. It fails when:

  * a shipped file has no uid;
  * two files share one;
  * a file's uid differs from the lock's - the case that matters, and the only one a person can
    cause by editing a file by hand;
  * a `former_ids` entry is claimed by more than one piece, which is the same collision the additive
    checker exists for, seen from the side this tool can already see.

It does NOT fail on a lock entry with no file: that is a piece that was removed or moved out, and
keeping the line is the whole point.

See docs/plans/compatibility.md section 4.7.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "uids.lock"

# The three datapack-loaded types whose Java implements `Identified`. Fittings are deliberately not
# here: a fitting's type is code, there are six of them and none has ever moved, so the mod tolerates
# an unresolvable one without trying to rebind it.
KINDS = ("armor_decoration", "armor_skin", "cloth")

# ap1 says which minting scheme, so a later one can be told apart without guessing at the length.
# 96 bits, base32, lower case: 20 characters, and a collision needs about 10^14 pieces.
PREFIX = "ap1"


def mint() -> str:
    body = base64.b32encode(secrets.token_bytes(12)).decode("ascii").rstrip("=").lower()
    return f"{PREFIX}{body}"


def shipped() -> list[tuple[str, str, Path]]:
    """(kind, "<ns>:<name>", path) for everything this repository ships."""
    found: list[tuple[str, str, Path]] = []
    roots = [ROOT / "src/main/resources/data"]
    packs = ROOT / "packs"
    if packs.is_dir():
        roots += [pack / "datapack" / "data" for pack in sorted(packs.iterdir()) if pack.is_dir()]
    for root in roots:
        if not root.is_dir():
            continue
        for namespace in sorted(p for p in root.iterdir() if p.is_dir()):
            for kind in KINDS:
                folder = namespace / "armorpieces" / kind
                if not folder.is_dir():
                    continue
                for path in sorted(folder.glob("*.json")):
                    found.append((kind, f"{namespace.name}:{path.stem}", path))
    return found


def load_lock() -> dict[str, str]:
    if not LOCK.is_file():
        return {}
    return json.loads(LOCK.read_text(encoding="utf-8"))


def save_lock(lock: dict[str, str]) -> None:
    LOCK.write_text(
        json.dumps(dict(sorted(lock.items())), indent=2) + "\n", encoding="utf-8")


def key(kind: str, ident: str) -> str:
    return f"{kind}/{ident}"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict) -> None:
    # Two spaces and a trailing newline, as every other data file in the tree is written.
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(check_only: bool) -> int:
    lock = load_lock()
    problems: list[str] = []
    seen: dict[str, str] = {}
    formers: dict[str, str] = {}
    minted = 0
    stamped = 0

    for kind, ident, path in shipped():
        data = read(path)
        entry = key(kind, ident)
        uid = data.get("uid")
        locked = lock.get(entry)

        if uid is None and locked is not None:
            # The lock knows it; the file lost it. Put it back rather than minting a second one.
            if check_only:
                problems.append(f"{ident}: has no uid, but uids.lock holds {locked} for it")
            else:
                data["uid"] = locked
                write(path, data)
                stamped += 1
                uid = locked
        elif uid is None:
            if check_only:
                problems.append(f"{ident}: no uid - run python tools/mint_uids.py")
            else:
                uid = mint()
                data["uid"] = uid
                write(path, data)
                lock[entry] = uid
                minted += 1
        elif locked is None:
            if check_only:
                problems.append(f"{ident}: carries {uid}, which uids.lock has never seen")
            else:
                lock[entry] = uid
        elif uid != locked:
            # Never repaired automatically, in either direction: one of the two is somebody's
            # mistake and only they know which.
            problems.append(f"{ident}: carries {uid}, but uids.lock says {locked}")

        if uid is not None:
            if uid in seen:
                problems.append(f"{ident}: shares the uid {uid} with {seen[uid]}")
            seen[uid] = ident

        for former in data.get("former_ids", []):
            claim = key(kind, former)
            if claim in formers:
                problems.append(
                    f"{ident}: claims the former id {former}, and so does {formers[claim]}")
            formers[claim] = ident
            if former == ident:
                problems.append(f"{ident}: lists itself as a former id")

    if not check_only:
        save_lock(lock)

    for problem in problems:
        print(f"  {problem}", file=sys.stderr)

    if check_only:
        if problems:
            print(f"{len(problems)} problem(s) in the uid ledger", file=sys.stderr)
            return 1
        print(f"uids: {len(seen)} pieces, {len(lock)} in the lock, {len(formers)} former ids - clean")
        return 0

    print(f"uids: minted {minted}, restored {stamped}, {len(seen)} shipped, {len(lock)} in the lock")
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="change nothing; fail if any uid is missing, doubled or altered")
    args = parser.parse_args()
    os.chdir(ROOT)
    return run(args.check)


if __name__ == "__main__":
    raise SystemExit(main())
