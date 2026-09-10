"""Tier 3: what the mod DRAWS and what its screens say, asked of a running client.

Everything below the render layer can be asserted as a number. This tier cannot: an armor piece is
right when it looks right, and the only honest machine version of that is "it has not changed since
a person looked at it". So half of what is here is a frame compared against a golden (`frames.py`),
and half is a question a screen can answer in words - a tooltip's lines, a menu's slots - which is
worth more than a picture wherever it exists, because it says WHY it failed.

Three things about this tier are decided by the toolkit and are worth knowing before reading on:

  * **The studio is the only stable background.** `studio {entity, equipment}` stands a living
    subject on a white floor with no sky and flat light, freezes the tick, and `render` photographs
    it out of band at a fixed resolution - no HUD, no window size, no animation phase. Two shots of
    one subject came back bit-identical, which is what makes a golden worth keeping at all.
  * **The subject is an armor stand, and the tick is NOT frozen.** Both halves were measured the
    hard way on 2026-09-10. A stand is the only humanoid that holds perfectly still on its own: a
    player and a zombie both carry vanilla's idle arm bob, which is driven by `ageInTicks` - and
    since the PARTIAL tick keeps advancing even under `/tick freeze`, their arms drift by around a
    thousand pixels between two frames, which is more than a whole small piece is worth. And
    freezing does not only fail to help: **under a frozen tick the decorations on the LEG bones stop
    drawing entirely** - tassets, knees, spurs and greaves, measured at zero pixels of difference on
    a stand, a zombie and a real player alike, while the head, body and arm sockets keep drawing. A
    frozen golden of those four would have been a photograph of plain armor, passing for ever.
  * **The studio has to be swept first.** It is a real dimension in a real world: an item dropped
    there by an earlier scene lies on the floor SPINNING, which is a moving object in the frame and
    the one thing that made an otherwise identical shot differ.
  * **A menu answers in words.** The advanced table's result lives in a real slot (`PREVIEW_SLOT`,
    index 6), so what a recipe produced can be read with `get_tooltip {slot: 6}` rather than
    photographed - which is how the four smithing rows here assert an OUTPUT rather than a picture
    of one.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from PIL import Image

from .bridge import Bridge, BridgeError
from .frames import Goldens, _difference

ROOT = Path(__file__).resolve().parent.parent.parent
LANG = ROOT / "src" / "main" / "resources" / "assets" / "armorpieces" / "lang" / "en_us.json"

#: The mod's own data, read from the tree rather than from the game: a scene that asked the game
#: what it loaded and then asserted on the answer would pass on an empty registry.
PARTS = ROOT / "src" / "main" / "resources" / "data" / "armorpieces" / "armorpieces" / "armor_decoration"

#: How every golden frame is taken. The yaw is the one number here that is not taste: the studio
#: stands its subject facing the corner it puts the CLIENT in, which is -x -z, so the camera belongs
#: at yaw -45. Shooting from +x +z (yaw 135) photographs the figure's BACK - and a socket on the
#: front of a leg then draws behind the leg and measures as nothing at all, which is a whole
#: afternoon of believing the mod had stopped drawing four of its twelve sockets.
FRAME = {"yaw": -45, "pitch": 0, "width": 640, "height": 640, "downscale": 2}

#: The subject. See the class note - it is a stand because a stand does not move.
FIGURE = "minecraft:armor_stand"

#: The dimension `studio` stands its subject in. Named here because sweeping it needs a command,
#: and a command runs in the overworld unless it is told otherwise.
STUDIO = "mcptoolkit:studio"

#: One part per socket, pinned rather than picked: a golden is worth keeping only if the same
#: subject stands in it next year. A part that leaves the mod fails the scene by name, which is the
#: right way to be told.
PER_ANCHOR = {
    "crest": ("head", "brush_crest"),
    "brow": ("head", "circlet"),
    "horns": ("head", "helm_wings"),
    "pauldrons": ("chest", "spaulders"),
    "back": ("chest", "cloak"),
    "collar": ("chest", "gorget"),
    "vambraces": ("chest", "vambraces"),
    "belt": ("legs", "buckled_belt"),
    "tassets": ("legs", "tassets"),
    "knees": ("legs", "poleyns"),
    "spurs": ("feet", "rowel_spurs"),
    "greaves": ("feet", "greaves"),
}

#: The eight armor materials a skin is baked against (`tools/bake_skin.py`), and the item each is
#: photographed on. Turtle scute has only ever been a helmet, which is why it is not a chestplate.
MATERIALS = {
    "leather": "leather",
    "chainmail": "chainmail",
    "iron": "iron",
    "gold": "golden",
    "diamond": "diamond",
    "netherite": "netherite",
    "copper": "copper",
    "turtle_scute": "turtle",
}

#: The sockets a camera in front cannot see. A cloak hangs down the back and a spur sits on the
#: heel, so those two are photographed from behind - one camera cannot have both sides of a figure,
#: and a frame of the side a piece is not on is a frame of nothing.
BEHIND = {"back", "spurs"}

IRON = {"head": "minecraft:iron_helmet", "chest": "minecraft:iron_chestplate",
        "legs": "minecraft:iron_leggings", "feet": "minecraft:iron_boots"}

#: How many pixels a piece has to be worth against the same figure without it. The smallest thing
#: the mod draws - a pair of greaves on a stand's shins - measured 444 at this framing; the
#: threshold is well under that and far over the noise, which is zero.
MIN_DRAWN = 60


class Failed(AssertionError):
    """A scene's assertion did not hold. The message is what the game said."""


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise Failed(message)


def lang() -> dict:
    return json.loads(LANG.read_text(encoding="utf-8"))


def named(key: str) -> str:
    """What `en_us.json` says a thing is called - the string a tooltip has to end up printing."""
    names = lang()
    if key not in names:
        raise Failed(f"{key} is not in en_us.json, so nothing here knows what to expect")
    return names[key]


# ---------------------------------------------------------------------------------------------
# Item syntax: the /give form of everything this mod puts on a stack
# ---------------------------------------------------------------------------------------------


def components(item: str, *added: str) -> str:
    """An item plus components, merged into ONE bracket list.

    Item syntax has exactly one component list: {@code helmet[a=1][b=2]} is not a stack with two
    components, it is a parse error - and the game refuses the whole command rather than half of it.
    So every helper below goes through here, and a skinned chestplate that is also clothed comes out
    as one list.
    """
    name, bracket, existing = item.partition("[")
    already = [existing.rstrip("]")] if bracket and existing.strip("]") else []
    return f"{name}[{','.join([*already, *added])}]"


def decorated(item: str, anchor: str, part: str, *, material: str = "minecraft:gold",
              fittings: str = "") -> str:
    """Armor wearing one piece, written the way a player would type it."""
    socket = f'{anchor}:{{material:"{material}",decoration:"{part}"'
    socket += f",fittings:{{{fittings}}}}}" if fittings else "}"
    return components(item, f"armorpieces:decorations={{{socket}}}")


def skinned(item: str, skin: str) -> str:
    return components(item, f'armorpieces:skin="{skin}"')


def clothed(item: str, cloth: str, base: str = "red", patterns: str = "") -> str:
    value = f'{{cloth:"{cloth}",base:"{base}"'
    value += f",patterns:[{patterns}]}}" if patterns else "}"
    return components(item, f"armorpieces:cloth={value}")


def suit(material: str = "iron", **overrides: str) -> dict:
    """A full set of one material, with any slot replaced by a written-out stack."""
    worn = {slot: f"minecraft:{material}_{piece}" for slot, piece in
            (("head", "helmet"), ("chest", "chestplate"), ("legs", "leggings"), ("feet", "boots"))}
    worn.update(overrides)
    return worn


# ---------------------------------------------------------------------------------------------
# The client
# ---------------------------------------------------------------------------------------------


@dataclass
class Client:
    """One attached client, the studio it stands things in, and the goldens it compares against."""

    bridge: Bridge
    goldens: Goldens
    out: Path
    player: str = ""
    pushed: list[str] = field(default_factory=list)
    staged: bool = False
    swept: bool = False
    #: Frames that did not match, or that no golden exists for. Collected rather than raised: the
    #: first frame of twelve is a bad place to stop, because what a person needs in order to bless
    #: or to diagnose is ALL of them, in one run.
    problems: list[str] = field(default_factory=list)

    # ---- the world -------------------------------------------------------------------------

    def out_lines(self, command: str) -> list[str]:
        result = self.bridge.command(command)
        lines = [str(line) for line in (result.get("output") or [])]
        if any("Unknown or incomplete command" in line for line in lines):
            raise Failed(f"the game does not know `{command}`: {lines}")
        return lines

    def who(self) -> str:
        """The client's own player - the one whose screens `get_screen` reads."""
        if not self.player:
            source = self.bridge.call("get_entities", radius=1).get("source", "")
            self.player = source.replace("player ", "").strip()
            expect(bool(self.player),
                   "the client has no player, so nothing here can open a screen: " + source)
        return self.player

    # ---- the studio ------------------------------------------------------------------------

    def figure(self, equipment: dict, *, entity: str = FIGURE, yaw: int = 135) -> dict:
        """Stand a subject on the white floor wearing these stacks, and let the frame settle.

        Deliberately NOT frozen; see the class note. What replaces the freeze is a sweep and a
        wait: the studio is a real dimension, and a stand takes a moment to reach the client.
        """
        box = self.bridge.call("studio", entity=entity, equipment=equipment, yaw=yaw, freeze=False)
        self.staged = True
        self.sweep(box["look_at"])
        self.bridge.command(f"execute in {STUDIO} run kill @e[type=minecraft:item]")
        time.sleep(1.2)
        return box["look_at"]

    def sweep(self, box: dict, reach: int = 16) -> None:
        """Empty the air around the studio floor, once per run.

        The studio is a REAL PLACE in a real world and it keeps what is left in it. A wall the icons
        scene built and did not take away, or a block dropped by a person driving this game by hand,
        stands beside the figure in every frame afterwards - which is how a whole set of goldens came
        to be blessed with a stray grey block in the corner of each. The floor itself is one block
        below the box and is not touched.
        """
        if self.swept:
            return
        self.swept = True
        low, high = box["min"], box["max"]
        self.bridge.command(
            f"execute in {STUDIO} run fill {low['x'] - reach} {low['y']} {low['z'] - reach} "
            f"{high['x'] + reach} {high['y'] + reach} {high['z'] + reach} minecraft:air replace")
        self.bridge.command(f"execute in {STUDIO} run kill @e[type=minecraft:item_frame]")

    def shot(self, name: str, box: dict, *, behind: bool = False) -> Path:
        """Photograph the staged subject, hold the frame against its golden, and hand it back."""
        # The subject's own column and nothing else. `render` stands back far enough to fit the BOX
        # it is given, so the studio's own 3x3x3 would put the figure in the middle of a lot of
        # white; two blocks from the floor up is the figure itself, feet to crest.
        centre = {"x": (box["min"]["x"] + box["max"]["x"]) // 2,
                  "z": (box["min"]["z"] + box["max"]["z"]) // 2}
        column = {
            "min": {"x": centre["x"], "y": box["min"]["y"], "z": centre["z"]},
            "max": {"x": centre["x"], "y": box["max"]["y"] - 1, "z": centre["z"]},
        }
        frame = dict(FRAME, yaw=FRAME["yaw"] + 180) if behind else FRAME
        reply = self.bridge.call("render", look_at=column, out=f"gate/tier3/{name}.png", **frame)
        taken = Path(reply["path"])
        expect(taken.is_file(), f"the render said it wrote {taken} and there is no such file")
        result = self.goldens.compare(name, taken)
        if result.status in ("FAIL", "new"):
            self.problems.append(result.note)
        return taken

    def drew(self, name: str, control: Path, taken: Path, least: int = MIN_DRAWN) -> None:
        """Assert that this frame is not the control frame - that SOMETHING was drawn.

        The golden beside this says the picture has not changed; this says the picture is not the
        picture of plain armor. They fail differently and that is the point: a socket that stopped
        drawing and a golden nobody has blessed since are the same red mark otherwise, and only one
        of them is a bug in the mod.
        """
        with Image.open(control) as before, Image.open(taken) as after:
            differing, _ = _difference(before.convert("RGB"), after.convert("RGB"))
        if differing < least:
            self.problems.append(
                f"{name} is the same picture as the undecorated figure ({differing} pixels differ, "
                f"and a piece is worth at least {least}): nothing was drawn for it. The frames are "
                f"{control} and {taken}.")

    def leave(self) -> None:
        if self.staged:
            try:
                self.bridge.call("studio", leave=True)
            except BridgeError:
                pass
            self.staged = False

    # ---- screens ---------------------------------------------------------------------------

    def tooltip(self, item: str, **args) -> list[str]:
        return [str(line) for line in self.bridge.call("get_tooltip", item=item, **args)["lines"]]

    def table(self) -> None:
        """Open the advanced smithing table's screen on the client, the way the command does."""
        self.bridge.call("close_screen")
        self.out_lines(f"execute as {self.who()} run armorpieces table")
        time.sleep(0.5)
        screen = self.bridge.call("get_screen").get("screen") or {}
        expect(screen.get("class") == "AdvancedSmithingScreen",
               f"`armorpieces table` opened {screen.get('class')!r} rather than the table's screen")

    def screen(self) -> dict:
        """The open screen with geometry AND slot contents - one call answers both."""
        return self.bridge.call("get_screen", detail="layout")

    def slots(self) -> dict:
        return {slot["index"]: slot for slot in self.screen()["menu"]["slots"]}

    def click_slot(self, index: int) -> None:
        """Click a container slot by its menu index.

        The slots a screen reports are in the MENU's own coordinates and the widgets are in the
        screen's, so a slot needs the menu's top-left added to it. The table's image is a fixed
        242x220 (`AdvancedSmithingMenu.IMAGE_WIDTH/HEIGHT`) centred in the screen, which is where
        that origin comes from.
        """
        screen = self.screen()
        left = (screen["screen"]["width"] - 242) // 2
        top = (screen["screen"]["height"] - 220) // 2
        slot = {s["index"]: s for s in screen["menu"]["slots"]}[index]
        self.bridge.call("click", x=left + slot["x"] + 8, y=top + slot["y"] + 8)
        time.sleep(0.25)

    def give(self, *items: str) -> None:
        for item in items:
            said = self.out_lines(f"give {self.who()} {item} 1")
            expect(any("Gave" in line for line in said),
                   f"the game would not give {item}: {said}")
        time.sleep(0.3)

    # ---- housekeeping ----------------------------------------------------------------------

    def push(self, path: str, content: dict | str) -> None:
        text = content if isinstance(content, str) else json.dumps(content, indent=2)
        self.bridge.push(path, text, reload=True)
        self.pushed.append(path)

    def restore(self) -> None:
        """Undo everything a scene did to the client. Called in a finally, always."""
        self.problems.clear()
        self.leave()
        try:
            self.bridge.call("close_screen")
        except BridgeError:
            pass
        try:
            self.bridge.command(f"clear {self.who()}")
        except (BridgeError, Failed):
            pass
        while self.pushed:
            path = self.pushed.pop()
            try:
                self.bridge.clear(path, reload=not self.pushed)
            except BridgeError:
                pass


@dataclass
class Scene:
    name: str
    what: str
    run: Callable[[Client], None]


SCENES: list[Scene] = []


def scene(name: str, what: str):
    def register(function: Callable[[Client], None]) -> Callable[[Client], None]:
        SCENES.append(Scene(name, what, function))
        return function

    return register


# ---------------------------------------------------------------------------------------------
# What the mod draws
# ---------------------------------------------------------------------------------------------


@scene("layer", "every socket draws: one golden frame per anchor, on a figure in iron")
def layer(client: Client) -> None:
    missing = [part for _, part in PER_ANCHOR.values()
               if not (PARTS / f"{part}.json").is_file()]
    expect(not missing,
           f"this scene photographs {missing}, which the mod no longer ships. Pin another part per "
           "anchor in PER_ANCHOR and bless the new frames - a golden of a part that is gone is not "
           "a check of anything.")
    # The same figure with nothing on it, which is both a golden of its own and the control every
    # socket below is measured against.
    box = client.figure(suit())
    control = client.shot("layer-plain", box)
    behind = client.shot("layer-plain-behind", box, behind=True)
    for anchor, (slot, part) in PER_ANCHOR.items():
        worn = suit()
        worn[slot] = decorated(IRON[slot], anchor, f"armorpieces:{part}")
        back = anchor in BEHIND
        taken = client.shot(f"layer-{anchor}", client.figure(worn), behind=back)
        client.drew(f"layer-{anchor}", behind if back else control, taken)


@scene("skins", "one skin across all eight armor materials, one golden frame each")
def skins(client: Client) -> None:
    for material, item in MATERIALS.items():
        if item == "turtle":
            worn = {"head": skinned("minecraft:turtle_helmet", "armorpieces:plate")}
        else:
            worn = {slot: skinned(f"minecraft:{item}_{piece}", "armorpieces:plate")
                    for slot, piece in (("head", "helmet"), ("chest", "chestplate"),
                                        ("legs", "leggings"), ("feet", "boots"))}
        bare = {slot: item.split("[")[0] for slot, item in worn.items()}
        control = client.shot(f"skin-none-{material}", client.figure(bare))
        taken = client.shot(f"skin-plate-{material}", client.figure(worn))
        client.drew(f"skin-plate-{material}", control, taken)


@scene("cloth", "a garment worn on the chest, drawn over the chest AND the leggings")
def cloth(client: Client) -> None:
    # The claim worth a picture is not that a tunic draws - it is that a garment stored on the CHEST
    # stack is drawn on the leggings sheet too (EquipmentLayerRendererMixin reads the chest slot
    # while drawing the legs). Every frame here is a full iron set with the cloth on the chest only.
    control = client.shot("cloth-none", client.figure(suit()))
    for name, worn in {
        "tunic": suit(chest=clothed("minecraft:iron_chestplate", "armorpieces:tunic")),
        "tabard": suit(chest=clothed("minecraft:iron_chestplate", "armorpieces:tabard", "blue")),
        "tunic-on-skin": {
            "head": skinned("minecraft:iron_helmet", "armorpieces:plate"),
            "chest": clothed(skinned("minecraft:iron_chestplate", "armorpieces:plate"),
                             "armorpieces:tunic"),
            "legs": skinned("minecraft:iron_leggings", "armorpieces:plate"),
            "feet": skinned("minecraft:iron_boots", "armorpieces:plate"),
        },
        "tabard-patterned": suit(chest=clothed(
            "minecraft:iron_chestplate", "armorpieces:tabard", "white",
            patterns='{pattern:"minecraft:cross",color:"red"}')),
    }.items():
        taken = client.shot(f"cloth-{name}", client.figure(worn))
        client.drew(f"cloth-{name}", control, taken)


@scene("fittings", "a fitting's own colour reaches the model: dye and banner, one frame each")
def fittings(client: Client) -> None:
    # The two fittings that carry a COLOUR of their own rather than a trim material, which is the
    # half of the fitting system a material shot cannot show.
    bare = decorated("minecraft:iron_chestplate", "collar", "armorpieces:bandolier")
    control = client.shot("fitting-none", client.figure(suit(chest=bare)))
    dyed = decorated("minecraft:iron_chestplate", "collar", "armorpieces:bandolier",
                     fittings='"armorpieces:inlay":"red"')
    taken = client.shot("fitting-inlay-red", client.figure(suit(chest=dyed)))
    # Against the SAME piece with an empty socket: a fitting that stopped colouring anything would
    # otherwise be a frame of a perfectly good bandolier.
    client.drew("fitting-inlay-red", control, taken)

    bannered = decorated(
        "minecraft:iron_chestplate", "back", "armorpieces:cloak",
        fittings='"armorpieces:banner":{base:"yellow",patterns:[{pattern:"minecraft:cross",'
                 'color:"black"}]}')
    # From behind: a banner fitting hangs off a cloak, and a cloak is on the back.
    behind = client.shot("fitting-none-behind", client.figure(suit(chest=bare)), behind=True)
    taken = client.shot("fitting-banner", client.figure(suit(chest=bannered)), behind=True)
    client.drew("fitting-banner", behind, taken)


@scene("icons", "every template item's icon, as a grid of item frames on the studio's white wall")
def icons(client: Client) -> None:
    # The one thing in this mod that no studio shot of a figure can reach: an ITEM's model. An item
    # frame draws the icon in the world and an INVISIBLE one draws nothing but the icon, so a grid of
    # them is the creative tab in a single frame - and built inside the studio, it is that grid on
    # white, with no sky behind it.
    templates = [f"armorpieces:{anchor}_template" for anchor in PER_ANCHOR] + [
        "armorpieces:skin_template", "armorpieces:cloth_template", "armorpieces:fitting_template"]
    # An invisible marker subject: what is wanted from `studio` here is the DIMENSION and the client
    # standing in it, not a figure.
    box = client.bridge.call("studio", entity="minecraft:armor_stand", nbt="{Invisible:1b,Marker:1b}",
                             equipment={}, yaw=135, freeze=False)["look_at"]
    client.staged = True
    client.sweep(box)
    x0, y0, z = box["min"]["x"] + 1, box["min"]["y"], box["min"]["z"] + 1
    wide = 4
    tall = (len(templates) + wide - 1) // wide
    studio = f"execute in {STUDIO} run "
    # Whatever an earlier run left, first: the studio is a real place and it keeps what is put there.
    client.out_lines(f"{studio}kill @e[type=minecraft:item_frame]")
    client.out_lines(f"{studio}fill {x0} {y0} {z} {x0 + wide - 1} {y0 + tall + 4} {z} minecraft:air")
    client.out_lines(f"{studio}fill {x0} {y0} {z} {x0 + wide - 1} {y0 + tall - 1} {z} "
                     "minecraft:white_concrete")
    for index, template in enumerate(templates):
        x = x0 + index % wide
        y = y0 + tall - 1 - index // wide
        client.out_lines(
            f"{studio}summon minecraft:item_frame {x + 0.5} {y + 0.5} {z - 1} "
            '{Facing:2b,Invisible:1b,Fixed:1b,Item:{id:"' + template + '",count:1}}')
    try:
        time.sleep(1.0)
        wall = {"min": {"x": x0, "y": y0, "z": z},
                "max": {"x": x0 + wide - 1, "y": y0 + tall - 1, "z": z}}
        reply = client.bridge.call("render", look_at=wall, out="gate/tier3/icons.png",
                                   yaw=0, pitch=0, distance=tall * 0.72, width=640, height=640,
                                   downscale=2)
        result = client.goldens.compare("icons", Path(reply["path"]))
        if result.status in ("FAIL", "new"):
            client.problems.append(result.note)
    finally:
        # Whatever happened: a wall left standing here is in every OTHER scene's frame.
        client.out_lines(f"{studio}kill @e[type=minecraft:item_frame]")
        client.out_lines(
            f"{studio}fill {x0} {y0} {z} {x0 + wide - 1} {y0 + tall - 1} {z} minecraft:air")


# ---------------------------------------------------------------------------------------------
# What the mod says
# ---------------------------------------------------------------------------------------------


@scene("tooltip", "the lines the game draws for everything this mod puts on a stack")
def tooltip(client: Client) -> None:
    def says(item: str, needle: str, why: str) -> None:
        lines = client.tooltip(item)
        expect(any(needle in line for line in lines),
               f"{why}\n  expected a line holding {needle!r}, and the game drew:\n    "
               + "\n    ".join(lines))

    # A decorated piece names the piece it wears. This is the claim 0.4.0 shipped unseen: the
    # toolkit could not hover a slot, so nobody had ever read these lines.
    circlet = named("decoration.armorpieces.circlet")
    says(decorated("minecraft:iron_helmet", "brow", "armorpieces:circlet"), circlet,
         "a decorated helmet has to name the piece it is wearing")

    # And the template that hands it out says the same thing in its own name.
    says('armorpieces:brow_template[armorpieces:decoration="armorpieces:circlet"]', circlet,
         "a template's tooltip has to name the piece it applies")

    says(skinned("minecraft:iron_chestplate", "armorpieces:plate"),
         named("skin.armorpieces.plate"), "a skinned chestplate has to name its skin")
    says(clothed("minecraft:iron_chestplate", "armorpieces:tunic"),
         named("cloth.armorpieces.tunic"), "a clothed chestplate has to name its garment")

    # A fitting's own value, on the socket that holds it.
    says(decorated("minecraft:iron_chestplate", "collar", "armorpieces:bandolier",
                   fittings='"armorpieces:inlay":"red"'),
         named("decoration.armorpieces.bandolier"),
         "a piece with a fitting still has to name the piece")

    # And the tolerant half: a piece nothing defines must not take the tooltip - or the stack - down.
    lines = client.tooltip(decorated("minecraft:iron_helmet", "brow",
                                     "gate:a_pack_that_is_not_installed"))
    expect(any("Iron Helmet" in line for line in lines),
           "a helmet wearing a piece nothing defines did not draw a tooltip at all: " + str(lines))


@scene("smithing", "the four recipes, driven through the table's own slots, read off its output")
def smithing(client: Client) -> None:
    def build(base: str, template: str, addition: str = "") -> list[str]:
        """Put a base and a template (and maybe an addition) in the table; return the result's lines."""
        # Close first, and only then clear. Closing hands whatever is in the table back to the
        # player and it lands a tick or two later, so a clear in the same breath is undone by the
        # last build's pieces arriving in an inventory this one thought was empty.
        client.bridge.call("close_screen")
        time.sleep(0.5)
        client.bridge.command(f"clear {client.who()}")
        client.give(base, template, *([addition] if addition else []))
        client.table()
        held = {index: slot for index, slot in client.slots().items()
                if slot.get("item") and index >= 7}
        # The hotbar is filled in the order the items were given, which is the order they go in:
        # the base into the display slot its armor type owns, then the template, then the addition.
        order = sorted(held)
        client.click_slot(order[0])
        client.click_slot(_display_slot(base))
        client.click_slot(order[1])
        client.click_slot(4)
        if addition:
            client.click_slot(order[2])
            client.click_slot(5)
        time.sleep(0.4)
        result = client.slots().get(6) or {}
        if not result.get("item"):
            return []
        return [str(line) for line in
                client.bridge.call("get_tooltip", slot=6)["lines"]]

    # 1. A part. The template carries the piece; the addition is the trim material it is made of.
    lines = build("minecraft:iron_chestplate",
                  'armorpieces:pauldrons_template[armorpieces:decoration="armorpieces:lames"]',
                  "minecraft:amethyst_shard")
    expect(any(named("decoration.armorpieces.lames") in line for line in lines),
           "the part recipe produced " + (str(lines) or "nothing at all"))

    # 2. A skin.
    lines = build("minecraft:iron_chestplate",
                  'armorpieces:skin_template[armorpieces:skin="armorpieces:plate"]',
                  "minecraft:iron_ingot")
    expect(any(named("skin.armorpieces.plate") in line for line in lines),
           "the skin recipe produced " + (str(lines) or "nothing at all"))

    # 3. A cloth. Its addition is a banner, which is where the garment's colour comes from.
    lines = build("minecraft:iron_chestplate",
                  'armorpieces:cloth_template[armorpieces:cloth={cloth:"armorpieces:tunic"}]',
                  "minecraft:red_banner")
    expect(any(named("cloth.armorpieces.tunic") in line for line in lines),
           "the cloth recipe produced " + (str(lines) or "nothing at all"))

    # 4. A fitting, which is the one that needs a piece already on the armor to fit itself into.
    fitted = decorated("minecraft:iron_chestplate", "collar", "armorpieces:bandolier")
    lines = build(fitted, 'armorpieces:fitting_template[armorpieces:fitting="armorpieces:inlay"]',
                  "minecraft:red_dye")
    # And it says which fitting, and what the dye made of it: the output of this recipe is a socket
    # inside a socket, and "it produced something" would pass on a plain chestplate.
    expect(any(named("fitting.armorpieces.inlay") in line for line in lines),
           "the fitting recipe produced " + (str(lines) or "nothing at all"))

    # And a recipe a pack switched off produces nothing. A recipe is a plain datapack file, so
    # unlike a part it can be pushed into the running game.
    client.push("data/armorpieces/recipe/apply_skin.json", {"type": "armorpieces:disabled"})
    try:
        lines = build("minecraft:iron_chestplate",
                      'armorpieces:skin_template[armorpieces:skin="armorpieces:plate"]',
                      "minecraft:iron_ingot")
        expect(not lines,
               "apply_skin was overridden with armorpieces:disabled and the table still made "
               "something: " + str(lines))
    finally:
        client.bridge.clear("data/armorpieces/recipe/apply_skin.json", reload=True)
        client.pushed.remove("data/armorpieces/recipe/apply_skin.json")


def _display_slot(base: str) -> int:
    """Which of the table's four display slots an armor item belongs in, by its item id."""
    for index, needle in enumerate(("helmet", "chestplate", "leggings", "boots")):
        if needle in base:
            return index
    raise Failed(f"{base} is not a piece of armor, so no display slot owns it")
