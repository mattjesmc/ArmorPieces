// Live proof of the kit split (mcp-toolkit 0.123.0 loop kit): the nine part tools from this proxy
// under `kit`, Blockbench from the toolkit shim under this workspace's `project` profile, the loop
// check appended to every editing reply, and the two things that check has to carry that the
// proxy used to compute in memory - the sheet layout of the cubes that moved, and the face that was
// complete and GREW.
//
// Since the toolkit's own Blockbench plugin (0.133.0) it also proves the thing that split could not
// give: ONE SESSION holding ONE piece. The two servers present the same MCPTK_SESSION, opening a
// piece binds it, and an edit from a DIFFERENT session is refused with who holds it - which is the
// failure the Animals pack was built under (a bee's bone in the fox; set-packs.md, "the active-tab
// hazard").
//
// Read-only against the pack: it opens a shipped piece, edits it in memory, and closes the tab with
// `discard`. Nothing is saved.
//
//   node tools/mcp/_probe-loop.mjs [<namespace:piece>]        (from the repository root)
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const ROOT = process.cwd();
const PIECE = process.argv[2] || "armorpieces:brooch";
const CUBE = "loop_probe_cube";

function open(command, args, env) {
  const t = new StdioClientTransport({ command, args, env: { ...process.env, ...env }, cwd: ROOT, stderr: "inherit" });
  const c = new Client({ name: "loop-probe", version: "0" });
  return c.connect(t).then(() => c);
}

const text = (r) => (r.content ?? []).filter((p) => p.type === "text").map((p) => p.text).join("\n");
const images = (r) => (r.content ?? []).filter((p) => p.type === "image").length;
let failures = 0;
function expect(label, ok, detail = "") {
  console.log(`${ok ? "  ok  " : "  FAIL"} ${label}${detail ? ` — ${detail}` : ""}`);
  if (!ok) failures++;
}
const dump = (label, s) => { if (process.env.DUMP) console.log([`--- ${label} ---`, s, "--- end ---"].join("\n")); };

// What `.mcp.json` gives both servers: one identity, so the plugin sees one session holding the
// piece rather than two fighting over it.
const SESSION = `kit-probe-${process.pid}`;
// WHICH WINDOW the pair landed in, not a fixed port. Each Blockbench window's plugin takes the
// first free port at or above 25801 and a session claims one window (mcp-toolkit
// BLOCKBENCH_ISOLATION_DESIGN.md section 6.3), so an arbiter pinned to the base port would check a
// window the two servers under test are not in - and would pass or fail on somebody else's tabs.
// Found lazily, because it can only be answered once the pair has claimed: the window carrying
// SESSION, else the only one there.
const BB = (() => {
  const raw = (process.env.ARMORPIECES_BB_URL || "").trim().replace(/\/$/, "");
  const range = /^(?:https?:\/\/)?([^/:\s]+):(\d+)-(\d+)$/i.exec(raw);
  if (range) return { pinned: null, host: range[1], from: Number(range[2]), to: Number(range[3]) };
  if (raw) return { pinned: raw };
  return { pinned: null, host: "127.0.0.1", from: 25801, to: 25816 };
})();
let bridgeBase = BB.pinned;
async function BRIDGE() {
  if (bridgeBase) return bridgeBase;
  const found = [];
  for (let port = BB.from; port <= BB.to; port++) {
    const base = `http://${BB.host}:${port}`;
    try {
      const h = await fetch(`${base}/hello`, { signal: AbortSignal.timeout(1000) }).then((r) => r.json());
      if (h?.ok !== false && h?.app === "blockbench") found.push({ base, hello: h });
    } catch { /* nothing there */ }
  }
  if (!found.length) throw new Error(`no Blockbench window answered on ${BB.host}:${BB.from}-${BB.to}`);
  const mine = found.find((w) => w.hello.claimed_by?.session === SESSION);
  bridgeBase = (mine ?? found[0]).base;
  console.log(`  (arbiter talking to ${bridgeBase}${mine ? ", the window the pair claimed" : ", the only window there"})`);
  return bridgeBase;
}
const proxy = await open("node", ["tools/mcp/server.mjs"], {
  ARMORPIECES_BB_PROFILE: "kit", MCPTK_SESSION: SESSION, MCPTK_CLIENT: "kit-probe",
});
const shim = await open("node", ["run/mcptoolkit/mcp-server/index.mjs"], {
  MCPTK_URL: "http://127.0.0.1:25599",
  MCPTK_MEMORY_DIR: `${ROOT}/run/mcptoolkit/memory-data`,
  MCPTK_SHOT_MAX: "384",
  MCPTK_SESSION: SESSION, MCPTK_CLIENT: "kit-probe",
});

/** The plugin, spoken to directly - the arbiter needs to see what the two servers are to it. */
async function plugin(tool, args, session = { id: SESSION, client: "kit-probe", profile: "kit" }) {
  const res = await fetch(`${await BRIDGE()}/cmd`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool, args, session }),
  });
  return await res.json();
}

// --- the split -------------------------------------------------------------------------------
const proxyTools = (await proxy.listTools()).tools;
const shimTools = (await shim.listTools()).tools;
const proxyNames = proxyTools.map((t) => t.name);
const shimNames = shimTools.map((t) => t.name);
const tok = (s) => Math.round((s ?? "").length / 4);
const manifest = (ts) => ts.reduce((n, t) => n + tok(t.description) + tok(JSON.stringify(t.inputSchema ?? {})), 0);
console.log(`\nthe split: proxy ${proxyNames.length} tools ~${manifest(proxyTools)} tok, shim ${shimNames.length} tools ~${manifest(shimTools)} tok`);
expect("no tool is served twice", proxyNames.filter((n) => shimNames.includes(n)).length === 0);
expect("the nine part tools are the proxy's whole surface", proxyNames.length === 9, proxyNames.join(" "));
expect("place_cube comes from the shim", shimNames.includes("place_cube") && !proxyNames.includes("place_cube"));
expect("place_cube carries the workspace note",
  shimTools.find((t) => t.name === "place_cube")?.description.includes("bone group under `part`"));
expect("no game-bridge or memory tool is served", !shimNames.some((n) => n.startsWith("mem_") || ["render", "screenshot", "ping", "push_asset", "reload_resources"].includes(n)),
  shimNames.filter((n) => n.startsWith("mem_") || ["render", "screenshot", "ping"].includes(n)).join(" "));

// An agent's `tools:` line is its allowlist in a headless run, so a name that is no longer served
// is a call the session spends a turn discovering it cannot make.
const { readFileSync } = await import("node:fs");
for (const agent of ["part-author-kit", "kit-smoke"]) {
  const line = /^tools:\s*(.+)$/m.exec(readFileSync(`${ROOT}/.claude/agents/${agent}.md`, "utf8"))?.[1] ?? "";
  const asked = line.split(",").map((s) => s.trim()).filter((s) => s.startsWith("mcp__"));
  const missing = asked.filter((n) => {
    const bare = n.replace(/^mcp__(mcptoolkit|blockbench)__/, "");
    return n.startsWith("mcp__mcptoolkit__") ? !shimNames.includes(bare) : !proxyNames.includes(bare);
  });
  expect(`${agent} asks only for tools that are served`, missing.length === 0, missing.join(" "));
}

// --- the piece -------------------------------------------------------------------------------
console.log(`\nopening ${PIECE}`);
const opened = text(await proxy.callTool({ name: "armorpieces_open", arguments: { piece: PIECE } }));
dump("open", opened);
expect("armorpieces_open publishes the piece and its neighbours", /other parts on \w+: bone-local/.test(opened),
  `${opened.split("\n").length} lines`);
const full = text(await proxy.callTool({ name: "armorpieces_check", arguments: {} }));
const bone = (full.match(/^([a-z0-9_]+)\s+at \(/m) ?? [])[1];
expect("a bone to model in", !!bone, bone ?? "none found");

// --- an edit through the shim ------------------------------------------------------------------
console.log("\nedit through the shim");
const outline = text(await shim.callTool({ name: "list_outline", arguments: {} }));
expect("a read-only call gets no check", !/\[armorpieces\]/.test(outline));

const placed = text(await shim.callTool({
  name: "place_cube",
  arguments: { group: bone, elements: [{ name: CUBE, from: [-1, 3, -3], to: [1, 5, -2], origin: [0, 3, -3] }] },
}));
dump("place_cube", placed);
expect("the reply carries the check", /\[armorpieces\]/.test(placed));
expect("the check ran", !/could not run/.test(placed), /\[loop\][^\n]*/.exec(placed)?.[0] ?? "");
// The check labels a cube by its bone and index (`clasp[2]`), not by the name Blockbench holds.
const layoutRow = /^\s{4}(\S+) uv \d+,\d+ [\dx]+: (.+)$/m.exec(placed);
expect("the reply carries the new cube's face rectangles",
  !!layoutRow && layoutRow[2].split(/\s{2}/).length === 6,
  layoutRow ? `${layoutRow[1]}: ${layoutRow[2].split(/\s{2}/).length} faces` : "no `sheet layout` block");

// --- the grew diff -----------------------------------------------------------------------------
console.log("\npaint it, then grow it");
const painted = text(await proxy.callTool({ name: "armorpieces_paint", arguments: { sheet: "part", faces: { [`${CUBE}.*`]: 140 } } }));
dump("paint", painted);
expect("armorpieces_paint painted the whole cube", /Painted \d+ face/.test(painted), painted.split("\n")[0]);

const grown = text(await shim.callTool({ name: "modify_cube", arguments: { id: CUBE, to: [1, 7, -2] } }));
dump("modify_cube", grown);
expect("growing a fully painted cube is reported as a repaint",
  /repaint: faces that were complete and grew/.test(grown),
  /! repaint[^\n]*/.exec(grown)?.[0] ?? grown.split("\n").filter((l) => /^\s*[!-]/.test(l)).slice(0, 2).join(" | "));

// --- the picture budget -------------------------------------------------------------------------
console.log("\nthe picture");
const shot = await shim.callTool({ name: "capture_screenshot", arguments: {} });
const shotText = text(shot);
expect("capture_screenshot returns one picture", images(shot) === 1);
expect("the picture is cropped, resized and priced", /picture \d+x\d+ ~\d+ tok/.test(shotText),
  /picture[^\n]*/.exec(shotText)?.[0] ?? shotText.slice(0, 120));
// Not a hand-kept list any more: the plugin stamps capture_screenshot `observe` on its own
// manifest entry, and the loop hook selects on that stamp.
expect("a look gets no check (the plugin stamps it `observe`)", !/\[armorpieces\]/.test(shotText));

// --- one session, one piece ---------------------------------------------------------------------
console.log("\nthe binding");
const list = await plugin("project", { op: "list" });
const held = (list.result?.projects ?? []).find((p) => p.held_by || p.holder || p.session);
expect("opening a piece bound it to this session",
  JSON.stringify(list.result ?? {}).includes(SESSION),
  held ? JSON.stringify(held) : JSON.stringify(list.result ?? list).slice(0, 160));

const intruder = await plugin("place_cube",
  { group: bone, elements: [{ name: "intruder_cube", from: [-1, 3, -3], to: [0, 4, -2] }] },
  { id: `${SESSION}-other`, client: "kit-probe-intruder", profile: "kit" });
expect("another session's edit to it is REFUSED, with who holds it",
  intruder.ok === false && /held/i.test(`${intruder.error} ${intruder.hint ?? ""}`),
  `${intruder.ok ? "accepted" : intruder.error}`.slice(0, 160));

// --- cleanup ------------------------------------------------------------------------------------
console.log("\ncleanup");
const closed = text(await proxy.callTool({ name: "armorpieces_close", arguments: { discard: true } }));
expect("tab closed, nothing saved", /closed/.test(closed), closed.slice(0, 80).replace(/\n/g, " "));

// --- the check with nothing open ------------------------------------------------------------------
// run-unit.ps1 runs the loop's `run` checks once more AFTER the session, and a session that behaved
// closed its tab as its last act - so the checker has to be addressable by unit, not only by editor
// state. mcp-toolkit 0.124.0 exports MCPTK_UNIT for exactly that (LOOP_KIT_DESIGN.md section 11).
console.log("\nthe check with nothing open");
const { execFileSync } = await import("node:child_process");
const byUnit = (unit) => {
  try {
    return execFileSync("python", ["tools/check_active.py", "--json", "--brief"],
      { cwd: ROOT, encoding: "utf8", env: { ...process.env, MCPTK_UNIT: unit } })
      .trim().split("\n").pop() ?? "";
  } catch (e) {
    return String(e.stdout ?? e.message).trim().split("\n").pop() ?? "";
  }
};
const named = byUnit("brooch");
let namedReport = null;
try { namedReport = JSON.parse(named); } catch { /* not a report */ }
expect("MCPTK_UNIT gives the runner a report once the tab is closed",
  typeof namedReport?.text === "string", named.slice(0, 90));
// The unit has to WIN over whatever the editor holds. It did not, and the helm_wings run paid for
// it: a second session took the tab mid-run and the runner attributed that piece's problems to
// this one. Asserted against the unit's own name, so it holds whether or not a tab is open.
expect("the report is about the unit, not about whatever tab is open",
  namedReport?.piece === "brooch" || /\[armorpieces\] brooch /.test(namedReport?.text ?? ""),
  `piece=${namedReport?.piece} — ${(namedReport?.text ?? "").split("\n")[0].slice(0, 70)}`);
// Once: `current.json` lags the close by a moment, and calling twice can straddle it.
const unnamed = byUnit("");
// The invariant is that MCPTK_UNIT is what makes the report about the UNIT - not that the editor is
// empty. Asserting "it fails loudly" only held when no other piece was open, so this went red
// whenever a human had a tab up (2026-09-07: `bedroll`). Without the variable you get whatever the
// editor has, or a loud failure; either is correct, and neither may be this unit.
expect("without it the check follows the editor, not the unit",
  /no active piece and no MCPTK_UNIT/.test(unnamed) || !/"piece":\s*"brooch"/.test(unnamed),
  unnamed.slice(0, 90));

console.log(`\n${failures ? `${failures} FAILURE(S)` : "all green"}`);
await proxy.close();
await shim.close();
process.exit(failures ? 1 : 0);
