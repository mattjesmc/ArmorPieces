"""Crop a screenshot to what is in it, then shrink it: a look costs its AREA, so empty space is
paid for on every turn that follows.

A picture costs roughly (width x height) / 750 tokens, and unlike a tool's text it is re-sent for the
rest of the session. Blockbench's viewport is ~1020x946 - about 1300 tokens - but the figure in it is
around 400x690, so nearly three quarters of that is background. Cropping first and resizing after
spends the whole budget on the armor:

    1020x946 whole viewport            ~1290 tokens,  28% of them the figure
    512x475  resized only              ~ 324 tokens,  28% of them the figure
    221x384  cropped, then resized     ~ 113 tokens, 100% of them the figure

The figure is 32 units tall, so 384 px down its long edge is ~12 screen pixels per armor texel -
several times what a value decision needs. Below about 160 the bands start to blur into each other.

Usage:
    python tools/shrink_shot.py <file.png> [longest edge, default 384]
    python tools/shrink_shot.py --report <file.png> [...]     # what each one costs, no rewriting
"""

import sys
from pathlib import Path

from PIL import Image

MARGIN = 4          # texels of breathing room, so nothing sits on the frame
TOKENS_PER_PX = 750


def content_box(image: Image.Image) -> tuple[int, int, int, int]:
    """The figure's own rectangle: the alpha channel if there is one, else what differs from the
    corner colour. Blockbench renders on a transparent ground, but a theme or a screenshot of a
    filled viewport should not defeat this."""
    box = image.getbbox()
    if box and (box[2] - box[0]) * (box[3] - box[1]) < image.width * image.height * 0.9:
        return box
    ground = image.convert("RGB").getpixel((0, 0))
    flat = image.convert("RGB")
    diff = flat.point(lambda v: v)  # copy, then compare channel-wise below
    mask = Image.new("L", image.size, 0)
    px, mk = flat.load(), mask.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = px[x, y]
            if abs(r - ground[0]) + abs(g - ground[1]) + abs(b - ground[2]) > 24:
                mk[x, y] = 255
    del diff
    return mask.getbbox() or (0, 0, image.width, image.height)


def tokens(size: tuple[int, int]) -> int:
    return round(size[0] * size[1] / TOKENS_PER_PX)


def shrink(path: Path, longest: int = 384, write: bool = True) -> dict:
    with Image.open(path) as opened:
        image = opened.convert("RGBA")
    before = image.size
    box = content_box(image)
    box = (max(0, box[0] - MARGIN), max(0, box[1] - MARGIN),
           min(image.width, box[2] + MARGIN), min(image.height, box[3] + MARGIN))
    cropped = image.crop(box)
    filled = (cropped.width * cropped.height) / (before[0] * before[1])

    out = cropped
    if max(out.size) > longest:
        scale = longest / max(out.size)
        out = out.resize((max(1, round(out.width * scale)), max(1, round(out.height * scale))),
                         Image.LANCZOS)
    if write:
        out.save(path)
    return {"before": before, "cropped": cropped.size, "after": out.size,
            "filled": filled, "was": tokens(before), "now": tokens(out.size)}


def main() -> None:
    args = sys.argv[1:]
    report = "--report" in args
    args = [a for a in args if a != "--report"]
    if not args:
        sys.exit(__doc__)
    longest = 384
    files = []
    for arg in args:
        if arg.isdigit():
            longest = int(arg)
        else:
            files.append(Path(arg))
    for path in files:
        got = shrink(path, longest, write=not report)
        if report:
            print(f"{path.name:<28}{got['before'][0]}x{got['before'][1]} -> "
                  f"{got['after'][0]}x{got['after'][1]}   {got['was']:>5} -> {got['now']:>4} tokens   "
                  f"figure was {got['filled'] * 100:.0f}% of the frame")
        else:
            print(f"{got['after'][0]}x{got['after'][1]}")


if __name__ == "__main__":
    main()
