"""Grab the game framebuffer at native size straight from the toolkit bridge and save it as PNG.

    python snap.py out.png
"""
import base64, json, sys, urllib.request

out = sys.argv[1]
req = urllib.request.Request(
    "http://127.0.0.1:25599/cmd",
    data=json.dumps({"tool": "screenshot", "args": {}}).encode(),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=30) as r:
    env = json.load(r)
if not env.get("ok"):
    sys.exit(f"bridge error: {env}")
res = env["result"]
img = res.get("_image") or res
data = base64.b64decode(img["base64"])
with open(out, "wb") as f:
    f.write(data)
print(out, res.get("width"), res.get("height"), len(data), "bytes")
