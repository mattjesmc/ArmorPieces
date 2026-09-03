#!/usr/bin/env node
// The Armor Pieces bridge: an MCP server that stands in front of the Blockbench MCP Server plugin.
//
// The plugin (jasonjgardner/blockbench-mcp-plugin) runs inside Blockbench and speaks MCP over HTTP.
// It has no way for another plugin to add tools, so everything Armor Pieces wants an agent to have
// is added here, one hop out, by a stdio server that is the agent's only view of Blockbench:
//
//   - a PROFILE: the tools a part author uses, out of the ninety-odd the plugin registers
//     (profile.mjs). Tool names are unchanged, so `mcp__blockbench__place_cube` is still that.
//   - a CHECK after every editing call: the Armor Pieces plugin publishes the open piece after
//     each edit (tools/blockbench_plugin, "status for the bridge"), and this runs
//     tools/check_part.py over it and appends the compact report to the reply - so a face that
//     landed on the helmet shell is reported by the call that put it there.
//   - the armorpieces_* tools: open, new, check, save, part, set_part, pieces, close. Each is a
//     risky_eval into the plugin's `armorpieces_api` with the bridge's traps handled here.
//
// Configuration, all optional:
//   ARMORPIECES_BB_URL      the plugin's endpoint      (http://localhost:3000/bb-mcp)
//   ARMORPIECES_BB_PROFILE  authoring | full           (authoring)
//   ARMORPIECES_PYTHON      the interpreter for tools/ (python)
//
// Blockbench need not be running when this starts: the tool list then comes from the last live
// manifest (cached in the temp dir) or the snapshot beside this file, and the connection is made on
// the first call. A session the plugin timed out is reconnected once, transparently.

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { execFile } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { INSTRUCTIONS, NOTES, PROFILES, READ_ONLY } from "./profile.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..", "..");
const UPSTREAM = process.env.ARMORPIECES_BB_URL || "http://localhost:3000/bb-mcp";
const PYTHON = process.env.ARMORPIECES_PYTHON || "python";
const PROFILE = (process.env.ARMORPIECES_BB_PROFILE || "authoring").trim();
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

let client = null;

async function upstream() {
  if (client) return client;
  const c = new Client({ name: "armorpieces-bridge", version: "0.1.0" });
  const transport = new StreamableHTTPClientTransport(new URL(UPSTREAM));
  try {
    await c.connect(transport);
  } catch (e) {
    throw new Error(
      `Blockbench is not answering at ${UPSTREAM} (${e.message}). Start Blockbench with the MCP ` +
      `Server plugin and the Armor Pieces plugin loaded, then call again.`,
    );
  }
  c.onclose = () => { if (client === c) client = null; };
  c.onerror = (e) => log(`upstream: ${e?.message ?? e}`);
  client = c;
  return c;
}

async function callUpstream(name, args) {
  const attempt = async () => (await upstream()).callTool({ name, arguments: args ?? {} });
  try {
    return await attempt();
  } catch (e) {
    // The plugin drops a session after its inactivity timeout; a fresh connection is the fix.
    if (/session|not found|closed|ECONN|fetch failed|404|400/i.test(String(e?.message))) {
      log(`reconnecting after: ${e.message}`);
      client = null;
      return await attempt();
    }
    throw e;
  }
}

function textOf(result) {
  return (result?.content ?? []).filter((c) => c.type === "text").map((c) => c.text).join("\n");
}

/**
 * Run JavaScript inside Blockbench through the plugin's risky_eval, and hand back the value. The
 * plugin returns `JSON.stringify(result)` as text, "Error executing code: ..." on a throw, and
 * refuses to run at all with no project open ("reading 'finishEdit'"): that last case is met by
 * opening a scratch project and trying again.
 */
async function evalIn(code, { retryWithProject = true } = {}) {
  const result = await callUpstream("risky_eval", { code });
  const text = textOf(result);
  if (result?.isError || /^Error executing code:/.test(text)) {
    if (retryWithProject && /finishEdit/.test(text)) {
      await callUpstream("create_project", { name: SCRATCH, format: "free" });
      return evalIn(code, { retryWithProject: false });
    }
    throw new Error(text.replace(/^Error executing code:\s*/, ""));
  }
  if (/^\(Code executed successfully/.test(text)) return undefined;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

/** Close the scratch project a piece was opened from, once the piece tab is up. Best effort. */
async function dropScratch() {
  try {
    await evalIn(
      `(function () { var s = ModelProject.all.find(function (p) { return p.name === '${SCRATCH}'; });` +
      ` if (s && s !== Project) setTimeout(function () { s.close(true); }, 100); return !!s; })()`,
      { retryWithProject: false },
    );
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

/** check_part.py over the active piece: the report as data, or a string when it could not run. */
async function runCheck(meta) {
  const args = [join(ROOT, "tools", "check_part.py"), "--status", meta.dir, "--json", "--brief"];
  const { stdout, stderr } = await run(args);
  const line = stdout.trim().split("\n").pop() ?? "";
  try {
    return JSON.parse(line);
  } catch {
    return `[armorpieces] the check could not run: ${(stderr || stdout).trim().split("\n").pop()}`;
  }
}

function header(meta) {
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
  while (Date.now() < until) {
    if (existsSync(join(meta.dir, "master.png"))) {
      await new Promise((r) => setTimeout(r, 120));
      return readMeta() ?? meta;
    }
    await new Promise((r) => setTimeout(r, 60));
  }
  return readMeta() ?? meta;
}

async function checkText(meta, full = false, withReferences = false) {
  const report = await runCheck(meta);
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

/**
 * The sheet layout as one line per cube, for the cubes whose net moved or appeared since the
 * last check the bridge ran - so a reply that added or resized a cube also says where its faces
 * now are, and a reply that painted says nothing about layout.
 */
let lastLayout = new Map();
let lastCoverage = new Map();

function layoutLines(report) {
  const seen = new Map();
  const coverage = new Map();
  const changed = [];
  const lost = [];
  for (const item of report.layout ?? []) {
    const key = `${item.uv.join(",")}|${item.size.join("x")}`;
    seen.set(item.cube, key);
    if (lastLayout.get(item.cube) !== key) changed.push(item);
    for (const [face, [got, area]] of Object.entries(item.coverage ?? {})) {
      const name = `${item.cube}.${face}`;
      coverage.set(name, got === area);
      // A face that was complete and no longer is: the resize grew it, and paint only moves.
      if (lastCoverage.get(name) === true && got < area) lost.push(`${name} ${got}/${area}`);
    }
  }
  lastLayout = seen;
  lastCoverage = coverage;
  const lines = [];
  if (changed.length) {
    lines.push("  sheet layout (face x,y w x h): " + (changed.length === seen.size ? "every cube" : "the cubes that moved"));
    for (const item of changed) {
      const faces = Object.entries(item.faces).map(([f, [x, y, w, h]]) => `${f} ${x},${y} ${w}x${h}`).join("  ");
      lines.push(`    ${item.cube} uv ${item.uv.join(",")} ${item.size.join("x")}: ${faces}`);
    }
  }
  if (lost.length) lines.push(`  ! repaint: faces that were complete and grew: ${lost.join(", ")}`);
  return lines;
}

/** Append the check to an editing call's reply when the call changed the piece. */
async function withCheck(name, seqBefore, result) {
  if (name === "undo" || name === "redo") await new Promise((r) => setTimeout(r, 350));
  const meta = readMeta();
  if (!meta || meta.seq === seqBefore) return result;
  const report = await runCheck(meta);
  const text = typeof report === "string" ? report : [report.text, ...layoutLines(report)].join("\n");
  return { ...result, content: [...(result.content ?? []), { type: "text", text }] };
}

const reply = (text, isError = false) => ({ content: [{ type: "text", text }], isError });

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
      const opts = JSON.stringify({ discard: !!discard, reload: !!reload });
      const out = await evalIn(
        `window.armorpieces_api.openFor(${JSON.stringify(piece)}, ${JSON.stringify(anchor ?? null)}, ${opts})`,
      );
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
      const out = await evalIn(
        `(function () { var api = window.armorpieces_api; var packs = api.packs(); var dp = ${JSON.stringify(datapack ?? null)} || packs[0];` +
        ` var rp = ${JSON.stringify(resourcepack ?? null)} || dp; if (!dp) throw new Error('no pack folder to put the piece in');` +
        ` var root = Settings.get('armorpieces_root'); var ns = ${JSON.stringify(namespace ?? null)} || ((root && dp.indexOf(root) === 0) ? 'armorpieces' : 'mypack');` +
        ` return api.create(dp, rp, ns, ${JSON.stringify(name)}, ${JSON.stringify(anchor)}); })()`,
      );
      await dropScratch();
      let meta = readMeta();
      if (meta) meta = await settled(meta);
      const check = meta ? await checkText(meta, false, true) : "";
      return reply(`${JSON.stringify(out, null, 1)}\n${check}`);
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
      return reply(JSON.stringify(out));
    },
  },
};

// --- the tool list ---------------------------------------------------------------------------------

async function upstreamTools() {
  try {
    const { tools } = await (await upstream()).listTools();
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

function annotate(tool) {
  const note = NOTES[tool.name];
  if (!note) return tool;
  return { ...tool, description: `${tool.description ?? ""}${note}` };
}

const { tools: upstreamList, source } = await upstreamTools();
const served = [
  ...upstreamList.filter(visible).map(annotate),
  ...Object.entries(OWN).map(([name, t]) => ({ name, description: t.description, inputSchema: t.inputSchema })),
];
const upstreamNames = new Set(upstreamList.map((t) => t.name));
log(`profile ${PROFILE}: ${served.length} tools (${upstreamList.filter(visible).length} of ${upstreamList.length} from ${source}, ${Object.keys(OWN).length} own)`);

// --- the server ------------------------------------------------------------------------------------

const server = new Server(
  { name: "armorpieces-blockbench", version: "0.1.0" },
  { capabilities: { tools: {} }, instructions: INSTRUCTIONS },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: served }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args = {} } = request.params;
  try {
    if (OWN[name]) return await OWN[name].execute(args);
    if (!upstreamNames.has(name) && upstreamList.length) {
      return reply(`Unknown tool ${name}.`, true);
    }
    if (!visible({ name })) {
      return reply(`${name} is not in the ${PROFILE} profile of the Armor Pieces bridge (ARMORPIECES_BB_PROFILE=full serves everything).`, true);
    }
    const seqBefore = readMeta()?.seq;
    const result = await callUpstream(name, args);
    if (READ_ONLY.has(name)) return result;
    return await withCheck(name, seqBefore, result);
  } catch (e) {
    return reply(e?.message ?? String(e), true);
  }
});

await server.connect(new StdioServerTransport());
