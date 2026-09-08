#!/usr/bin/env node
// The Armor Pieces bridge: an MCP server that stands in front of Blockbench's plugin bridge.
//
// The bridge is `mcptoolkit_bridge.js` (mcp-toolkit 0.133.0+, plain HTTP on 127.0.0.1:25801), which
// replaced the third-party Blockbench MCP plugin this server was first written against. Neither can
// be extended by another plugin, so everything Armor Pieces wants an agent to have is added here,
// one hop out, by a stdio server:
//
//   - the armorpieces_* tools: open, new, check, save, part, set_part, pieces, close. Each is a
//     risky_eval into the plugin's `armorpieces_api` with the bridge's traps handled here. Under
//     the default `kit` profile these nine are the WHOLE of what this server serves.
//   - a CHECK after every editing call: the Armor Pieces plugin publishes the open piece after
//     each edit (tools/blockbench_plugin, "status for the bridge"), and this runs
//     tools/check_part.py over it and appends the compact report to the reply - so a face that
//     landed on the helmet shell is reported by the call that put it there.
//   - a PROFILE over Blockbench's own manifest (profile.mjs), for the pre-kit profiles. Names are
//     unchanged, so `mcp__blockbench__place_cube` is still that.
//
// TRANSPORT (2026-09-07). The bridge speaks the game bridge's shape - GET /hello, GET /tools with
// `mechanism` on every entry, POST /cmd {tool, args, session} -> {ok, result, mechanism} - so there
// is no MCP handshake, no session id in a response header and no SSE to parse. Two things that
// shape the code here: a picture comes back as `_image` on the result rather than as MCP image
// content, and `mechanism` on the manifest replaces the hand-kept read-only list.
//
// ONE SESSION PER PIECE, AND THAT IS HARDER THAN IT LOOKS. The plugin binds a project to the session
// that made or opened it and refuses an EDIT to a project another live session holds. This server
// and the mcp-toolkit shim are two processes inside one Claude session editing one piece, so they
// must present ONE identity, or the shim's place_cube and this server's armorpieces_save would
// refuse each other. They agree without being told: both fall back to the PARENT process id, which
// is the `claude.exe` they are both direct children of.
//
// The trap is the other direction, and `.mcp.json` has now been wrong twice in it. It derived the
// id from CLAUDE_CODE_SESSION_ID, which a headless `claude -p` child INHERITS - so every child a
// session launched presented the SAME id, was one session to the plugin, and shared ONE binding
// (measured 2026-09-07: a dozen of kelp_mantle's calls answered about coral_crown). The fix was
// ${ARMORPIECES_SESSION:-armorpieces}, which nothing ever set, so every session fell back to the
// same literal and the bug survived its own fix. `.mcp.json` now sets no id at all. An explicit
// MCPTK_SESSION still wins, for deliberate sharing - and, independently, `evalIn` names its
// project on every call so a shared binding cannot misdirect these tools again.
//
// Configuration, all optional:
//   ARMORPIECES_BB_URL      the bridge's base URL      (http://127.0.0.1:25801)
//   ARMORPIECES_BB_PROFILE  kit | kit_skin | full             (kit)
//                           `kit` serves ONLY the nine part tools: Blockbench comes from the
//                           mcp-toolkit shim's project profile instead (.mcptoolkit/loop.json).
//   ARMORPIECES_PYTHON      the interpreter for tools/ (python)
//   MCPTK_SESSION           the identity both this server and the shim bind projects under
//                           (unset: `mcptk-<parent pid>`, which the pair derives identically)
//
// Blockbench need not be running when this starts: the tool list then comes from the last live
// manifest (cached in the temp dir) or the snapshot beside this file, and the first call reaches
// for the app again.

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { execFile } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { KIT_INSTRUCTIONS, KIT_SKIN_INSTRUCTIONS, NOTES, OWN_PROFILES, PROFILES, READ_ONLY } from "./profile.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..", "..");
// Where the bridge is; `/cmd` and `/tools` hang off it. A stale `.../bb-mcp` from the old plugin
// would otherwise fail as a 404 with nothing saying why, so it is trimmed and reported.
//
// NOT ONE PORT ANY MORE (mcp-toolkit 0.139.0 / plugin 0.5.0). Each Blockbench WINDOW's plugin takes
// the first free port at or above 25801, so the port names the window, and a session works in a
// window of its own. A bare URL still PINS one window, which is what writing one down means; the
// default, and `host:from-to`, is a range to discover over.
const RAW_URL = (process.env.ARMORPIECES_BB_URL || "").trim()
  .replace(/\/(bb-mcp|cmd|tools|hello)\/?$/, "").replace(/\/$/, "");
const RANGE = /^(?:https?:\/\/)?([^/:\s]+):(\d+)-(\d+)$/i.exec(RAW_URL);
const PINNED = RAW_URL && !RANGE ? RAW_URL : null;
const SCAN = RANGE
  ? { host: RANGE[1], from: Number(RANGE[2]), to: Math.max(Number(RANGE[2]), Number(RANGE[3])) }
  : { host: "127.0.0.1", from: 25801, to: 25816 };
const PYTHON = process.env.ARMORPIECES_PYTHON || "python";
// `.mcp.json` sets this as `${ARMORPIECES_BB_PROFILE:-kit}` so one run can pick another profile
// without editing the file. A client that does not expand that syntax would hand us the literal,
// and a session that dies at startup over a config nicety is a worse failure than a default.
const RAW_PROFILE = (process.env.ARMORPIECES_BB_PROFILE || "").trim();
const PROFILE = /^\$\{/.test(RAW_PROFILE) || !RAW_PROFILE
  ? (RAW_PROFILE.match(/:-([\w]+)\}$/)?.[1] ?? "kit")
  : RAW_PROFILE;
const TEMP = join(tmpdir(), "armorpieces-bb");
const STATUS = join(TEMP, "status");
const CACHE = join(TEMP, "blockbench-tools.json");
const SNAPSHOT = join(HERE, "blockbench-tools.json");
const SCRATCH = "armorpieces_scratch";

if (!(PROFILE in PROFILES)) {
  throw new Error(`unknown ARMORPIECES_BB_PROFILE "${PROFILE}" (known: ${Object.keys(PROFILES).join(", ")})`);
}
const log = (msg) => process.stderr.write(`[armorpieces-bridge] ${msg}\n`);

// --- upstream ------------------------------------------------------------------------------------

/**
 * Who this server is to the plugin. MCPTK_SESSION is the id the mcp-toolkit shim binds projects
 * under; sharing it is what makes the shim's place_cube and this server's armorpieces_save one
 * session holding one piece rather than two sessions refusing each other.
 *
 * Nothing has to set it. The fallback is the PARENT process id - this session's `claude.exe`,
 * which both this server and the shim are direct children of - so the pair agrees, two concurrent
 * sessions never do, and no environment variable can leak it. The string must be IDENTICAL on both
 * sides, which is why the prefix is the shim's `mcptk-` and not this server's own name; `client`
 * is what says which of the two is calling. (mcp-toolkit
 * `docs/models/BLOCKBENCH_ISOLATION_DESIGN.md` section 6.1.)
 */
const SESSION = {
  id: (process.env.MCPTK_SESSION ?? "").trim() || `mcptk-${process.ppid}`,
  client: (process.env.MCPTK_CLIENT ?? "").trim() || "armorpieces-bridge",
  profile: PROFILE,
};

// A contact sheet or a piece being written back is a long call; a plugin sitting in a dialog for a
// human's own reasons is the case the message has to survive.
const CALL_TIMEOUT_MS = 120_000;
// A window either answers on localhost at once or is not there; the scan is the whole range at once.
const HELLO_TIMEOUT_MS = 1_000;

// --- which window --------------------------------------------------------------------------------
// THE HALF OF STEP 2 THAT LIVES HERE. A session is two processes - the mcp-toolkit shim and this
// server - and pinning this one to 25801 while the shim scanned would have undone the whole thing:
// the shim would take a window of its own, this server would keep calling into whatever window won
// the base port, and every unqualified call of the SECOND session on a machine would land in the
// FIRST session's window and be refused there. That is precisely the failure the A/B measured
// (mcp-toolkit `BLOCKBENCH_ISOLATION_DESIGN.md` section 9), so getting the toolkit's half right and
// leaving this one pinned would have measured the pin, not the fix.
//
// It needs no channel to the shim and no locking. Both processes compute the SAME session id from
// the parent pid, both walk the range in port order, and the plugin answers a claim from an id that
// already holds a window with a REJOIN - so whichever of the pair arrives second is handed the
// window the first one took, whether or not it saw the claim. Ladder: rejoin ours, claim a free one,
// share an unreserved one (the pre-0.139.0 behaviour, with `held_by` still guarding every edit).
// `POST /window` is deliberately NOT here: asking for a new window is for a session with none, and
// this server's session already has whatever the shim took.
//
// No presence socket either, and that is not an oversight - the shim holds one under the same id in
// the same window, so the session is connected there, and this server's claim lives exactly as long
// as its session does. What it must not do is hold a window the shim is not in.
let windowBase = null;
let resolvingWindow = null;

async function helloAt(base) {
  const res = await fetch(`${base}/hello`, { signal: AbortSignal.timeout(HELLO_TIMEOUT_MS) });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const h = await res.json();
  // Sixteen ports on localhost are sixteen chances to find some other service that answers JSON.
  if (!h || h.ok === false || h.app !== "blockbench") throw new Error("not Blockbench");
  return h;
}
async function claimAt(base) {
  try {
    const res = await fetch(`${base}/claim`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-MCPTK-Session": SESSION.id },
      body: JSON.stringify({ session: SESSION }),
      signal: AbortSignal.timeout(HELLO_TIMEOUT_MS),
    });
    // 404 is a plugin from before step 2: nothing to claim here, which is a window to use.
    if (res.status === 404) return null;
    return await res.json();
  } catch { return null; }
}
async function discoverWindow() {
  const found = [];
  const ports = [];
  for (let p = SCAN.from; p <= SCAN.to; p++) ports.push(p);
  await Promise.all(ports.map(async (port) => {
    const base = `http://${SCAN.host}:${port}`;
    try { found.push({ base, port, hello: await helloAt(base) }); } catch { /* nothing there */ }
  }));
  found.sort((a, b) => a.port - b.port);
  if (!found.length) throw new Error(`no Blockbench window answered on ${SCAN.host}:${SCAN.from}-${SCAN.to}`);
  const mine = found.find((w) => w.hello.claimed_by?.session === SESSION.id);
  if (mine) { log(`window ${mine.port} (${mine.hello.window}) — rejoined, this session already had it`); return mine.base; }
  for (const w of found) {
    if (!w.hello.window || w.hello.reserved || w.hello.claimed_by) continue;
    const env = await claimAt(w.base);
    if (env?.ok) { log(`window ${w.port} (${w.hello.window}) — claimed`); return w.base; }
  }
  const shareable = found.filter((w) => !w.hello.reserved);
  if (!shareable.length) {
    throw new Error(`every Blockbench window on ${SCAN.host}:${SCAN.from}-${SCAN.to} is reserved for the `
      + "person at the keyboard (Tools > MCP Toolkit Bridge > Reserve this window)");
  }
  const w = shareable[0];
  log(`window ${w.port} — SHARED with ${w.hello.claimed_by ? `session ${w.hello.claimed_by.session}` : "whoever is there"}; `
    + "name the project on every call");
  return w.base;
}
/**
 * The window this server works in, found once and remembered. One discovery at a time: two calls
 * arriving together must not both scan, or both could claim - and a window taken twice by one
 * session is a window denied to a session that has none.
 */
function upstream() {
  if (windowBase) return Promise.resolve(windowBase);
  if (PINNED) { windowBase = PINNED; claimAt(PINNED).catch(() => {}); return Promise.resolve(windowBase); }
  if (resolvingWindow) return resolvingWindow;
  resolvingWindow = discoverWindow().then((base) => { windowBase = base; return base; });
  resolvingWindow.catch(() => {}).then(() => { resolvingWindow = null; });
  return resolvingWindow;
}
/** Forget the window, so the next call discovers again: Blockbench may come back on another port. */
function forgetWindow() { windowBase = null; }
/** For a message: the window when there is one, the range that was searched when there is not. */
const where = () => windowBase ?? PINNED ?? `${SCAN.host}:${SCAN.from}-${SCAN.to}`;

function unreachable(e) {
  return new Error(
    `Blockbench is not answering at ${where()} (${e.message}). Open Blockbench with the Armor ` +
    "Pieces plugin loaded and start the bridge (Tools > MCP Toolkit Bridge > Start), then call again.",
  );
}

/** POST /cmd, and hand back the plugin's envelope. Throws with the plugin's own sentence on ok:false. */
async function bridge(name, args) {
  let base;
  try {
    base = await upstream();
  } catch (e) {
    // Discovery failing IS "Blockbench isn't open", and must say the same thing about it.
    throw unreachable(e);
  }
  let res;
  try {
    res = await fetch(`${base}/cmd`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-MCPTK-Session": SESSION.id },
      body: JSON.stringify({ tool: name, args: args ?? {}, session: SESSION }),
      signal: AbortSignal.timeout(CALL_TIMEOUT_MS),
    });
  } catch (e) {
    if (e.name === "TimeoutError" || e.name === "AbortError") {
      throw new Error(
        `Blockbench accepted "${name}" but gave no answer within ${CALL_TIMEOUT_MS / 1000}s. It may ` +
        "be sitting in a dialog of its own; ask the person at the keyboard to look at the window " +
        "before treating this as a dead bridge.");
    }
    // The window we were working in is gone. Forget it, so the next call discovers again: a
    // Blockbench that restarts may come back as a different window on a different port. A TIMEOUT is
    // not this - that is a live window sitting in a dialog, and its port is still the right one.
    forgetWindow();
    throw unreachable(e);
  }
  let env;
  try {
    env = await res.json();
  } catch {
    throw new Error(`Blockbench answered "${name}" with HTTP ${res.status} and no JSON`);
  }
  if (!env || env.ok !== true) {
    const msg = env?.error ?? `HTTP ${res.status}`;
    throw new Error(env?.hint ? `${msg}. ${env.hint}` : msg);
  }
  return env;
}

/**
 * A picture costs about (width x height) / 750 tokens and, unlike a tool's text, it is re-sent on
 * every turn for the rest of the session: Blockbench's ~1020x946 viewport is ~1300 tokens a look, so
 * the six looks a skin needs outweigh every text reply in the session put together. shrink_shot.py
 * crops to the figure BEFORE resizing - half the viewport is empty ground, and empty ground costs
 * the same as armor - which brings a look to ~120 tokens with more resolution on the figure than
 * before. 0 keeps them whole.
 */
const SHOT_MAX = Number(process.env.ARMORPIECES_SHOT_MAX ?? 384);

async function shrinkImages(result) {
  const parts = result?.content ?? [];
  if (!SHOT_MAX || !parts.some((p) => p.type === "image" && p.data)) return result;
  const content = [];
  for (const part of parts) {
    if (part.type !== "image" || !part.data) {
      content.push(part);
      continue;
    }
    const file = join(TEMP, `shot-${process.pid}.png`);
    try {
      mkdirSync(TEMP, { recursive: true });
      writeFileSync(file, Buffer.from(part.data, "base64"));
      const { error } = await run([join(ROOT, "tools", "shrink_shot.py"), file, String(SHOT_MAX)]);
      content.push(error ? part : { ...part, data: readFileSync(file).toString("base64") });
    } catch {
      content.push(part);
    }
  }
  return { ...result, content };
}

/**
 * A Blockbench tool as MCP content. The plugin puts a picture under `_image` on the result rather
 * than in an image part, so that is unwrapped here (and the rest of the result kept beside it).
 */
async function callUpstream(name, args) {
  const result = (await bridge(name, args)).result ?? {};
  if (result && typeof result === "object" && result._image) {
    const { _image, ...rest } = result;
    const content = [{ type: "image", data: _image.base64, mimeType: _image.mimeType ?? "image/png" }];
    if (Object.keys(rest).length) content.push({ type: "text", text: JSON.stringify(rest) });
    return await shrinkImages({ content });
  }
  return { content: [{ type: "text", text: typeof result === "string" ? result : JSON.stringify(result) }] };
}

/**
 * Run JavaScript inside Blockbench through the plugin's risky_eval, and hand back the value.
 *
 * The bridge's eval is an ordinary one: the completion value comes back as `result.value` already
 * parsed, a returned Promise is awaited, and a throw is an `ok:false` envelope that `bridge` has
 * already turned into an Error - so there is no "Error executing code:" prefix to strip and no
 * comment filter to write around. What survives from the old plugin is the no-project case: the
 * Armor Pieces api needs a tab, and a scratch project is how one is had.
 */
async function evalIn(code, { retryWithProject = true } = {}) {
  try {
    // NAME THE PROJECT. `armorpieces_api` reads Blockbench's global `Project`, so an eval that does
    // not say which project it means runs against whatever the plugin selected last - and the
    // plugin selects by SESSION binding, not by caller. Two headless sessions that present one
    // session id (a `claude -p` child inherits CLAUDE_CODE_SESSION_ID from its parent, so every
    // child of one session did) therefore share one binding, and the second one's part data,
    // paint, check and save all resolve to the FIRST one's piece. Measured 2026-09-07 on
    // kelp_mantle: a dozen bare calls answered about coral_crown, and one set_part executed
    // against it. Passing the uuid makes each of these tools address its own piece whatever the
    // binding says, which is the property the tools always claimed to have.
    // Since plugin 0.2.0 the eval's scope carries PROJECT - the project the bridge actually
    // resolved. `armorpieces_api` still reads Blockbench's GLOBAL `Project`, so the two must agree
    // or the API would act on the wrong tab; asserting it INSIDE the eval turns that into a throw
    // before anything is written, instead of a reply we notice afterwards. Guarded on `typeof` so
    // an older plugin still runs.
    const guarded = bound
      ? `(function () { if (typeof PROJECT !== 'undefined' && PROJECT) {`
        + ` if (PROJECT.uuid !== ${JSON.stringify(bound.uuid)}) throw new Error('the bridge is bound to `
        + `${bound.name} but this eval resolved to ' + PROJECT.name);`
        + ` if (PROJECT !== Project) throw new Error('armorpieces_api reads the global Project, which is '`
        + ` + (Project ? Project.name : 'nothing') + ', not ' + PROJECT.name); }`
        + ` return (${code}); })()`
      : code;
    const args = bound ? { code: guarded, project: bound.uuid } : { code };
    const { result } = await bridge("risky_eval", args);
    const ran = result && typeof result === "object" ? result.project : null;
    if (bound && ran && ran.name && ran.name !== bound.name) {
      throw new Error(
        `Refusing the result: this bridge is bound to "${bound.name}" but Blockbench ran that ` +
        `against "${ran.name}". Re-open your piece with armorpieces_open and try again.`);
    }
    return result && typeof result === "object" && "value" in result ? result.value : result;
  } catch (e) {
    if (retryWithProject && /no project|finishEdit|Project is (null|undefined)/i.test(String(e?.message))) {
      await bridge("project", { op: "new", name: SCRATCH, format: "free" });
      return evalIn(code, { retryWithProject: false });
    }
    throw e;
  }
}

/**
 * Bind this session to the tab a piece was just opened into.
 *
 * The plugin binds a session to a project it made or opened, and a session with no binding acts on
 * "whatever tab is active" - which is the hazard the Animals pack was built under and lost a piece
 * to (a bee's bone in the fox, set-packs.md "the active-tab hazard"). A piece is opened through the
 * Armor Pieces api rather than through `project op:open`, so the binding has to be claimed here,
 * afterwards; from then on every call this server and the shim make - they share MCPTK_SESSION -
 * goes to this piece by name, and another live session's edit to it is refused with `held_by`.
 *
 * Best effort: an unbound session still works, it is just the old, sharper knife.
 */
let bound = null;

async function bindActive(expectKey) {
  bound = null;
  // FIND THE PIECE'S OWN PROJECT, never the active tab. Reading the global `Project` here was the
  // bug behind the 2026-09-08 A/B: `armorpieces_new` opens a piece out of a scratch project, and
  // `evalIn`'s no-project retry creates that scratch with `project op:new` - which BINDS the
  // session to it. So while the scratch is up the session is not unbound, it is bound to the WRONG
  // project; every later call resolves there BY BINDING rather than by active-tab fallback, which
  // is why it survived the piece tab becoming active and why the piece answered "no piece is open"
  // 30 times in one solo session. Second order and worse: this function left the local `bound`
  // null, and `evalIn` applies its PROJECT arbiter only `if (bound)` - so the guard added in
  // 0.135.0 to catch a wrong-project eval was switched off in exactly the state that trips it.
  //
  // The plugin keeps a project's piece on the project object (`Project[ID + '_piece']`, read by
  // `currentPiece()`), so every open tab's key is readable WITHOUT selecting it. Scan for the key
  // we were asked for and select that uuid. Failing to find it stays unbound, which is safe.
  const look = async () => evalIn(
    "(function () { var want = " + JSON.stringify(expectKey ?? null) + "; var out = null;"
    + " ModelProject.all.forEach(function (p) {"
    + "   var piece = p['armorpieces_piece'];"
    + "   if (!piece || !piece.key) return;"
    + "   if (want) { if (piece.key === want) out = { uuid: p.uuid, name: p.name, key: piece.key }; }"
    + "   else if (!out) out = { uuid: p.uuid, name: p.name, key: piece.key };"
    + " });"
    + " return out; })()",
    { retryWithProject: false },
  );
  try {
    let info = await look();
    if (!info) {
      await new Promise((r) => setTimeout(r, 250));   // the tab may still be coming up
      info = await look();
    }
    if (!info || !info.uuid) {
      log(`bind: no open project carries piece ${expectKey ?? "(any)"}; staying unbound`);
      return null;
    }
    const { result } = await bridge("project", { op: "select", project: info.uuid });
    bound = info;
    return result;
  } catch (e) {
    log(`bind: ${e.message}`);
    return null;
  }
}

/**
 * Close the scratch project a piece was opened from. Runs AFTER bindActive, so this session is
 * already pointing at the piece and the scratch is a project nothing is bound to.
 *
 * Through `project op:close`, not a raw `s.close(true)` eval. The plugin's own op nulls every
 * session bound to that uuid; closing the project object behind the plugin's back does not, and
 * leaves any such session bound to a dead uuid it only discovers on its next call. The old
 * `s !== Project` condition is gone with it: it was load-bearing only because the binding was
 * wrong, and it was also the reason the scratch was never closed in the one case that mattered -
 * when the scratch WAS the active project. With the piece selected by key first, neither is true.
 */
async function dropScratch() {
  try {
    const uuid = await evalIn(
      `(function () { var s = ModelProject.all.find(function (p) { return p.name === '${SCRATCH}'; });` +
      ` return s ? s.uuid : null; })()`,
      { retryWithProject: false },
    );
    if (!uuid) return;
    await bridge("project", { op: "close", project: uuid, force: true });
  } catch (e) {
    log(`scratch: ${e.message}`);
  }
}

// --- the plugin's status, and the check over it ----------------------------------------------------

function readJson(file) {
  try {
    return JSON.parse(readFileSync(file, "utf8"));
  } catch {
    return null;
  }
}

/** meta.json of the active piece, with `dir` added, or null when no piece is open. */
function readMeta() {
  const current = readJson(join(STATUS, "current.json"));
  if (!current?.uuid) return null;
  const dir = join(STATUS, current.uuid);
  const meta = readJson(join(dir, "meta.json"));
  return meta ? { ...meta, dir } : null;
}

function run(args, { timeout = 90_000 } = {}) {
  return new Promise((done) => {
    execFile(PYTHON, args, { cwd: ROOT, timeout, windowsHide: true, maxBuffer: 16 << 20 },
      (error, stdout, stderr) => done({ error, stdout: stdout ?? "", stderr: stderr ?? "" }));
  });
}

/**
 * The check over whatever is active: check_part.py for a piece, check_skin.py for an armor skin.
 * The plugin says which in meta.kind, so one code path serves both and every editing call gets the
 * check that applies to it. The report comes back as data, or as a string when it could not run.
 */
/**
 * The check of whatever piece is active, through tools/check_active.py.
 *
 * Not check_part.py directly, though this used to call it directly and could: the sheet layout of
 * the cubes that moved and the "! repaint: a face that was complete and GREW" line are diffs
 * against the LAST CHECK, and in a kit session two servers edit one piece - Blockbench through the
 * mcp-toolkit shim (which runs check_active.py from .mcptoolkit/loop.json) and these nine tools
 * here. Two histories over one piece is a paint through this server and a resize through the other
 * comparing against a state where the face was never painted, so the regrow goes unsaid. One
 * checker, one history file beside the piece's status directory, both servers reading it.
 *
 * `layout` false is for the callers that print the whole report anyway (open, new, check, save):
 * the block is for the reply to an EDIT.
 */
async function runCheck(meta, layout = true) {
  const args = [join(ROOT, "tools", "check_active.py"), "--json", "--brief"];
  if (!layout) args.push("--no-layout");
  const { stdout, stderr } = await run(args);
  const line = stdout.trim().split("\n").pop() ?? "";
  try {
    return JSON.parse(line);
  } catch {
    return `[armorpieces] the check could not run: ${(stderr || stdout).trim().split("\n").pop()}`;
  }
}

function header(meta) {
  if (meta.kind === "skin") {
    const skinBits = [];
    if (meta.unsaved_edits) skinBits.push(`${meta.unsaved_edits} unsaved edit(s)`);
    skinBits.push(meta.material ? `shown on ${meta.material}` : "shown as the greyscale master");
    return `skin ${meta.skin} · ${skinBits.join(" · ")}`;
  }
  const bits = [];
  if (meta.unsaved_edits) bits.push(`${meta.unsaved_edits} unsaved edit(s)`);
  if (meta.part_dirty) bits.push("part data changed, unsaved");
  bits.push(`editing ${meta.editing === "fitting" ? `mask ${meta.fitting}` : meta.editing}`);
  return `${meta.piece?.key} on ${meta.anchor} · sheet ${meta.sheet?.join("x")} · ${bits.join(" · ")}`;
}

/**
 * A piece just opened publishes its sheets a moment after its model: Blockbench loads the images
 * asynchronously and the plugin republishes each one as it lands. Wait for the master, briefly.
 */
async function settled(meta, ms = 2000) {
  const until = Date.now() + ms;
  const first = meta.kind === "skin" ? "humanoid.png" : "master.png";
  while (Date.now() < until) {
    if (existsSync(join(meta.dir, first))) {
      await new Promise((r) => setTimeout(r, 120));
      return readMeta() ?? meta;
    }
    await new Promise((r) => setTimeout(r, 60));
  }
  return readMeta() ?? meta;
}

async function checkText(meta, full = false, withReferences = false) {
  const report = await runCheck(meta, false);
  if (typeof report === "string") return report;
  const text = full ? report.full : report.text;
  // On open and new, the envelopes of the parts this one is placed against ride along once, so
  // "the hairline height the circlet uses" is a number in the reply rather than a tab to open.
  const refs = withReferences && !full ? referenceText(report) : "";
  return `${header(meta)}\n${text}${refs ? `\n${refs}` : ""}`;
}

function referenceText(report) {
  const refs = report.references;
  if (!refs) return "";
  const row = (r) => {
    const g = ["x", "y", "z"].map((a, i) => `${a} ${r.lo[i].toFixed(2)}..${r.hi[i].toFixed(2)}`).join("  ");
    const b = ["x", "y", "z"].map((a, i) => `${a} ${r.bb_lo[i].toFixed(2)}..${r.bb_hi[i].toFixed(2)}`).join("  ");
    return `    ${r.part.padEnd(14)} ${g}  |  ${b}`;
  };
  const lines = [`  other parts on ${refs.bone}: bone-local (+Y down)  |  Blockbench`];
  if (refs.same_socket.length) {
    lines.push("   same socket, never compared - the heights and depths to place against:");
    lines.push(...refs.same_socket.map(row));
  }
  if (refs.mates.length) {
    lines.push("   other sockets on the bone, worn together - what clash lines measure:");
    lines.push(...refs.mates.map((r) => `${row(r)}  (${r.socket})`));
  }
  return lines.join("\n");
}

/** Append the check to an editing call's reply when the call changed the piece. The sheet layout of
 * the cubes that moved and the regrow diff are inside `text`, computed by check_active.py against
 * the piece's own history - see runCheck. */
async function withCheck(name, seqBefore, result) {
  if (name === "undo" || name === "redo") await new Promise((r) => setTimeout(r, 350));
  const meta = readMeta();
  if (!meta || meta.seq === seqBefore) return result;
  const report = await runCheck(meta);
  const text = typeof report === "string" ? report : report.text;
  return { ...result, content: [...(result.content ?? []), { type: "text", text }] };
}

const reply = (text, isError = false) => ({ content: [{ type: "text", text }], isError });

// --- armor skins -----------------------------------------------------------------------------------

const SKIN_SHEETS = ["humanoid", "humanoid_leggings"];

/**
 * The nets of the two skin sheets and their face rectangles, from skin_sheets.py - which reads them
 * out of mc_humanoid, which transcribed them from the game. Asked for once: they change when
 * Minecraft's armor mesh does, not while a session runs.
 */
let regionCache = null;

async function skinRegions() {
  if (regionCache) return regionCache;
  const { stdout, stderr } = await run([join(ROOT, "tools", "skin_sheets.py"), "--regions", "--json"]);
  try {
    regionCache = JSON.parse(stdout.trim().split("\n").pop());
  } catch {
    throw new Error(`could not read the sheet nets: ${(stderr || stdout).trim().split("\n").pop()}`);
  }
  return regionCache;
}

/**
 * What a step between two master levels actually buys after the bake (bake_skin.py --contrast).
 * Vanilla's armor textures repeat colours, so a shading step that reads in greyscale can come
 * out identical on iron - the first skin drawn here lost a whole pass to exactly that. Asked
 * for once: it changes when the vanilla textures do.
 */
let contrastCache = null;

async function contrastText() {
  if (contrastCache) return contrastCache;
  try {
    const { stdout } = await run([join(ROOT, "tools", "bake_skin.py"), "--contrast", "--rule"]);
    contrastCache = stdout.trim();
  } catch {
    contrastCache = "contrast: shade in bands 4-5 levels apart (bake_skin.py --contrast).";
  }
  return contrastCache;
}

/** The net legend as lines, so a session sees where every face is without opening a file. */
async function legendText() {
  const table = await skinRegions();
  const lines = [];
  for (const sheet of SKIN_SHEETS) {
    lines.push(`nets on ${sheet} (face x,y w x h):`);
    for (const region of Object.values(table)) {
      if (region.sheet !== sheet) continue;
      const faces = Object.entries(region.faces)
        .map(([face, r]) => `${face} ${r[0]},${r[1]} ${r[2]}x${r[3]}`).join("  ");
      const both = region.both_sides ? ", both sides" : "";
      lines.push(`  ${region.region} (${region.slot}, inflate ${region.inflate}${both}): ${faces}`);
    }
  }
  return lines.join("\n");
}

/** A sheet's rows with a column ruler, which is what makes a coordinate readable at a glance. */
function sheetText(sheet, rows) {
  const width = rows[0]?.length ?? 64;
  const tens = "    " + Array.from({ length: width }, (_, x) => (x % 10 === 0 ? String((x / 10) % 10) : " ")).join("");
  const ones = "    " + Array.from({ length: width }, (_, x) => String(x % 10)).join("");
  return [`${sheet} (${width}x${rows.length})`, tens, ones,
    ...rows.map((row, y) => `${String(y).padStart(3)} ${row}`)].join("\n");
}

// --- the armorpieces_* tools ---------------------------------------------------------------------

const OWN = {
  armorpieces_pieces: {
    description:
      "Every Armor Piece the plugin can find - in the packs added under Packs..., in this " +
      "repository, and in the game's own folders - as `namespace:name` with its pack folders, " +
      "plus which pieces are open in tabs right now and whether they carry unsaved edits.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
    async execute() {
      const data = await evalIn(
        `(function () { var api = window.armorpieces_api; var open = ModelProject.all.filter(function (p) {` +
        ` return p.armorpieces_piece; }).map(function (p) { return { key: p.armorpieces_piece.key,` +
        ` anchor: p.armorpieces_state && p.armorpieces_state.anchor, active: p === Project,` +
        ` unsaved_edits: p.undo ? p.undo.index - (p.armorpieces_saved_index || 0) : 0 }; });` +
        ` return { pieces: api.pieces().map(function (p) { return { key: p.key, datapack: p.dataPack,` +
        ` resourcepack: p.assetPack }; }), open: open, packs: api.packs() }; })()`,
      );
      // One line per pack pair rather than one record per piece: thirty-odd pieces share a pack.
      const byPack = new Map();
      for (const p of data.pieces) {
        const where = p.datapack === p.resourcepack ? p.datapack : `${p.datapack} + ${p.resourcepack}`;
        if (!byPack.has(where)) byPack.set(where, []);
        byPack.get(where).push(p.key);
      }
      const lines = [];
      for (const [where, keys] of byPack) lines.push(`${where}:\n  ${keys.join(", ")}`);
      lines.push(data.open.length
        ? "open: " + data.open.map((o) => `${o.key} on ${o.anchor}${o.active ? " (active)" : ""}${o.unsaved_edits ? ` [${o.unsaved_edits} unsaved]` : ""}`).join("; ")
        : "open: none");
      return reply(lines.join("\n"));
    },
  },

  armorpieces_open: {
    description:
      "Open an Armor Piece on its rig as the active tab, or switch to its tab if it is already " +
      "open. `anchor` rebuilds the rig on another of the part's sockets (the geometry is reloaded " +
      "from disk, so save first). A tab with unsaved edits is refused unless `discard` is true. " +
      "The reply ends with the piece's check.",
    inputSchema: {
      type: "object",
      properties: {
        piece: { type: "string", description: "`namespace:name`, as armorpieces_pieces lists it." },
        anchor: { type: "string", description: "Socket to rig on; default the part's first." },
        discard: { type: "boolean", default: false, description: "Drop unsaved edits in an open tab." },
        reload: { type: "boolean", default: false, description: "Rebuild from disk even on the same anchor." },
      },
      required: ["piece"],
      additionalProperties: false,
    },
    async execute({ piece, anchor, discard, reload }) {
      bound = null;
      const opts = JSON.stringify({ discard: !!discard, reload: !!reload });
      const out = await evalIn(
        `window.armorpieces_api.openFor(${JSON.stringify(piece)}, ${JSON.stringify(anchor ?? null)}, ${opts})`,
      );
      // Bind FIRST, then drop the scratch: closing it while the session still points at it is what
      // leaves a session bound to nothing (or, before this order, bound to the scratch itself).
      await bindActive(typeof out?.piece === "string" ? out.piece : undefined);
      await dropScratch();
      let meta = readMeta();
      if (meta) meta = await settled(meta);
      const check = meta ? await checkText(meta, false, true) : "(no status published - is the Armor Pieces plugin loaded?)";
      return reply(`${JSON.stringify(out)}\n${check}`);
    },
  },

  armorpieces_new: {
    description:
      "Create a new Armor Piece - its data file with one socket, a starter model (one bone, one " +
      "cube on the anchor), a blank 64x32 master and its language line - and open it. Packs " +
      "default to the first folder the plugin searches (the repository's src/main/resources when " +
      "the bridge runs from the repository); the namespace defaults to `armorpieces` there and " +
      "`mypack` elsewhere. Fittings, effects and loot come after, with armorpieces_set_part.",
    inputSchema: {
      type: "object",
      properties: {
        name: { type: "string", description: "Part id: lowercase, digits and underscores." },
        anchor: { type: "string", description: "The socket: crest, brow, horns, pauldrons, back, collar, vambraces, belt, tassets, knees, spurs or greaves." },
        namespace: { type: "string" },
        datapack: { type: "string", description: "Folder holding data/ - where the part file goes." },
        resourcepack: { type: "string", description: "Folder holding assets/ - where model, texture and language file go. The same folder is fine." },
      },
      required: ["name", "anchor"],
      additionalProperties: false,
    },
    async execute({ name, anchor, namespace, datapack, resourcepack }) {
      bound = null;
      // A pack folder that exists on disk is INVISIBLE to the plugin until it is in the
      // `armorpieces_packs` setting: `api.create` happily writes the piece's files into it and then
      // every later armorpieces_* call fails, because the plugin never scanned that root. That cost
      // a whole session on the Dragonslayer pack's first piece (2026-09-08). Register whatever the
      // caller explicitly named, before creating anything. `userPacks()` re-reads the setting on
      // every call, so this takes effect immediately - no restart, no rescan.
      const registered = await evalIn(
        `(function () { var want = ${JSON.stringify([datapack, resourcepack].filter((d) => typeof d === "string" && d))};`
        + ` var list = []; try { list = JSON.parse(Settings.get('armorpieces_packs') || '[]') || []; } catch (e) { list = []; }`
        + ` if (!Array.isArray(list)) list = [];`
        + ` var added = [];`
        + ` want.forEach(function (d) { if (list.indexOf(d) === -1) { list.push(d); added.push(d); } });`
        + ` if (added.length) { settings['armorpieces_packs'].set(JSON.stringify(list)); Settings.save(); }`
        + ` return added; })()`,
      );
      const out = await evalIn(
        `(function () { var api = window.armorpieces_api; var packs = api.packs(); var dp = ${JSON.stringify(datapack ?? null)} || packs[0];` +
        ` var rp = ${JSON.stringify(resourcepack ?? null)} || dp; if (!dp) throw new Error('no pack folder to put the piece in');` +
        ` var root = Settings.get('armorpieces_root'); var ns = ${JSON.stringify(namespace ?? null)} || ((root && dp.indexOf(root) === 0) ? 'armorpieces' : 'mypack');` +
        ` return api.create(dp, rp, ns, ${JSON.stringify(name)}, ${JSON.stringify(anchor)}); })()`,
      );
      // Bind FIRST, then drop the scratch: closing it while the session still points at it is what
      // leaves a session bound to nothing (or, before this order, bound to the scratch itself).
      await bindActive(typeof out?.piece === "string" ? out.piece : undefined);
      await dropScratch();
      let meta = readMeta();
      if (meta) meta = await settled(meta);
      const check = meta ? await checkText(meta, false, true) : "";
      const note = Array.isArray(registered) && registered.length
        ? `registered pack root(s) with the plugin: ${registered.join(", ")}\n`
        : "";
      return reply(`${JSON.stringify(out, null, 1)}\n${note}${check}`);
    },
  },

  armorpieces_check: {
    description:
      "The full check of the open piece, as tools/check_part.py prints it: the bone chain and " +
      "envelope, clearance past the body and every armor shell, faces on a shell, what the part " +
      "shares its bone with and any clash, then the sheets - unpainted faces, stray paint, colour " +
      "on a greyscale sheet - and the verdict. Lines marked ! are problems that need a decision; " +
      "- lines are notes.",
    inputSchema: {
      type: "object",
      properties: { brief: { type: "boolean", default: false, description: "Only the compact block." } },
      additionalProperties: false,
    },
    async execute({ brief }) {
      const meta = readMeta();
      if (!meta) return reply("No piece is open in the Armor Pieces plugin. armorpieces_open one first.", true);
      return reply(await checkText(meta, !brief));
    },
  },

  armorpieces_save: {
    description:
      "Save the open piece back into its pack: the geometry through bb_geo, every sheet to its " +
      "file, the template recipe, and the data file and language line when the part changed. For " +
      "a part of the mod itself the master is installed into the resources by " +
      "sync_decoration_masters.py, whose report is returned. Refused while the check reports " +
      "problems, unless `force` is true - say why in that case.",
    inputSchema: {
      type: "object",
      properties: { force: { type: "boolean", default: false, description: "Save despite problems." } },
      additionalProperties: false,
    },
    async execute({ force }) {
      const meta = readMeta();
      if (!meta) return reply("No piece is open in the Armor Pieces plugin.", true);
      const report = await runCheck(meta);
      if (typeof report !== "string" && !report.ok && !force) {
        return reply(
          `Not saved: ${report.problems.length} problem(s) need a decision first.\n${report.text}\n` +
          `Fix them, or call again with force: true and say why each is acceptable.`,
          true,
        );
      }
      const out = await evalIn("window.armorpieces_api.save()");
      const lines = [`Saved ${out.piece}: ${out.wrote.join(", ")}.`];
      if (out.report) lines.push(out.report);
      if (typeof report === "string") lines.push(report);
      else if (!report.ok) lines.push(`Saved with problems standing:\n${report.text}`);
      return reply(lines.join("\n"));
    },
  },

  armorpieces_part: {
    description:
      "The datapack half of the open piece: the part file as it stands (unsaved edits included), " +
      "the name a player reads, its resolved fittings, every fitting definition the pack and the " +
      "mod offer, the template recipe, and the socket table (anchor -> bone).",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
    async execute() {
      const data = await evalIn(
        `(function () { var api = window.armorpieces_api; if (!api.isWorkspace()) throw new Error('no piece is open');` +
        ` var piece = api.currentPiece(); var sockets = {}; var table = api.anchors();` +
        ` Object.keys(table).forEach(function (k) { sockets[k] = table[k].part + (table[k].mirrored ? ' (mirrored pair)' : ''); });` +
        ` var brief = function (f) { return { id: f.id, type: f.type, masked: f.masked, bone: f.bone || undefined,` +
        ` label: f.label, options: (f.options || []).map(function (o) { return o.value; }) }; };` +
        ` return { piece: piece.key, name: api.displayName().text, data: api.data(),` +
        ` fittings: api.fittings().map(brief), available_fittings: api.availableFittings().map(brief),` +
        ` recipe: api.readRecipe(piece), sockets: sockets, files: { data: piece.data, geometry: piece.geometry, texture: piece.texture } }; })()`,
      );
      return reply(JSON.stringify(data, null, 1));
    },
  },

  armorpieces_set_part: {
    description:
      "Change the datapack half of the open piece, written on the next save: the display name, " +
      "the sockets it may occupy (the first stays the recipe's), its fittings in order, its effects, " +
      "its loot rows, and the template recipe. Fields left out keep their value. A masked fitting " +
      "gets its mask sheet created at once (`part_<fitting>`, blank, ready to paint); `static: true` " +
      "creates the colour layer `part_static`. Effects are the objects the part file holds " +
      "(`{\"type\": \"armorpieces:...\", ...}`; armorpieces_part shows the current ones); loot rows " +
      "are `{table, weight, chance}`; the recipe is `{centre, ring, craftable}` with vanilla item " +
      "ids, ring defaulting to paper.",
    inputSchema: {
      type: "object",
      properties: {
        name: { type: "string" },
        anchors: { type: "array", items: { type: "string" } },
        fittings: { type: "array", items: { type: "string" }, description: "Fitting ids, `namespace:name`, in the order their masks are applied." },
        effects: { type: "array", items: { type: "object" } },
        loot: { type: "array", items: { type: "object" } },
        static: { type: "boolean", description: "Create the static (real colour) layer." },
        recipe: {
          type: "object",
          properties: {
            centre: { type: "string", description: "The item in the middle of the paper ring, e.g. minecraft:iron_nugget." },
            ring: { type: "string", description: "The four ring items; default minecraft:paper." },
            craftable: { type: "boolean", description: "False writes the recipe disabled, for a part that is found, not made." },
          },
          additionalProperties: false,
        },
      },
      additionalProperties: false,
    },
    async execute(args) {
      const data = await evalIn(
        `(function () { var api = window.armorpieces_api; if (!api.isWorkspace()) throw new Error('no piece is open');` +
        ` var d = api.data(); var a = ${JSON.stringify(args)}; var out = {};` +
        ` api.applyPartEdit(a.name !== undefined ? a.name : api.displayName().text, a.anchors || d.anchors || [],` +
        ` a.fittings || d.fittings || [], a.effects || d.effects || [], a.loot || d.loot || []);` +
        ` if (a.recipe) out.recipe = api.setRecipe(a.recipe.centre, a.recipe.ring, a.recipe.craftable);` +
        ` out.sheets_created = api.ensureSheets(); if (a.static) out.static_created = api.ensureStatic();` +
        ` api.publish(); out.name = api.displayName().text; out.data = api.data(); return out; })()`,
      );
      return reply(JSON.stringify(data, null, 1));
    },
  },

  armorpieces_paint: {
    description:
      "Paint whole faces of the open piece's cubes on one sheet, in one undo step. `faces` maps " +
      "a face address to a value. The address is `<cube>.<face>`: the cube by the name you gave it " +
      "or by the check's `bone[i]` label, `*` for every part cube or every face (`plate.*`, `*.up`). " +
      "The value is a grey 0-255 on the master and the masks (a hex colour there is folded to its " +
      "luminance), a `#rrggbb` colour on `part_static`, a `[top, bottom]` pair shaded row by row " +
      "from the top of the face down, or null to clear the face. `pixels` is a list of " +
      "`{x, y, value}` sheet texels for a highlight or a rivet. Later entries paint over earlier " +
      "ones, so `\"*.*\": 140` then `\"*.up\": 200` is a lit top. The reply ends with the check, so " +
      "the unpainted-face count comes down with it. A Spire-sized part is one call per sheet.",
    inputSchema: {
      type: "object",
      properties: {
        sheet: { type: "string", default: "part", description: "`part` (master), `part_static`, or `part_<fitting>`." },
        faces: {
          type: "object",
          description: "Face address -> value. Object key order is paint order.",
          additionalProperties: {
            anyOf: [
              { type: "number" }, { type: "string" }, { type: "null" },
              { type: "array", minItems: 2, maxItems: 2, items: { anyOf: [{ type: "number" }, { type: "string" }] } },
            ],
          },
        },
        pixels: {
          type: "array",
          items: {
            type: "object",
            properties: {
              x: { type: "integer" }, y: { type: "integer" },
              value: { anyOf: [{ type: "number" }, { type: "string" }, { type: "null" }] },
            },
            required: ["x", "y"],
            additionalProperties: false,
          },
        },
      },
      additionalProperties: false,
    },
    async execute({ sheet, faces, pixels }) {
      const seqBefore = readMeta()?.seq;
      const out = await evalIn(
        `window.armorpieces_api.paintFaces(${JSON.stringify(sheet ?? "part")}, ${JSON.stringify(faces ?? {})}, ${JSON.stringify(pixels ?? [])})`,
      );
      const summary = `Painted ${out.faces.length} face(s)${out.pixels ? ` and ${out.pixels} pixel(s)` : ""} on ${out.sheet}:\n  ${out.faces.join("\n  ")}`;
      return await withCheck("armorpieces_paint", seqBefore, reply(summary));
    },
  },

  armorpieces_close: {
    description: "Close the open piece's tab. Refused with unsaved edits unless `discard` is true.",
    inputSchema: {
      type: "object",
      properties: { discard: { type: "boolean", default: false } },
      additionalProperties: false,
    },
    async execute({ discard }) {
      const out = await evalIn(`window.armorpieces_api.close(${!!discard})`);
      bound = null;
      return reply(JSON.stringify(out));
    },
  },

  armorpieces_skins: {
    description:
      "Every armor skin under tools/skin_masters - a skin is the armor's OWN texture, one greyscale " +
      "pair on vanilla's grid, coloured per material at load time - plus which are open in tabs and " +
      "whether they carry unsaved edits.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
    async execute() {
      const data = await evalIn(
        `(function () { var api = window.armorpieces_api;` +
        ` var open = ModelProject.all.filter(function (p) { return p.armorpieces_skin; }).map(function (p) {` +
        ` return { name: p.armorpieces_skin.name, active: p === Project,` +
        ` unsaved_edits: p.undo ? p.undo.index - (p.armorpieces_saved_index || 0) : 0 }; });` +
        ` return { skins: api.skins(), open: open }; })()`,
      );
      const lines = data.skins.length
        ? ["skins: " + data.skins.map((s) => s.name).join(", ")]
        : ["no skins yet - python tools/skin_sheets.py --new <name> starts one"];
      lines.push(data.open.length
        ? "open: " + data.open.map((o) => `${o.name}${o.active ? " (active)" : ""}${o.unsaved_edits ? ` [${o.unsaved_edits} unsaved]` : ""}`).join("; ")
        : "open: none");
      return reply(lines.join("\n"));
    },
  },

  armorpieces_open_skin: {
    description:
      "Open an armor skin as the active tab: the vanilla player wearing all four armor slots, at " +
      "their real inflate, painted by the skin's own two sheets. Nothing is modelled here - the " +
      "geometry is vanilla's - so the whole job is what is painted on `humanoid` (helmet, " +
      "chestplate, boots) and `humanoid_leggings` (belt and legs). The reply carries the net " +
      "legend, every face rectangle, and the check.",
    inputSchema: {
      type: "object",
      properties: {
        skin: { type: "string", description: "A folder name under tools/skin_masters." },
        discard: { type: "boolean", default: false, description: "Drop unsaved edits when reloading." },
        reload: { type: "boolean", default: false, description: "Rebuild the rig and re-read both sheets from disk." },
      },
      required: ["skin"],
      additionalProperties: false,
    },
    async execute({ skin, discard, reload }) {
      const opts = JSON.stringify({ discard: !!discard, reload: !!reload });
      const out = await evalIn(
        `window.armorpieces_api.openSkin(${JSON.stringify(skin)}, ${opts})`,
      );
      // Bind FIRST, then drop the scratch: closing it while the session still points at it is what
      // leaves a session bound to nothing (or, before this order, bound to the scratch itself).
      await bindActive(typeof out?.piece === "string" ? out.piece : undefined);
      await dropScratch();
      let meta = readMeta();
      if (meta) meta = await settled(meta);
      const check = meta ? await checkText(meta) : "(no status published - is the Armor Pieces plugin loaded?)";
      return reply(`${JSON.stringify(out)}\n${await legendText()}\n${await contrastText()}\n${check}`);
    },
  },

  armorpieces_skin_sheet: {
    description:
      "Read a skin's sheet back as it stands, as rows of characters with a column ruler: `.` is " +
      "transparent, `0`-`9` and `a`-`f` are the sixteen greys (level i is the value 17i). Both " +
      "sheets unless one is named. This is the sheet Blockbench is showing, unsaved edits included.",
    inputSchema: {
      type: "object",
      properties: { sheet: { type: "string", description: "`humanoid` or `humanoid_leggings`; default both." } },
      additionalProperties: false,
    },
    async execute({ sheet }) {
      const wanted = sheet ? [sheet] : SKIN_SHEETS;
      const parts = [];
      for (const id of wanted) {
        const rows = await evalIn(`window.armorpieces_api.skinAscii(${JSON.stringify(id)})`);
        parts.push(sheetText(id, rows));
      }
      return reply(parts.join("\n\n"));
    },
  },

  armorpieces_skin_paint: {
    description:
      "Paint one skin sheet by stamping rows of characters, in one undo step. `.` clears a texel, " +
      "`0`-`9` and `a`-`f` paint that grey, and a SPACE leaves the texel alone - so a stamp over " +
      "one net does not disturb the sheet around it. Place it either with `at` [x, y] or, better, " +
      "with `region` and `face`, which puts row 0 column 0 on that face's top-left texel and " +
      "refuses rows that would run off it. The value is a position on the material's ramp, not a " +
      "colour: `0` is the material's deepest shadow and `f` its brightest highlight, and a master " +
      "that only uses the middle comes out flat on every material. The reply ends with the check.\n" +
      "Paint a whole sheet in ONE call with `stamps`: a list of {region, face, rows}, or {region, " +
      "face, fill} for a flat field, or both together - the rows land over the fill, so a base and " +
      "its detail are one stamp and the whole skin is two or three calls. A call per face is how " +
      "a session spends its turns on nothing.",
    inputSchema: {
      type: "object",
      properties: {
        sheet: { type: "string", default: "humanoid", description: "`humanoid` or `humanoid_leggings`." },
        rows: { type: "array", items: { type: "string" }, description: "One string per texel row." },
        region: { type: "string", description: "helmet, helmet_raised, chest, arm, boot, waist or leg." },
        face: { type: "string", description: "front, back, right, left, top or bottom - the wearer's own." },
        fill: { type: "string", description: "One character: paint the whole face this level first." },
        at: {
          type: "array", minItems: 2, maxItems: 2, items: { type: "integer" },
          description: "Sheet texel the first character lands on. Ignored when region/face is given.",
        },
        stamps: {
          type: "array",
          description: "Many stamps in one call and one undo step - this is how a skin is painted. " +
            "Each is {region, face, rows} or {region, face, fill} or both; they are applied in order, " +
            "so a later stamp draws over an earlier one.",
          items: {
            type: "object",
            properties: {
              sheet: { type: "string", description: "`humanoid` or `humanoid_leggings`." },
              region: { type: "string" },
              face: { type: "string" },
              rows: { type: "array", items: { type: "string" } },
              fill: { type: "string" },
              shade_only: {
                type: "boolean",
                description: "Change values but never the silhouette: paint aimed at a clear " +
                  "texel is dropped. On by default for a skin pinned to a vanilla silhouette.",
              },
              tile: {
                type: "array", items: { type: "string" },
                description: "A small pattern repeated over the whole face - a weave, a quilt, " +
                  "a scale course. With `shift`, each row starts n texels further along, which " +
                  "is a brick bond.",
              },
              shift: { type: "integer", description: "Texels to offset each successive row of the tile." },
              at: { type: "array", minItems: 2, maxItems: 2, items: { type: "integer" } },
            },
            additionalProperties: false,
          },
        },
      },
      additionalProperties: false,
    },
    async execute({ sheet, rows, region, face, at, fill, stamps }) {
      const table = await skinRegions();
      // A pinned skin is drawn on vanilla's own outline (skin_sheets.py --seed), so every stamp
      // shades by default and the silhouette cannot be lost to a stray rectangle.
      const open = readMeta();
      const pinned = !!open?.skin && existsSync(join(ROOT, "tools", "skin_masters", open.skin, "silhouette"));
      const list = stamps?.length ? stamps : [{ sheet, rows, region, face, at, fill }];
      const jobs = [];
      const drawn = [];
      for (let i = 0; i < list.length; i++) {
        const stamp = list[i];
        const sheetId = stamp.sheet ?? sheet ?? "humanoid";
        const label = stamp.region ? `${stamp.region}.${stamp.face}` : `stamp ${i}`;
        let origin = stamp.at ?? [0, 0];
        let rect = null;
        if (stamp.region) {
          const net = table[stamp.region];
          if (!net) return reply(`${label}: no net "${stamp.region}"; the sheets carry ${Object.keys(table).join(", ")}`, true);
          if (net.sheet !== sheetId) return reply(`${label}: ${stamp.region} is on ${net.sheet}, not ${sheetId}`, true);
          rect = net.faces[stamp.face];
          if (!rect) return reply(`${label}: no face "${stamp.face}" on ${stamp.region}; one of ${Object.keys(net.faces).join(", ")}`, true);
          origin = [rect[0], rect[1]];
        }
        const shade = stamp.shade_only ?? pinned;
        const flat = stamp.fill === undefined || stamp.fill === null || stamp.fill === "" ? null : String(stamp.fill);
        if (flat !== null) {
          if (!rect) return reply(`${label}: fill needs region and face - it covers exactly one face`, true);
          if (flat.length !== 1) return reply(`${label}: fill is one character, not "${flat}"`, true);
          jobs.push({ sheet: sheetId, at: origin, where: `${label} fill`, shade_only: shade,
            rows: Array.from({ length: rect[3] }, () => flat.repeat(rect[2])) });
        }
        const tile = (stamp.tile ?? []).filter((r) => r.length);
        if (tile.length) {
          if (!rect) return reply(`${label}: tile needs region and face - it covers exactly one face`, true);
          const shift = stamp.shift ?? 0;
          const mod = (a, n) => ((a % n) + n) % n;
          jobs.push({ sheet: sheetId, at: origin, where: `${label} tile`,
            shade_only: shade,
            rows: Array.from({ length: rect[3] }, (_, y) => {
              const line = tile[mod(y, tile.length)];
              return Array.from({ length: rect[2] }, (_, x) => line[mod(x - shift * y, line.length)]).join("");
            }) });
        }
        const stampRows = stamp.rows ?? [];
        if (stampRows.length) {
          if (rect && (stampRows.length > rect[3] || stampRows.some((r) => r.length > rect[2]))) {
            return reply(
              `${label}: ${stampRows.length}x${Math.max(...stampRows.map((r) => r.length))} does not fit ` +
              `${stamp.region}.${stamp.face}, which is ${rect[2]}x${rect[3]} at ${rect[0]},${rect[1]}`, true);
          }
          jobs.push({ sheet: sheetId, at: origin, where: label, rows: stampRows, shade_only: shade });
        } else if (flat === null && !tile.length) {
          return reply(`${label}: nothing to paint - give rows, fill or tile`, true);
        }
        drawn.push(label);
      }
      const seqBefore = readMeta()?.seq;
      const out = await evalIn(`window.armorpieces_api.paintSkinMany(${JSON.stringify(jobs)})`);
      const listed = drawn.slice(0, 12).join(", ") + (drawn.length > 12 ? `, +${drawn.length - 12} more` : "");
      return await withCheck("armorpieces_skin_paint", seqBefore,
        reply(`Painted ${out.texels} texel(s) on ${out.sheets.join(" + ")} in ${drawn.length} stamp(s): ` +
          `${listed}.${out.skipped ? ` ${out.skipped} landed off the silhouette and were dropped ` +
            `(this skin is pinned to vanilla's outline).` : ""}`));
    },
  },

  armorpieces_skin_material: {
    description:
      "Show the open skin as one armor material would render it, or go back to the greyscale it is " +
      "authored in. The colours are that material's own, taken out of its vanilla texture by " +
      "tools/bake_skin.py - so this is the bake, in the viewport. The brush and the painter always " +
      "land on the greyscale master either way. Look at a skin on at least iron, gold and " +
      "netherite before saving it: they are the light, the saturated and the dark end of the range." +
      "\n\nThe bake is not the ramp alone. Vanilla's own texture for the material - its panel " +
      "edges, the rim on a plate, the shadow under an overhang - is added to each texel's VALUE " +
      "before the ramp is read, and between two texels side by side it can put five of the sixteen " +
      "levels a skin is drawn in. `view: \"light\"` shows that offset on its own, mid grey where " +
      "it changes nothing, so the shape a drawing is going into can be looked at; `light` moves " +
      "the mix, 0.35 being what the game does and 0 the pattern alone. check_skin.py counts how " +
      "many of the drawn steps it actually overrules.",
    inputSchema: {
      type: "object",
      properties: {
        material: {
          type: "string",
          description: "iron, gold, diamond, netherite, copper, chainmail, turtle_scute, leather, " +
            "or `none` for the greyscale master.",
        },
        view: {
          type: "string",
          enum: ["material", "light"],
          description: "`material` (default) bakes the skin as the game does; `light` shows " +
            "vanilla's own lighting for that material on its own, with the skin's alpha.",
        },
        light: {
          type: "number",
          minimum: 0,
          maximum: 1,
          description: "How much of vanilla's lighting is mixed in. Default 0.35, which is what " +
            "the game does; 0 is the pattern with none of it.",
        },
      },
      required: ["material"],
      additionalProperties: false,
    },
    async execute({ material, view, light }) {
      const options = JSON.stringify({ view: view ?? null, light: light ?? null });
      const out = await evalIn(
        `(function () { var api = window.armorpieces_api;` +
        ` var r = api.setSkinMaterial(${JSON.stringify(material)}, ${options}); api.publishSkin(); return r; })()`,
      );
      const text = !out.material ? "Showing the greyscale master."
        : out.view === "light"
          ? `Showing vanilla's own lighting for ${out.material} at a mix of ${out.light} - mid grey adds nothing.`
          : `Showing the skin on ${out.material}, vanilla's light mixed at ${out.light}.`;
      // The point of switching material is to LOOK at it, so the picture comes back with the
      // switch rather than costing a second round trip.
      try {
        const shot = await callUpstream("capture_screenshot", {});
        return { content: [{ type: "text", text }, ...(shot?.content ?? [])] };
      } catch (e) {
        return reply(`${text} capture_screenshot to look at it (${e.message}).`);
      }
    },
  },

  armorpieces_skin_check: {
    description:
      "The full check of the open skin, as tools/check_skin.py prints it: coverage face by face, " +
      "the value range and how many of the eight ramp shades it reaches, then the problems and " +
      "notes. Lines marked ! need a decision before saving.",
    inputSchema: {
      type: "object",
      properties: { brief: { type: "boolean", default: false, description: "Only the compact block." } },
      additionalProperties: false,
    },
    async execute({ brief }) {
      const meta = readMeta();
      if (!meta || meta.kind !== "skin") {
        return reply("No skin is open in the Armor Pieces plugin. armorpieces_open_skin one first.", true);
      }
      return reply(await checkText(meta, !brief));
    },
  },

  armorpieces_save_skin: {
    description:
      "Write both sheets back to tools/skin_masters/<skin> and install the pair into the mod's " +
      "resources with sync_skin_masters.py, whose report is returned. The template's icon needs " +
      "nothing: the game draws it from the sheet. Refused while the check reports problems, " +
      "unless `force` is true - say why each is acceptable in that case.",
    inputSchema: {
      type: "object",
      properties: { force: { type: "boolean", default: false, description: "Save despite problems." } },
      additionalProperties: false,
    },
    async execute({ force }) {
      const meta = readMeta();
      if (!meta || meta.kind !== "skin") return reply("No skin is open in the Armor Pieces plugin.", true);
      const report = await runCheck(meta);
      if (typeof report !== "string" && !report.ok && !force) {
        return reply(
          `Not saved: ${report.problems.length} problem(s) need a decision first.\n${report.text}\n` +
          `Fix them, or call again with force: true and say why each is acceptable.`,
          true,
        );
      }
      const out = await evalIn("window.armorpieces_api.saveSkin()");
      const lines = [`Saved skin ${out.skin}: ${out.wrote.join(", ")}.`];
      if (out.report) lines.push(out.report);
      if (typeof report === "string") lines.push(report);
      else if (!report.ok) lines.push(`Saved with problems standing:\n${report.text}`);
      return reply(lines.join("\n"));
    },
  },

  armorpieces_close_skin: {
    description: "Close the open skin's tab. Refused with unsaved edits unless `discard` is true.",
    inputSchema: {
      type: "object",
      properties: { discard: { type: "boolean", default: false } },
      additionalProperties: false,
    },
    async execute({ discard }) {
      const out = await evalIn(`window.armorpieces_api.closeSkin(${!!discard})`);
      return reply(JSON.stringify(out));
    },
  },
};

// --- the tool list ---------------------------------------------------------------------------------

/**
 * Blockbench's own manifest, from GET /tools. Every entry carries `mechanism`, which is what the
 * check-after-an-edit selects on - so the hand-kept READ_ONLY list is now only the fallback for a
 * name the cached manifest does not carry.
 */
async function upstreamTools() {
  try {
    const res = await fetch(`${await upstream()}/tools`, { signal: AbortSignal.timeout(5000) });
    const tools = await res.json();
    if (!Array.isArray(tools)) throw new Error(`HTTP ${res.status}`);
    mkdirSync(TEMP, { recursive: true });
    writeFileSync(CACHE, JSON.stringify({ tools }), "utf8");
    return { tools, source: "Blockbench" };
  } catch (e) {
    for (const file of [CACHE, SNAPSHOT]) {
      const cached = readJson(file);
      if (cached?.tools) return { tools: cached.tools, source: file };
    }
    return { tools: [], source: `nothing (${e.message})` };
  }
}

function visible(tool) {
  const allowed = PROFILES[PROFILE];
  return allowed ? allowed.has(tool.name) : true;
}

/** Our own tools are all served unless the profile names a subset (`kit`, `kit_skin`). */
function ownVisible(name) {
  const allowed = OWN_PROFILES[PROFILE];
  return allowed ? allowed.has(name) : true;
}

function annotate(tool) {
  const note = NOTES[tool.name];
  if (!note) return tool;
  return { ...tool, description: `${tool.description ?? ""}${note}` };
}

const { tools: upstreamList, source } = await upstreamTools();
const ownNames = Object.keys(OWN).filter(ownVisible);
const served = [
  ...upstreamList.filter(visible).map(annotate),
  ...ownNames.map((name) => ({ name, description: OWN[name].description, inputSchema: OWN[name].inputSchema })),
];
const upstreamNames = new Set(upstreamList.map((t) => t.name));
// The manifest's own stamp first, the hand-kept list only for a name it does not carry (an old
// cached manifest, or the snapshot beside this file).
const observes = (name) => {
  const stamp = upstreamList.find((t) => t.name === name)?.mechanism;
  return stamp ? stamp === "observe" : READ_ONLY.has(name);
};
log(`profile ${PROFILE}: ${served.length} tools (${upstreamList.filter(visible).length} of ${upstreamList.length} from ${source}, ${ownNames.length} of ${Object.keys(OWN).length} own)`);
// THIS session's OWN id, said once by the process that computes it. The A/B's identity column is
// its falsifier, and until 2026-09-08 it had no evidence: `measure_sessions.py` read ids out of
// reply TEXT, where the only id that ever appears is the one a `held_by` refusal names - which is
// by definition somebody else's (mcp-toolkit CHANGELOG 0.140.0). A line on this server's own
// stderr cannot be another session's, because nothing but this process writes it.
log(`session ${SESSION.id} (client ${SESSION.client}, ppid ${process.ppid})`);

// --- the server ------------------------------------------------------------------------------------

const server = new Server(
  { name: "armorpieces-blockbench", version: "0.1.0" },
  // `full` is a script profile and a script does not read instructions; the part paragraph is the
  // honest default for it.
  { capabilities: { tools: {} }, instructions: PROFILE === "kit_skin" ? KIT_SKIN_INSTRUCTIONS : KIT_INSTRUCTIONS },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: served }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args = {} } = request.params;
  try {
    if (OWN[name]) {
      if (!ownVisible(name)) {
        return reply(`${name} is not in the ${PROFILE} profile of the Armor Pieces bridge (ARMORPIECES_BB_PROFILE=full serves the piece and skin tools together).`, true);
      }
      return await OWN[name].execute(args);
    }
    if (!upstreamNames.has(name) && upstreamList.length) {
      return reply(`Unknown tool ${name}.`, true);
    }
    if (!visible({ name })) {
      return reply(`${name} is not in the ${PROFILE} profile of the Armor Pieces bridge (ARMORPIECES_BB_PROFILE=full serves everything).`, true);
    }
    const seqBefore = readMeta()?.seq;
    const result = await callUpstream(name, args);
    if (observes(name)) return result;
    return await withCheck(name, seqBefore, result);
  } catch (e) {
    return reply(e?.message ?? String(e), true);
  }
});

await server.connect(new StdioServerTransport());
