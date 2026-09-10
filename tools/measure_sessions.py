"""Archive every part-authoring transcript, and measure them side by side.

A part session is one headless `claude -p --agent part-author*` run that built one piece. Three
eras of tooling produced them, and the transcripts are the only record of what each cost:

    A  one server      tools/mcp/server.mjs served Blockbench itself; every call is
                       `mcp__blockbench__*` (2026-09-03)
    B  kit split       the toolkit's shim serves Blockbench, the proxy keeps its nine piece tools;
                       Blockbench is still the THIRD-PARTY plugin, so the names are the old 94
                       (`paint_with_brush`, `remove_element`, ...) (2026-09-05..09-06)
    C  own plugin      same split, but Blockbench is mcp-toolkit's own bridge: 26 tools, families
                       behind an `op` (`element`, `texture`, `inspect`) (2026-09-07)
    D  own id          the same 26 tools, but each session presents its OWN identity: mcp-toolkit
                       0.136.0 / shim 0.66.0 derives the session id from the PARENT process, so
                       concurrent sessions no longer share one binding (2026-09-07 evening)
    E  a window each    the same 26 tools again, but mcp-toolkit 0.140.0 / shim 0.68.0 / plugin
                       0.6.0 gives each session its OWN Blockbench window, which is what finally made
                       concurrency pay (2026-09-08 evening onwards)

The eras are detected from the tool NAMES a session actually called, not from its date, so a
re-run of an old session is classified by what it used. C and D are the one exception, and it is
deliberate: they call the same tools, and what changed is who each session says it IS. That
boundary is therefore a date - and `shared_id` in the output is the evidence that says whether the
change took, because the plugin writes a note into the reply whenever one id arrives on two live
sockets. A D run with `shared_id` true is a D run in name only.

    python tools/measure_sessions.py            # measure, print the tables
    python tools/measure_sessions.py --archive  # also copy the transcripts somewhere durable

Transcripts live in ~/.claude/projects/<slug>/, which is not ours and is not backed up. --archive
copies them under .mcptoolkit/runs/archive/<era>/ and writes measurements.json beside them.
"""
import argparse
import collections
import datetime
import glob
import io
import json
import os
import re
import shutil

HOME = os.path.expanduser("~")
PROJECT = os.path.join(HOME, ".claude", "projects", "C--Users-Matthijs-ArmorPieces")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(REPO, ".mcptoolkit", "runs", "archive")

# $/Mtok: input, output, cache write (1.25x input), cache read (0.1x input)
RATES = {"sonnet": (2.0, 10.0, 2.50, 0.20), "opus": (5.0, 25.0, 6.25, 0.50)}

# Era C ends and D begins at the 0.136.0 publish (2026-09-07 20:00 local). See the docstring for why
# this one boundary is a clock and not a tool name.
OWN_ID_FROM = 1788804000

# Era D ends and E begins at the 0.140.0 publish (2026-09-08 18:00 local) - "a window each". Like the
# C/D boundary this one is a clock, and for the same reason: D and E call the same 26 tools and what
# changed is the window each session is given, which a transcript does not name.
WINDOW_EACH_FROM = 1788883200

# What the plugin says when one session id arrives on more than one live socket - the failure the
# parent-process identity exists to prevent, and so the falsifier for era D.
SHARED_NOTE = "connections; one binding cannot tell them apart"
# Session ids as they appear in any reply that names them (`project op:list`, the note above).
# Only the SHAPED ids: a bare `armorpieces` matches this mod's own namespace in half the
# replies in the corpus, which made every era look identity-stamped when none of them were.
SESSION_ID = re.compile(r"\b(?:mcptk-\d+|shim-\d+)\b")
# ...but an id in a reply is not necessarily THIS session's. A `held_by` refusal names the HOLDER,
# which is by definition somebody else - so scooping every id out of every body filed the REFUSED
# session of the 2026-09-08 concurrency A/B under the other one's id (mcptk-13676 for what was
# really mcptk-99264). The distinct-id column is what proves a row is era D at all, so that was the
# falsifier's own column reading the wrong process. Two contexts are read apart from the rest: what
# a session says about ITSELF (ping's blockbench block; the shared-id note, which quotes the
# caller's id because it is the caller's id that is shared), and what it quotes about ANOTHER (the
# refusal, in the plugin's sentence and in holderBlock's JSON). An own stamp wins; failing that, an
# id that only ever appeared inside somebody else's refusal is not evidence of identity, and a row
# is left with NO id rather than the wrong one. Written without escapes so the two shapes read as
# the JSON and the sentence they match.
OWN_ID = re.compile(
    '"blockbench"[ ]*:[ ]*[{][^{}]*?"session"[ ]*:[ ]*"(mcptk-[0-9]+|shim-[0-9]+)"'
    '|session id "(mcptk-[0-9]+|shim-[0-9]+)" is held by')
HELD_BY_ID = re.compile(
    'held_by:[ ]*session[ ]+(mcptk-[0-9]+|shim-[0-9]+)'
    '|"held_by"[ ]*:[ ]*[{][^{}]*?"session"[ ]*:[ ]*"(mcptk-[0-9]+|shim-[0-9]+)"')

# Names only the new plugin has, and names only the old one had.
NEW_ONLY = {"element", "texture", "inspect", "project", "apply_texture", "export_model", "animation"}
OLD_ONLY = {"remove_element", "rename_element", "duplicate_element", "paint_with_brush",
            "paint_fill_tool", "draw_shape_tool", "gradient_tool", "eraser_tool",
            "color_picker_tool", "texture_selection", "paint_settings", "activate_texture",
            "save_checkpoint"}


def rows(path):
    for line in io.open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except Exception:
            continue


def first_user_text(rs):
    for r in rs:
        if r.get("type") != "user":
            continue
        c = (r.get("message") or {}).get("content")
        if isinstance(c, str):
            return c
        if isinstance(c, list):
            return " ".join(x.get("text", "") for x in c if isinstance(x, dict))
    return ""


def measure(path):
    rs = list(rows(path))
    if not rs:
        return None
    prompt = first_user_text(rs)
    if "docs/plans/briefs/" not in prompt and "docs\\plans\\briefs\\" not in prompt:
        return None
    norm = prompt.replace("\\", "/")
    i = norm.find("briefs/")
    piece = norm[i + 7:norm.find(".md", i)] if i > 0 else "?"
    if not piece or "/" in piece or len(piece) > 40:
        return None

    tools = collections.Counter()
    tin = tout = cw = cr = 0
    assistant = 0
    stamps = []
    # Identity, read out of the replies rather than assumed - see the docstring.
    shared = False
    ids = set()
    own = set()
    held = set()
    for r in rs:
        ts = r.get("timestamp")
        if ts:
            stamps.append(ts)
        m = r.get("message") or {}
        u = m.get("usage") or {}
        if u:
            assistant += 1
            tin += u.get("input_tokens", 0) or 0
            tout += u.get("output_tokens", 0) or 0
            cw += u.get("cache_creation_input_tokens", 0) or 0
            cr += u.get("cache_read_input_tokens", 0) or 0
        c = m.get("content")
        if isinstance(c, list):
            for x in c:
                if not isinstance(x, dict):
                    continue
                if x.get("type") == "tool_use":
                    tools[x.get("name", "?")] += 1
                elif x.get("type") == "tool_result":
                    body = x.get("content")
                    if isinstance(body, list):
                        body = " ".join(b.get("text", "") for b in body if isinstance(b, dict))
                    if isinstance(body, str):
                        if SHARED_NOTE in body:
                            shared = True
                        ids.update(SESSION_ID.findall(body))
                        own.update(i for g in OWN_ID.findall(body) for i in g if i)
                        held.update(i for g in HELD_BY_ID.findall(body) for i in g if i)

    bare = {n.split("__")[-1] for n in tools if n.startswith("mcp__")}
    # C and D call the same 26 tools, so this boundary cannot be read off the names. It IS readable
    # off the replies whenever one names a session: a `mcptk-` id can only come from a 0.136.0 shim.
    # That evidence outranks the clock - dating alone filed the 2026-09-08 dragon_knuckles run that
    # called no distinctive tool as C, id `mcptk-104264` and all, because the date rule it fell
    # through to was the OLD one.
    # Prefer the session's OWN stamp over any id quoted inside a refusal (see OWN_ID).
    ids = own or (ids - held)
    own_id = any(i.startswith("mcptk-") for i in ids)
    dated_d = own_id or os.path.getmtime(path) >= OWN_ID_FROM
    dated_e = os.path.getmtime(path) >= WINDOW_EACH_FROM
    own_era = "E a window each" if dated_e else "D own id"
    if bare & NEW_ONLY:
        era = own_era if dated_d else "C own plugin"
    elif bare & OLD_ONLY:
        era = "B kit split"
    elif any(n.startswith("mcp__blockbench__") and not n.split("__")[-1].startswith("armorpieces_")
             for n in tools):
        era = "A one server"
    elif any(n.startswith("mcp__mcptoolkit__") for n in tools):
        # Kit split, but it called nothing distinctive - date it by the switchover instead of
        # guessing, so a short session is not filed under the wrong plugin. A session that named an
        # id is not guessed at at all.
        era = (own_era if dated_d
               else "C own plugin" if os.path.getmtime(path) >= 1788775200
               else "B kit split")
    else:
        era = "B kit split"

    # Every part session so far ran on Sonnet unless its own transcript says otherwise.
    model = next((m.get("message", {}).get("model") for m in rs
                  if (m.get("message") or {}).get("model")), "") or ""
    tier = "opus" if "opus" in model or "fable" in model else "sonnet"
    ri, ro, rw, rr = RATES[tier]
    cost = tin * ri / 1e6 + tout * ro / 1e6 + cw * rw / 1e6 + cr * rr / 1e6

    mins = None
    if len(stamps) >= 2:
        try:
            a = datetime.datetime.fromisoformat(min(stamps).replace("Z", "+00:00"))
            b = datetime.datetime.fromisoformat(max(stamps).replace("Z", "+00:00"))
            mins = round((b - a).total_seconds() / 60, 1)
        except Exception:
            pass

    bb = {n: c for n, c in tools.items() if n.startswith("mcp__")}
    return dict(piece=piece, era=era, file=os.path.basename(path), model=model, tier=tier,
                mtime=datetime.datetime.fromtimestamp(os.path.getmtime(path)).isoformat(" ", "seconds"),
                minutes=mins, assistant_turns=assistant, tool_calls=sum(tools.values()),
                bridge_calls=sum(bb.values()), bridge=dict(sorted(bb.items())),
                other_calls=sum(tools.values()) - sum(bb.values()),
                shared_id=shared, session_ids=sorted(ids), refused_by=sorted(held - ids),
                out=tout, cache_write=cw, cache_read=cr, cost=round(cost, 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", action="store_true", help="copy transcripts under .mcptoolkit/runs/archive/")
    args = ap.parse_args()

    found = []
    for f in glob.glob(os.path.join(PROJECT, "*.jsonl")):
        m = measure(f)
        if m:
            found.append(m)
    # Also the stream-json logs the 09-06 runs wrote into the repo.
    for f in glob.glob(os.path.join(REPO, ".mcptoolkit", "runs", "*.jsonl")):
        m = measure(f)
        if m:
            found.append(m)
    found.sort(key=lambda m: (m["era"], m["mtime"]))

    print(f"{'era':15}{'piece':20}{'min':>6}{'turns':>7}{'bridge':>8}{'out kt':>8}{'cache-rd Mt':>12}{'$':>7}  id")
    for m in found:
        # The id column is the evidence, not decoration: "SHARED" here means this session was not
        # alone in its identity whatever era it is filed under.
        idcol = "SHARED" if m["shared_id"] else (",".join(m["session_ids"]) or "-")
        # A session that never stamped its own id but WAS refused by one still met another
        # session, which is evidence about the run even though it is not this row's identity.
        if not m["shared_id"] and not m["session_ids"] and m["refused_by"]:
            idcol = "- (refused by " + ",".join(m["refused_by"]) + ")"
        print(f"{m['era']:15}{m['piece']:20}{(m['minutes'] or 0):6.1f}{m['assistant_turns']:7d}"
              f"{m['bridge_calls']:8d}{m['out']/1000:8.0f}{m['cache_read']/1e6:12.1f}{m['cost']:7.2f}  {idcol}")

    print()
    print(f"{'era':15}{'n':>3}{'min':>7}{'turns':>7}{'bridge':>8}{'out kt':>8}{'cache-rd Mt':>12}{'$ each':>8}")
    for era in sorted({m["era"] for m in found}):
        g = [m for m in found if m["era"] == era]
        n = len(g)
        avg = lambda k: sum(m[k] or 0 for m in g) / n
        shared = sum(1 for m in g if m["shared_id"])
        print(f"{era:15}{n:3d}{avg('minutes'):7.1f}{avg('assistant_turns'):7.1f}{avg('bridge_calls'):8.1f}"
              f"{avg('out')/1000:8.0f}{avg('cache_read')/1e6:12.1f}{avg('cost'):8.2f}"
              + (f"  {shared} shared id" if shared else ""))

    if args.archive:
        os.makedirs(ARCHIVE, exist_ok=True)
        for m in found:
            era_dir = os.path.join(ARCHIVE, m["era"].split()[0])
            os.makedirs(era_dir, exist_ok=True)
            src = os.path.join(PROJECT, m["file"])
            if not os.path.exists(src):
                src = os.path.join(REPO, ".mcptoolkit", "runs", m["file"])
            dst = os.path.join(era_dir, f"{m['piece']}--{m['file']}")
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
        with io.open(os.path.join(ARCHIVE, "measurements.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(found, fh, indent=1)
        total = sum(os.path.getsize(os.path.join(r, f))
                    for r, _, fs in os.walk(ARCHIVE) for f in fs)
        print(f"\narchived {len(found)} transcripts to {ARCHIVE} ({total / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
