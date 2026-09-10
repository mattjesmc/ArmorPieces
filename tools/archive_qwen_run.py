"""Archive a Qwen authoring session's transcript into the repository's run corpus.

WHY THIS EXISTS SEPARATELY FROM run_briefs.ps1: a Qwen session runs with
`CLAUDE_CONFIG_DIR=~/.claude-qwen`, so its transcript is written to
`~/.claude-qwen/projects/<slug>/<session>.jsonl` and NOT to `~/.claude/projects/...`.
`tools/run_briefs.ps1` and `tools/measure_sessions.py` both look only in the latter, so a
Qwen run that nobody copies is a run that is simply lost - and the eight from the 2026-09-09
pilot were nearly lost that way.

A transcript is SELF-CONTAINED: every screenshot the session took is embedded in it as a
base64 data URL, so copying the .jsonl copies the images with it. This script says how many
and how large, so "the pictures were archived too" is a measured claim and not a hope.

    python tools/archive_qwen_run.py <session-id> [--piece <name>] [--label <text>]
    python tools/archive_qwen_run.py --all          # every qwen transcript not yet archived

Archived to `.mcptoolkit/runs/archive/E-qwen/<piece>--<session>.jsonl`, with a sibling
`<piece>--<session>.meta.json` holding the counts, cost and model so the corpus can be
measured without re-parsing every line.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

QWEN_PROJECTS = Path.home() / ".claude-qwen" / "projects"
ARCHIVE = Path(".mcptoolkit/runs/archive/E-qwen")
DATA_URL = re.compile(r'"data"\s*:\s*"([A-Za-z0-9+/=]{256,})"')


BRIEF_RE = re.compile(r"briefs[\\/]([a-z0-9_]+?)(?:_surface|_fitting)?\.md")


def _walk_images(node):
    """(count, base64 chars) of every image block anywhere under `node`."""
    n, b = 0, 0
    if isinstance(node, dict):
        if node.get("type") == "image":
            src = node.get("source") or {}
            n, b = 1, len(src.get("data") or "")
        for value in node.values():
            dn, db = _walk_images(value)
            n += dn
            b += db
    elif isinstance(node, list):
        for item in node:
            dn, db = _walk_images(item)
            n += dn
            b += db
    return n, b


def _piece_from(node):
    """The piece name out of the first prompt that names a brief file."""
    if isinstance(node, str):
        m = BRIEF_RE.search(node)
        return m.group(1) if m else None
    if isinstance(node, dict):
        for value in node.values():
            got = _piece_from(value)
            if got:
                return got
    elif isinstance(node, list):
        for item in node:
            got = _piece_from(item)
            if got:
                return got
    return None


def summarise(path: Path) -> dict:
    """Count what is in a transcript without holding it all in memory twice."""
    images, image_bytes, turns, tools = 0, 0, 0, {}
    models, cost, piece, session = set(), None, None, path.stem
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            msg = row.get("message") or {}
            if row.get("type") == "assistant":
                turns += 1
                if msg.get("model"):
                    models.add(msg["model"])
                for block in msg.get("content") or []:
                    if block.get("type") == "tool_use":
                        tools[block["name"]] = tools.get(block["name"], 0) + 1
            # Images ride anywhere in the row, and a picture is RE-SENT on later turns, so the
            # whole row is walked and every occurrence counted. Counting only the first copy
            # would understate what the archive actually carries - blaze_halo holds 6 image
            # blocks for 3 distinct screenshots.
            # The WHOLE row, not just message.content: a screenshot also survives in the
            # sibling `toolUseResult` record, and both copies are bytes this archive carries.
            found = _walk_images(row)
            images += found[0]
            image_bytes += found[1]
            if piece is None and row.get("type") == "user":
                piece = _piece_from(msg.get("content"))
            if row.get("type") == "result":
                cost = row.get("total_cost_usd")
    # DID THIS RUN PRODUCE ANYTHING? A session that stalled - hit a `!` the brief would not let it
    # force, ran out of turns, or was killed - built and painted in Blockbench and then exited
    # without calling save, so nothing of it reached the pack. Those runs are worth keeping while
    # you are diagnosing why they stalled and worth pruning afterwards, so the fact is recorded
    # rather than guessed at: `--prune-unsaved` deletes exactly the ones with `saved: false`.
    saved = tools.get("mcp__blockbench__armorpieces_save", 0) > 0
    return {
        "session": session, "piece": piece, "turns": turns, "images": images,
        "image_b64_bytes": image_bytes, "models": sorted(models), "cost_usd": cost,
        "saved": saved,
        "tool_calls": dict(sorted(tools.items(), key=lambda kv: -kv[1])),
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def archive_one(src: Path, piece_override=None, label=None) -> dict:
    info = summarise(src)
    piece = piece_override or info["piece"] or "unknown"
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    dst = ARCHIVE / f"{piece}--{src.stem}.jsonl"
    shutil.copy2(src, dst)

    digest_src, digest_dst = sha256(src), sha256(dst)
    if digest_src != digest_dst:
        raise SystemExit(f"copy verify FAILED for {src} -> {dst}")

    meta = dict(info, piece=piece, label=label, source=str(src), archived=str(dst),
                bytes=dst.stat().st_size, sha256=digest_dst)
    (ARCHIVE / f"{piece}--{src.stem}.meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("session", nargs="?", help="session id (the .jsonl stem)")
    ap.add_argument("--piece", help="override the piece name in the archived filename")
    ap.add_argument("--label", help="free text kept in the meta file")
    ap.add_argument("--all", action="store_true", help="archive every transcript not yet archived")
    args = ap.parse_args()

    # NO PRUNE COMMAND HERE, DELIBERATELY. A `--prune-unsaved` existed for about ten minutes on
    # 2026-09-10 and immediately over-deleted: asked to drop two stalled Village runs, it also took
    # three older ones that merely never called save - a read-only canary probe among them, which
    # was the only record of a finished investigation. "Never saved" is a poor proxy for
    # "worthless". Deciding which runs to drop is the author's call, made per run; this script
    # records `saved` in each meta so that call is easy, and deletes nothing on its own.

    candidates = sorted(QWEN_PROJECTS.glob("*/*.jsonl"))
    if not candidates:
        raise SystemExit(f"no qwen transcripts under {QWEN_PROJECTS}")

    if args.session:
        picks = [p for p in candidates if p.stem == args.session]
        if not picks:
            raise SystemExit(f"no transcript {args.session} under {QWEN_PROJECTS}")
    elif args.all:
        done = {p.name.split("--", 1)[1][:-6] for p in ARCHIVE.glob("*--*.jsonl")} \
            if ARCHIVE.exists() else set()
        picks = [p for p in candidates if p.stem not in done]
        if not picks:
            print("nothing new to archive")
            return 0
    else:
        raise SystemExit("give a session id, or --all")

    total_images = 0
    for src in picks:
        # A near-empty transcript is a /clear or a settings poke, not a run.
        if src.stat().st_size < 4096:
            print(f"  skip {src.stem}  (only {src.stat().st_size} bytes - not a run)")
            continue
        meta = archive_one(src, args.piece, args.label)
        total_images += meta["images"]
        cost = f"${meta['cost_usd']:.4f}" if meta["cost_usd"] else "-"
        print(f"  {meta['piece']:<18} {meta['session'][:8]}  {meta['bytes']:>9,}B  "
              f"{meta['turns']:>3} turns  {meta['images']:>2} img "
              f"({meta['image_b64_bytes']/1024:.0f}KB b64)  {cost}  "
              f"{','.join(meta['models']) or '-'}")
    print(f"\n-> {ARCHIVE}  ({total_images} images carried inside the transcripts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
