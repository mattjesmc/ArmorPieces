"""Put every pack under packs/ into the Blockbench plugin's `armorpieces_packs` setting - a
Blockbench setting, not a repo file (main-pack-split.md, "still owed"; RUNNING.md, "the qwen
driver") - through one window's risky_eval. Without it a piece in a pack cannot be reopened by
name and nothing fails loudly.

    python tools/register_packs.py <port> [<session id>]

The session id must be one the window will serve: a window held by a live session refuses every
other id (plugin 0.12), so the batch driver calls this with its OWN id on the window it was given.
Idempotent; prints what it added.
"""
import glob
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"legacy", "vlm-scratch"}

port = sys.argv[1] if len(sys.argv) > 1 else "25802"
sid = sys.argv[2] if len(sys.argv) > 2 else "ab-observer"
packs = sorted(os.path.basename(d) for d in glob.glob(os.path.join(ROOT, "packs", "*"))
               if os.path.isdir(d) and os.path.basename(d) not in SKIP)
want = []
for p in packs:
    want.append(os.path.join(ROOT, "packs", p, "datapack"))
    want.append(os.path.join(ROOT, "packs", p, "resourcepack"))

code = """
var want = WANT;
var list = []; try { list = JSON.parse(Settings.get('armorpieces_packs') || '[]') || []; } catch (e) { list = []; }
if (!Array.isArray(list)) list = [];
var added = [];
want.forEach(function (d) { if (list.indexOf(d) === -1) { list.push(d); added.push(d); } });
var kept = list.filter(function (d) { return d.indexOf('legends') === -1; });
if (added.length || kept.length !== list.length) { settings['armorpieces_packs'].set(JSON.stringify(kept)); Settings.save(); }
JSON.stringify({ added: added, total: kept.length })
""".replace("WANT", json.dumps(want))

body = json.dumps({"tool": "risky_eval", "args": {"code": code},
                   "session": {"id": sid, "client": "armorpieces", "profile": "kit"}}).encode()
req = urllib.request.Request(f"http://127.0.0.1:{port}/cmd", data=body,
                             headers={"Content-Type": "application/json", "X-MCPTK-Session": sid})
try:
    print("register_packs:", urllib.request.urlopen(req, timeout=30).read().decode()[:1500])
except Exception as e:  # never kill the batch over the pack list
    print("register_packs: FAILED", e)
