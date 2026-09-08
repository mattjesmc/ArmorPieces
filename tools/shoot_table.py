"""
Shoot the gallery's advanced smithing table picture: the table on the studio floor with a dressed
stand beside it, and the table's own screen holding that same suit.

The screen is the whole point of the block - a set worn by a stand, every socket, fitting and trim
of one piece as a row of icons - and a screen only exists on top of the world it dims. A real
screenshot of it is therefore a picture of a dark grey figure behind a menu, which says nothing
about the armor. So this takes TWO frames from ONE camera, one with the menu closed and one with it
open, and sets the screen's own rectangle, lifted at 1:1 out of the frame it was drawn in, on the
undimmed world beside the table. Nothing is scaled, recoloured or redrawn: every pixel is the
game's, and the only lie is that the world behind an open menu is not darkened.

The suit is `high_court` from `/armorpieces stage set` - a hand-built set, the same one every time,
which is what a page's screenshot needs - and it is put in the table the way a player would: the
four pieces into the display slots, a Lames Shoulder template and an amethyst shard into the input
slots, the chestplate picked and its pauldrons row picked under it. So the picture shows both of
the table's answers at once: Apply lit over a part on its way in, and Remove over the socket it
would come out of.

Needs the dev client running with the mcptoolkit mod (`./gradlew runClient`), on a world with a
flat white studio floor around STAGE - the same one the other gallery shots are taken on. Run with
the game's window at 3840x2131 or thereabouts; the crop is taken in fractions of the frame, and the
screen is pasted at whatever size the game drew it.

Usage:
    python tools/shoot_table.py [out.png]        # default docs/assets/gallery/table.png
"""

import base64
import json
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

BRIDGE = "http://127.0.0.1:25599/cmd"

SET = "high_court"
STAGE = (200, 100, 260)        # where the set is staged to be undressed, well out of frame
TABLE = (183, 100, 244)        # the block
FIGURE = (184.9, 100, 244.5)   # the stand beside it, facing the camera
BACKDROP = (172, 100, 240, 196, 112, 240)   # a white wall, so the shot has no sky in it
CAMERA = (184.3, 102.4, 248.6, 180, 20)     # x y z yaw pitch

# The screen is 242x220 GUI pixels (AdvancedSmithingScreen.IMAGE_WIDTH/HEIGHT) and its slots are
# named in the menu's own coordinates, so every click below is written as the menu writes it.
SCREEN_W, SCREEN_H = 242, 220
DISPLAY = [(8, 20), (8, 40), (8, 60), (8, 80)]     # the four armor slots, head to toe
INPUTS = [(187, 151), (205, 151)]                  # template, material
HOTBAR = [(8 + 18 * i, 196) for i in range(9)]
FIRST_ROW = (69, 28)           # the first socket row of the selected piece, on its part icon

# The world crop, as fractions of the frame: the table and the stand at the left, empty floor at
# the right for the screen to stand on.
CROP = (1150 / 3840, 0.0, 3700 / 3840, 1340 / 2131)
RIGHT_MARGIN = 0.071           # of the crop's width, between the screen and the right edge


def call(tool, args=None, timeout=30):
    req = urllib.request.Request(
        BRIDGE,
        data=json.dumps({"tool": tool, "args": args or {}}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        envelope = json.load(response)
    if not envelope.get("ok"):
        sys.exit(f"bridge error on {tool}: {envelope.get('error')}")
    return envelope["result"]


def cmd(command):
    return call("run_command", {"command": command}).get("output")


def player():
    """The name of the client's player - every command below is run as them."""
    source = call("get_entities", {"radius": 1}).get("source", "")
    if not source.startswith("player "):
        sys.exit("no client player: start the dev client and join a world first")
    return source.removeprefix("player ")


def shoot(path):
    result = call("screenshot")
    image = result.get("_image") or result
    Path(path).write_bytes(base64.b64decode(image["base64"]))
    return Image.open(path).convert("RGB")


def screen_origin():
    """Where the screen's top-left sits in the frame, in the FRAME's pixels.

    The menu reports its geometry in GUI pixels; the frame is that times the GUI scale, which is
    read here rather than assumed because it is chosen from the window size.
    """
    screen = call("get_screen", {"detail": "layout"})["screen"]
    return (screen["width"] - SCREEN_W) // 2, (screen["height"] - SCREEN_H) // 2, screen["width"]


def click_slot(origin, slot):
    call("click", {"x": origin[0] + slot[0] + 8, "y": origin[1] + slot[1] + 8})
    time.sleep(0.12)


def main(out):
    who = player()
    call("close_screen")
    # closing hands whatever was in the table back to the player, and it lands a tick or two later -
    # clear before that and the pieces come back as a second copy of everything put in below.
    time.sleep(0.5)
    cmd("armorpieces stage clear")
    cmd(f"clear {who}")
    cmd("time set 6000")
    cmd("weather clear")
    cmd("fill {} {} {} {} {} {} minecraft:white_concrete".format(*BACKDROP))
    cmd("setblock {} {} {} armorpieces:advanced_smithing_table".format(*TABLE))
    cmd(f"tp {who} " + " ".join(str(v) for v in CAMERA))

    # Dress a stand with the set, take the four pieces off it for the table, and stand it in shot.
    # `stage set` places its caption marker at the origin and the stand a row beyond it, so the
    # dressed one is the FURTHEST of the two.
    cmd(f"execute as {who} positioned {STAGE[0]} {STAGE[1]} {STAGE[2]} run armorpieces stage set {SET}")
    time.sleep(0.5)
    staged = (f"@e[type=armor_stand,tag=armorpieces_stage,x={STAGE[0]},y={STAGE[1]},z={STAGE[2]},"
              "distance=..8,limit=1,sort=furthest]")
    for i, piece in enumerate(["armor.head", "armor.chest", "armor.legs", "armor.feet"]):
        cmd(f"item replace entity {who} hotbar.{i} from entity {staged} {piece}")
    cmd(f"give {who} armorpieces:pauldrons_template[armorpieces:decoration=\"armorpieces:lames\"] 1")
    cmd(f"give {who} minecraft:amethyst_shard 1")
    cmd(f"tp {staged} {FIGURE[0]} {FIGURE[1]} {FIGURE[2]} 0 0")
    cmd("kill @e[type=armor_stand,tag=armorpieces_stage,"
        f"x={STAGE[0]},y={STAGE[1]},z={STAGE[2]},distance=..8]")
    time.sleep(0.8)
    world = shoot("table_world.png")

    cmd(f"execute as {who} run armorpieces table")
    time.sleep(0.8)
    left, top, width = screen_origin()
    origin = (left, top)
    for hotbar, slot in zip(HOTBAR, DISPLAY + INPUTS):
        click_slot(origin, hotbar)   # pick the piece up
        click_slot(origin, slot)     # and put it where it goes
    call("click", {"index": 1})      # work on the chestplate
    time.sleep(0.3)
    call("click", {"x": left + FIRST_ROW[0], "y": top + FIRST_ROW[1]})   # and on its first socket
    time.sleep(0.8)
    frame = shoot("table_screen.png")

    scale = frame.width // width
    box = (left * scale, top * scale, (left + SCREEN_W) * scale, (top + SCREEN_H) * scale)
    menu = frame.crop(box)

    crop = world.crop((round(CROP[0] * world.width), round(CROP[1] * world.height),
                       round(CROP[2] * world.width), round(CROP[3] * world.height)))
    crop.paste(menu, (crop.width - menu.width - round(RIGHT_MARGIN * crop.width),
                      (crop.height - menu.height) // 2))
    crop.save(out)
    Path("table_world.png").unlink()
    Path("table_screen.png").unlink()
    print(out, crop.size)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/assets/gallery/table.png")
