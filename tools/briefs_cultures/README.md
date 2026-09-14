# The culture packs' brief generator (2026-09-13)

`docs/plans/cultures.md` is the plan; this is how its 48 briefs were made, kept so the pattern is
not re-remembered next time (the 2026-09-10 and 2026-09-12 generators lived in session scratchpads
and are gone).

    python tools/briefs_cultures/verify_cultures.py      # falsify the piece tables (run from the repo root)
    python tools/briefs_cultures/gen_cultures.py         # write docs/plans/briefs/<piece>.md
    python tools/briefs_cultures/gen_cultures.py --plan  # the plan tables, markdown
    python tools/briefs_cultures/gen_sets.py             # the four packs' armorpieces-sets.json + Java

`pieces_<pack>.py` hold the designs: cube coordinates in Blockbench world, neighbours, which cube is
material / static / masked, the paint. `gen_cultures.py` snaps every face off every bone-mate plane
(on disk AND the siblings of the same batch), derives the budgets, and renders `template.txt`
(`template_banner.txt` for a banner piece). Re-running it after the batch overwrites the briefs'
Lessons sections - do not.
