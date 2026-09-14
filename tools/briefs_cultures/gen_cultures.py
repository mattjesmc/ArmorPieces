"""Generate the 48 briefs of the four culture packs (2026-09-13): Samurai, Norse, Antiquity,
Tournament. Same shape as gen_finish.py (2026-09-12): every face snapped off every bone-mate
plane and shell wall, budgets derived from the snapped cubes, every piece rotation-free, one brief
per piece for part-author-qwen on qwen3.8-flash.

New here: the 48 are snapped against EACH OTHER too. A sibling on the same bone (any of the four
packs) will be on disk by the time the later session runs, so its planes are bone-mate planes.
Snapping is sequential in P order, so a later piece avoids the earlier one's snapped values.

    python gen_cultures.py            # write docs/plans/briefs/<piece>.md
    python gen_cultures.py --plan     # print the plan tables (markdown) instead
"""
import io, os, sys, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = "docs/plans/briefs"

PACKS = {
 "samurai": dict(ns="armorpieces_samurai", title="Armor Pieces: Samurai",
                 dir=r"C:\Users\Matthijs\ArmorPieces\packs\samurai",
                 look="black lacquer over iron, red odoshi lacing and gilt fittings - the armor of a "
                      "daimyo, every piece a named part of a real suit",
                 table="Samurai", loot="the pack's `daimyo` loot group"),
 "norse": dict(ns="armorpieces_norse", title="Armor Pieces: Norse",
               dir=r"C:\Users\Matthijs\ArmorPieces\packs\norse",
               look="riveted iron, wolf-grey fur, painted lime wood and a little gold - the north "
                    "as the sagas tell it, hair and beard included",
               table="Norse", loot="the pack's `jarl` loot group"),
 "antiquity": dict(ns="armorpieces_antiquity", title="Armor Pieces: Antiquity",
                   dir=r"C:\Users\Matthijs\ArmorPieces\packs\antiquity",
                   look="bronze and red leather - Greece and Rome, the hoplite and the legionary, "
                        "every piece a thing with a Latin or Greek name",
                   table="Antiquity", loot="the pack's `legion` loot group"),
 "tourney": dict(ns="armorpieces_tourney", title="Armor Pieces: Tournament",
                 dir=r"C:\Users\Matthijs\ArmorPieces\packs\tourney",
                 look="bright steel and heraldry - azure and gold, the joust and the lists, a lady's "
                      "favour on the arm; the hardware answers the trim and the colours are its own",
                 table="Tournament", loot="the pack's `tilt` loot group"),
}

# bone -> (pivot label, conversion text, rig block). Shells are the real inflates.
BONES = {
 "head": ("the head bone's pivot at Blockbench `(0, 24, 0)`",
          "check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z",
          "    head box                x -4 .. 4       y 24 .. 32      z -4 .. 4\n"
          "    helmet shell (+1)       x -5 .. 5       y 23 .. 33      z -5 .. 5"),
 "body": ("the body bone's pivot at Blockbench `(0, 24, 0)`",
          "check_x = -bb_x        check_y = 24 - bb_y        check_z = bb_z",
          "    body box                x -4 .. 4       y 12 .. 24      z -2 .. 2\n"
          "    chestplate shell (+1)   x -5 .. 5       y 11 .. 25      z -3 .. 3\n"
          "    leggings shell (+0.5)   x -4.5 .. 4.5   y 11.5 .. 24.5  z -2.5 .. 2.5"),
 "left_arm": ("the arm bone's pivot at Blockbench `(-5, 22, 0)` - **not** the top of the arm box",
          "check_x = -5 - bb_x        check_y = 22 - bb_y        check_z = bb_z",
          "    left arm box            x -8 .. -4      y 12 .. 24      z -2 .. 2\n"
          "    sleeve shell (+1)       x -9 .. -3      y 11 .. 25      z -3 .. 3"),
 "left_leg": ("the leg bone's pivot at Blockbench `(-1.9, 12, 0)` - **not** the top of the leg box",
          "check_x = -1.9 - bb_x        check_y = 12 - bb_y        check_z = bb_z",
          "    left leg box            x -3.9 .. 0.1   y 0 .. 12       z -2 .. 2\n"
          "    leggings shell (+0.4)   x -4.3 .. 0.5   y -0.4 .. 12.4  z -2.4 .. 2.4\n"
          "    boots shell (+0.9)      x -4.8 .. 1.0   y -0.9 .. 12.9  z -2.9 .. 2.9"),
}
SOCK_BONE = {"crest": "head", "brow": "head", "horns": "head", "pauldrons": "left_arm",
             "back": "body", "collar": "body", "vambraces": "left_arm", "belt": "body",
             "tassets": "left_leg", "knees": "left_leg", "greaves": "left_leg", "spurs": "left_leg"}
SOCK_ANCHOR = {"crest": "(0, 32, 0)", "brow": "(0, 28, -4)", "horns": "(-4, 29, 0)",
               "pauldrons": "(-6, 22, 0)", "back": "(0, 22, 2)", "collar": "(0, 23, -2)",
               "vambraces": "(-6, 16, 0)", "belt": "(0, 14, 0)", "tassets": "(-1.9, 10, 0)",
               "knees": "(-1.9, 6, -2)", "greaves": "(-1.9, 4, -2)", "spurs": "(-1.9, 2, 2)"}
MIRRORED = {"horns", "pauldrons", "vambraces", "tassets", "knees", "greaves", "spurs"}

from pieces_samurai import P as P1
from pieces_norse import P as P2
from pieces_antiquity import P as P3
from pieces_tourney import P as P4
P = P1 + P2 + P3 + P4
for p in P:
    p.setdefault("bone", SOCK_BONE[p["socket"]])
    p.setdefault("anchor", SOCK_ANCHOR[p["socket"]])
    p.setdefault("mirrored", p["socket"] in MIRRORED)

# ---------------------------------------------------------------------------------------------
# Snap every face off the planes of the bone-mates (on disk AND the siblings designed here) and
# the outer shell (LESSONS #22/#24), then derive the two budgets from the snapped cubes.
sys.path.insert(0, "tools")
import check_part as _cp, trace_geometry as _tr
from bb_rig import parse_anchors as _pa
_anchors = _pa()
TOL = 0.012
OUTER = {"head": ((-5, 5), (23, 33), (-5, 5)), "body": ((-5, 5), (11, 25), (-3, 3)),
         "left_arm": ((-9, -3), (11, 25), (-3, 3)), "left_leg": ((-4.8, 1.0), (-0.9, 12.9), (-2.9, 2.9))}
CONV = {"head": (0.0, 24.0), "body": (0.0, 24.0), "left_arm": (-5.0, 22.0), "left_leg": (-1.9, 12.0)}
_pc = {}


def disk_planes(sock, bone):
    if sock not in _pc:
        planes = [set(), set(), set()]
        for stem, cube, lo, hi in _tr.neighbours("__none__", sock, bone, _anchors):
            blo, bhi = _cp.to_blockbench(bone, lo, hi)
            for ax in range(3):
                planes[ax].add(round(blo[ax], 3)); planes[ax].add(round(bhi[ax], 3))
        for ax in range(3):
            planes[ax].update(OUTER[bone][ax])
        _pc[sock] = planes
    return _pc[sock]


def free(val, planes):
    return all(abs(val - pv) >= TOL for pv in planes) and abs(val - round(val)) > 1e-9


def snap(val, planes):
    if free(val, planes):
        return val
    for step in range(1, 40):
        for d in (step, -step):
            v = round(val + d * 0.01, 2)
            if free(v, planes):
                return v
    raise SystemExit(f"no free value near {val}")


def nums(co):
    return [float(t) for t in re.findall(r"-?\d+\.?\d*", co)]


# sibling planes accumulate per bone as pieces are snapped, keyed by socket so a piece never
# snaps against its own socket (same-socket pieces are never worn together)
_sib = {}
SNAPPED = []
for p in P:
    bone, sock = p["bone"], p["socket"]
    planes = [set(s) for s in disk_planes(sock, bone)]
    for (sb, ss), pl in _sib.items():
        if sb == bone and ss != sock:
            for ax in range(3):
                planes[ax] |= pl[ax]
    new, xs, ys, zs = [], [], [], []
    mine = _sib.setdefault((bone, sock), [set(), set(), set()])
    for nm, what, co in p["cubes"]:
        v = nums(co)
        assert len(v) == 6, (p["id"], nm, co)
        w = list(v) if nm == "cloth" else [snap(v[i], planes[i // 2]) for i in range(6)]
        for i in range(6):
            if w[i] != v[i]:
                SNAPPED.append((p["id"], nm, "xyz"[i // 2], v[i], w[i]))
            mine[i // 2].add(w[i])
        assert w[0] < w[1] and w[2] < w[3] and w[4] < w[5], (p["id"], nm, w)
        xs += w[0:2]; ys += w[2:4]; zs += w[4:6]
        new.append((nm, what, f"x {w[0]:.2f} .. {w[1]:.2f}    y {w[2]:.2f} .. {w[3]:.2f}    z {w[4]:.2f} .. {w[5]:.2f}"))
    p["cubes"] = new
    lo = [math.floor(min(a) * 10 - 0.5) / 10 for a in (xs, ys, zs)]
    hi = [math.ceil(max(a) * 10 + 0.5) / 10 for a in (xs, ys, zs)]
    p["budget_bb"] = f"x {lo[0]:.1f} .. {hi[0]:.1f}, y {lo[1]:.1f} .. {hi[1]:.1f}, z {lo[2]:.1f} .. {hi[2]:.1f}"
    ox, py = CONV[bone]
    cx = sorted([ox - lo[0], ox - hi[0]]); cy = sorted([py - lo[1], py - hi[1]])
    p["budget_check"] = f"x  {cx[0]:.1f} .. {cx[1]:.1f}      y  {cy[0]:.1f} .. {cy[1]:.1f}      z  {lo[2]:.1f} .. {hi[2]:.1f}"
    p["_lo"], p["_hi"] = lo, hi

TMPL = io.open(os.path.join(HERE, "template.txt"), encoding="utf-8").read()
TMPL_BANNER = io.open(os.path.join(HERE, "template_banner.txt"), encoding="utf-8").read()


def neigh_rows(p):
    """The brief's neighbour table: the hand-written rows, with any row naming a sibling built in
    this batch given the sibling's SNAPPED envelope (the hand-typed one is a guess), plus a generic
    row for every same-bone sibling of this pack the hand rows did not mention."""
    rows = []
    sibs = {q["id"]: q for q in P if q is not p and q["bone"] == p["bone"]}
    named = set()
    for a, b, c in p["neigh"]:
        sid = a.split(" ")[0]
        if sid in sibs:
            lo, hi = sibs[sid]["_lo"], sibs[sid]["_hi"]
            b = f"x {lo[0]:.2f}..{hi[0]:.2f}, y {lo[1]:.2f}..{hi[1]:.2f}, z {lo[2]:.2f}..{hi[2]:.2f}"
            named.add(sid)
        rows.append((a, b, c))
    for sid, q in sibs.items():
        if sid in named or q["pack"] != p["pack"] or q["socket"] == p["socket"]:
            continue
        lo, hi = q["_lo"], q["_hi"]
        rows.append((f"{sid} ({q['socket']})",
                     f"x {lo[0]:.2f}..{hi[0]:.2f}, y {lo[1]:.2f}..{hi[1]:.2f}, z {lo[2]:.2f}..{hi[2]:.2f}",
                     "your own pack's piece on this bone, worn WITH you and built in the same batch - "
                     "the coordinates above already stay off its faces; an OVERLAP note against it is "
                     "a `-`, never a `!`"))
    return rows


def render(p):
    pk = PACKS[p["pack"]]
    pivot, conv, rig = BONES[p["bone"]]
    fits = p["fittings"]
    fit0 = fits[0]
    cubelist = "\n\n".join(f"- **{nm}** — {what}:\n\n        {co}" for nm, what, co in p["cubes"])
    neightable = "\n".join(f"| `{a}` | {b} | {c} |" for a, b, c in neigh_rows(p))
    statictable = "\n".join(
        f"- {', '.join('`'+c+'`' for c in cubes)}: base `{base}`, `up` `{lit}` — {note}"
        for cubes, base, lit, note in p["static"]) or "- (no static cubes)"
    maxabs = max(abs(float(v)) for nm, w, co in p["cubes"] for v in [co.split()[1], co.split()[3]])
    if not p["mirrored"]:
        pair = ""
    elif p["bone"] == "head":
        pair = ("\n\n**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` "
                f"is `{maxabs}`, so the pair spans **{round(2*maxabs, 2)}** — the check compares "
                "that against the **18** the shoulders span, and you are inside it. Report the span.")
    else:
        where = ("arms are already outboard of the shoulders" if p["bone"] == "left_arm"
                 else "legs sit inboard of the shoulders")
        pair = ("\n\n**This is a mirrored socket, so the pair spans `2 x |x|`.** Your outermost `x` "
                f"is `{maxabs}`, so the pair spans **{round(2*maxabs, 2)}**. **The 18-unit ceiling is "
                f"a `horns` rule and does not apply on this bone** — the {where}, and the mod's "
                "own `cuffs` spans 20.14 here. Report the span; do not try to come under 18.")
    has_static = bool(p["static"])
    staticwhy = ((f"`static_created: true` is correct. " + p["static"][0][3].split(" - ")[0].capitalize()
                  + " is a colour that must not change with the armor.") if has_static else
                 "`static_created: true` is correct even though this piece paints no static cube: "
                 "the sheet stays empty and costs nothing. Skip the static paint call and say so.")
    common = dict(
        name=p["name"], ns=pk["ns"], title=pk["title"], look=pk["look"], table=pk["table"],
        loot=pk["loot"], socket=p["socket"], line=p["line"], id=p["id"], packdir=pk["dir"],
        centre=p["centre"], fit0=fit0, fitpad=" " * max(0, 8 - len(fit0)), staticwhy=staticwhy,
        material=p["material"], rig=rig, anchor=p["anchor"],
        mirror=("**This is a mirrored socket: model the negative-x side ONLY** and the game mirrors "
                "it to the other side. On this side, `west` is the outboard face and `north` is the "
                "front." if p["mirrored"] else "This socket is not mirrored: build the whole piece once."),
        intent=p["intent"], cubelist=cubelist, n=len(p["cubes"]), np1=len(p["cubes"]) + 1,
        budget_bb=p["budget_bb"], pivot=pivot, conv=conv, budget_check=p["budget_check"],
        pairspan=pair, neightable=neightable, paint=p["paint"], statictable=statictable,
        fitwhere=", ".join(f"`{c}`" for c in p["fit_cubes"]),
        pairdone=("\n- [ ] Pair span reported." if p["mirrored"] else ""))
    if p.get("banner"):
        return TMPL_BANNER.format(**common)
    return TMPL.format(
        fitlist=", ".join(f'"armorpieces:{f}"' for f in fits),
        fitdesc=f"one, **`armorpieces:{fit0}`**, masked. The reply will say a `part_{fit0}` sheet "
                f"was created; that is what you paint the mask onto later, and it is why this call "
                f"comes before painting.",
        **common)


if __name__ == "__main__":
    if "--plan" in sys.argv:
        for pack in PACKS:
            print(f"\n### {PACKS[pack]['title']}\n\n| socket | piece | what it is | fitting | centre |\n|---|---|---|---|---|")
            for p in P:
                if p["pack"] == pack:
                    print(f"| `{p['socket']}` | `{p['id']}` | {p['short']} | `{'` + `'.join(p['fittings'])}` | `{p['centre'].split(':')[1]}` |")
        sys.exit(0)
    for p in P:
        text = render(p)
        path = os.path.join(OUT, p["id"] + ".md")
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        print(f"  {p['pack']:<9} {p['id']:<18} {p['socket']:<10} {p['bone']:<9} {len(p['cubes'])} cubes  "
              f"{'+'.join(p['fittings']):<13} {'mirrored' if p['mirrored'] else '':<9} {text.count(chr(10))+1:>4} lines")
    for s in SNAPPED:
        print("  snapped %-20s %-12s %s %7.2f -> %7.2f" % s)
    print(f"\n{len(P)} briefs written, {len(SNAPPED)} faces snapped")
