"""Every piece must have a surface the player can change.

A piece is drawn from three kinds of sheet, and they are not alternatives - they stack:

  MATERIAL  `<part>.png`            the greyscale master, recoloured through the TRIM
                                    material's ramp. This is the surface that answers the
                                    armor the piece is worn on.
  STATIC    `<part>_static.png`     real colour, laid OVER the recoloured master. A static
                                    texel does not answer the trim - it is what it is.
  FITTING   `<part>_<fitting>.png`  one greyscale mask per masked fitting, laid over both.
                                    The player fills it at the advanced smithing table.
                                    An EMPTY fitting costs nothing and the mask is not read,
                                    so a static layer under a mask is the piece's default look
                                    and the fitting is the override.

  (DecorationTextureManager.bake: recolour(master, statics, palette) then applyMask(...) per
  mask, in declaration order.)

So a piece can be 100% static and still be perfectly good - Animals and Coral are full of them,
because an animal's colour IS the piece - PROVIDED it carries a fitting for the player to fill.

What is NOT good, and what this check exists to catch, is a piece with NEITHER: static over the
whole silhouette AND no fitting. Nothing the player does changes it. It is inert. It renders
identically on netherite and on leather, with every trim, forever.

Measured 2026-09-10, this found five: ghast_tendrils, hoglin_hair and strider_hair in the Nether
pack, fox_ears in Animals and axolotl_frills in Coral.

    python tools/check_surfaces.py            # every pack and the mod
    python tools/check_surfaces.py nether     # one pack
"""
import json
import os
import sys
import glob

from PIL import Image

# Below this share of the master left answering the trim, a piece with no fitting is called
# inert. Not zero: a dozen stray texels of master showing through is not a surface.
THIN = 0.05

# Scratch packs are experiments, not content. `legacy` is generated from the other packs'
# former_ids by build_legacy_pack.py, so a finding there belongs to the pack it came from.
SKIP_PACKS = {"vlm-scratch", "legacy"}

ROOTS = [("mod", "src/main/resources/data/*/armorpieces/armor_decoration/*.json",
          "src/main/resources/assets")]
for _p in sorted(glob.glob("packs/*/datapack")):
    _name = _p.replace("\\", "/").split("/")[1]
    if _name in SKIP_PACKS:
        continue
    ROOTS.append((_name,
                  f"packs/{_name}/datapack/data/*/armorpieces/armor_decoration/*.json",
                  f"packs/{_name}/resourcepack/assets"))


def _maskless_fittings():
    """Fittings that are not a mask sheet at all.

    `armorpieces:banner` renders a real banner on its own `banner` bone off the `shield`
    sheet - there is no `<part>_banner.png` and there never was. Only the `material` and
    `dye` types are masks, so the type is read rather than the name hard-coded: a pack that
    ships its own banner-like fitting is covered too.
    """
    out = set()
    for f in glob.glob("src/main/resources/data/*/armorpieces/fitting/*.json") + \
            glob.glob("packs/*/datapack/data/*/armorpieces/fitting/*.json"):
        try:
            kind = json.load(open(f, encoding="utf-8")).get("type")
        except Exception:
            continue
        if kind not in ("armorpieces:material", "armorpieces:dye"):
            out.add(os.path.basename(f)[:-5])
    return out


MASKLESS = _maskless_fittings()


def opaque(path):
    """The set of texels a sheet actually paints, or None when there is no such sheet."""
    if not os.path.exists(path):
        return None
    im = Image.open(path).convert("RGBA")
    return {(x, y) for y in range(im.height) for x in range(im.width)
            if im.getpixel((x, y))[3] > 0}


def fittings_of(data):
    fs = data.get("fittings") or []
    if isinstance(fs, dict):
        return list(fs.keys())
    return [f if isinstance(f, str) else (f.get("type") or f.get("id") or "?") for f in fs]


def check(pack, datapat, assetbase, report, stats):
    bad, thin, total = [], [], 0
    dirs = glob.glob(f"{assetbase}/*/textures/entity/decoration")
    if not dirs:
        return bad, thin, total
    tex = dirs[0]
    for f in sorted(glob.glob(datapat)):
        data = json.load(open(f, encoding="utf-8"))
        if "anchors" not in data:
            continue
        name = os.path.basename(f)[:-5]
        master = opaque(os.path.join(tex, name + ".png"))
        if master is None:
            report.append(f"  {pack}/{name}: NO MASTER SHEET")
            bad.append(name)
            continue
        total += 1
        static = opaque(os.path.join(tex, name + "_static.png")) or set()
        fits = fittings_of(data)
        masks, unpainted = set(), []
        for fit in fits:
            key = fit.split(":")[-1]
            if key in MASKLESS:
                continue          # a banner is a bone and a shield sheet, never a mask
            mk = opaque(os.path.join(tex, f"{name}_{key}.png"))
            if mk is None or not mk:
                unpainted.append(key)
            else:
                masks |= mk
        # A MASK IS AN OVERRIDE, NOT A LAYER THE PIECE ALWAYS WEARS: it is not read until the
        # player fills the fitting, so a masked-but-unfilled texel still answers the trim. Only
        # static permanently takes a texel away from the material surface.
        left = master - static
        share = len(left) / max(len(master), 1)
        # What is left once the player HAS filled every fitting - the floor, not the norm.
        floor = len(master - static - masks) / max(len(master), 1)

        stats.append((name, len(master), len(static), share, floor, bool(fits)))

        for key in unpainted:
            report.append(
                f"  {pack}/{name}: fitting '{key}' is declared but its mask sheet is "
                f"empty or missing - the fitting changes nothing")
            bad.append(name)

        if not fits and share <= THIN:
            report.append(
                f"  {pack}/{name}: INERT - static covers {100*(1-share):.0f}% of the master "
                f"and there is no fitting. Nothing the player does changes this piece. "
                f"Give it a fitting, or leave some master showing.")
            bad.append(name)
        elif not fits and share < 0.20:
            thin.append(f"  {pack}/{name}: only {100*share:.0f}% of the master answers the "
                        f"trim and there is no fitting")

        # A sheet that exists and paints nothing. Harmless at render time - no texels, no effect -
        # but it means a session called set_part {static: true} and never painted the layer, which
        # is the same class of miss as an unpainted mask.
        if os.path.exists(os.path.join(tex, name + "_static.png")) and not static:
            thin.append(f"  {pack}/{name}: ships an EMPTY static sheet - created and never "
                        f"painted. Paint it or drop it.")
    return bad, thin, total


def main():
    want = sys.argv[1] if len(sys.argv) > 1 else None
    report, notes, bad, total, packstats = [], [], [], 0, []
    for pack, datapat, assetbase in ROOTS:
        if want and pack != want:
            continue
        stats = []
        b, t, n = check(pack, datapat, assetbase, report, stats)
        if stats:
            with_static = sum(1 for r in stats if r[2] > 0)
            packstats.append((pack, len(stats), with_static,
                              sum(1 for r in stats if r[5])))
        bad += b
        notes += t
        total += n

    print(f"=== surfaces: {total} pieces checked\n")
    print(f"  {'pack':<10} {'pieces':>7} {'with STATIC':>12} {'with FITTING':>13}")
    for pack, n, st, fi in packstats:
        note = ""
        if n > 3 and st == 0:
            note = "   <-- no static anywhere: nothing in this pack has a colour of its own"
        elif n > 3 and fi * 100 // n < 50:
            note = "   <-- fitting-starved"
        print(f"  {pack:<10} {n:>7} {st:>7} ({100*st//n:>3}%) {fi:>7} ({100*fi//n:>3}%){note}")
    if report:
        print("\nproblems:")
        for line in report:
            print(line)
    if notes:
        print("\nnotes:")
        for line in notes:
            print(line)
    if not report:
        print("  every piece has a surface the player can change")
    print(f"\n{len(bad)} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
