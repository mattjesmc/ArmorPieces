"""Goldens: a frame this repository has already LOOKED AT, and the diff when it stops matching.

Tier 3 is the only tier whose subject is a picture, and a picture cannot be asserted the way a
number can. What can be asserted is that it has not CHANGED - so every frame the suite takes is
compared against a copy under `tools/gate/goldens/`, and a frame with no golden beside it is not a
pass and not a failure: it is a frame nobody has looked at yet. `--bless` is the moment a person
looks, and it is the only way one gets written.

Two facts decide how strict the comparison is, and both were measured on 2026-09-10:

  * **The same scene renders bit-identically.** `studio {freeze:true}` stops the tick, the studio has
    no sky and flat full-bright light, and `render` is out of band at a fixed resolution - two shots
    of one subject came back with a maximum channel difference of ZERO. So the tolerance below is
    not for noise in the renderer; it is for a driver or a game update moving a texel, and it is
    deliberately small enough that a decoration that stopped drawing cannot hide under it.
  * **A small piece is a small part of the frame.** A circlet is a few hundred texels of a 320x320
    figure. A percentage-of-the-image threshold generous enough to absorb antialiasing would absorb
    the whole circlet with it, which is why the allowance is a COUNT of pixels and a low one.

A failure writes three panels side by side - the golden, what came back, and the mask of where they
differ - because the number that failed says nothing about whether the render layer died or a
texture moved by a pixel.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent.parent
GOLDENS = ROOT / "tools" / "gate" / "goldens"

#: A channel may move by this much without counting as a differing pixel. One step of a texture's
#: own dithering; nothing a person could see.
TOLERANCE = 4

#: How many pixels may differ before the frame has changed. A whole piece is hundreds.
ALLOWANCE = 24


@dataclass
class Comparison:
    name: str
    status: str  # pass | FAIL | new | blessed
    note: str = ""
    pixels: int = 0


@dataclass
class Goldens:
    """The store, and what a run did to it."""

    out: Path
    bless: bool = False
    results: list[Comparison] = field(default_factory=list)

    def golden(self, name: str) -> Path:
        return GOLDENS / f"{name}.png"

    def compare(self, name: str, taken: Path) -> Comparison:
        """One frame against its golden. Records and returns the verdict."""
        result = self._compare(name, taken)
        self.results.append(result)
        return result

    def _compare(self, name: str, taken: Path) -> Comparison:
        golden = self.golden(name)
        if not golden.is_file():
            if self.bless:
                golden.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(taken, golden)
                return Comparison(name, "blessed", f"written from {taken}")
            return Comparison(name, "new", (
                f"no golden for {name}. This frame has never been looked at: open {taken}, and if "
                f"it is right, run this scene again with --bless to keep it as the answer."))

        with Image.open(golden) as before, Image.open(taken) as now:
            first = before.convert("RGB")
            second = now.convert("RGB")
            if first.size != second.size:
                return Comparison(name, "FAIL", (
                    f"the frame is {second.size[0]}x{second.size[1]} and its golden is "
                    f"{first.size[0]}x{first.size[1]} - a render argument changed, not the mod"))
            differing, mask = _difference(first, second)

        if differing <= ALLOWANCE:
            return Comparison(name, "pass", "", differing)
        if self.bless:
            # The other half of blessing, and the one that is used far more often: a part was
            # re-authored, a texture was redrawn, and the golden is now the OLD picture. Overwriting
            # is announced by name at the end of the run, which is what keeps it honest.
            shutil.copyfile(taken, golden)
            return Comparison(name, "blessed", f"replaced, {differing} pixels changed", differing)
        panels = self._panels(name, golden, taken, mask)
        return Comparison(name, "FAIL", (
            f"{differing} pixels differ from the golden (more than {ALLOWANCE} may). "
            f"What changed is drawn in {panels}: golden, this run, and the mask between them. "
            f"If this run is the better picture, --bless replaces the golden."), differing)

    def _panels(self, name: str, golden: Path, taken: Path, mask: Image.Image) -> Path:
        """Golden, now and the mask in one image, because a count is not a diagnosis."""
        with Image.open(golden) as before, Image.open(taken) as now:
            width, height = before.size
            sheet = Image.new("RGB", (width * 3 + 8, height), (24, 24, 28))
            sheet.paste(before.convert("RGB"), (0, 0))
            sheet.paste(now.convert("RGB"), (width + 4, 0))
            sheet.paste(mask, (width * 2 + 8, 0))
        path = self.out / f"{name}.diff.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(path)
        return path


def _difference(first: Image.Image, second: Image.Image) -> tuple[int, Image.Image]:
    """How many pixels moved by more than the tolerance, and a red mask of where.

    Channel by channel and then the LARGEST of the three, rather than the difference of two greys:
    a gold fitting turning grey barely moves a luminance, and it is the whole subject of the frame.
    """
    channels = ImageChops.difference(first, second).split()
    worst = channels[0]
    for channel in channels[1:]:
        worst = ImageChops.lighter(worst, channel)
    over = worst.point(lambda value: 255 if value > TOLERANCE else 0, mode="1")
    differing = sum(over.histogram()[1:])
    mask = Image.new("RGB", first.size, (255, 255, 255))
    mask.paste(Image.new("RGB", first.size, (220, 40, 40)), (0, 0), over)
    return differing, mask
