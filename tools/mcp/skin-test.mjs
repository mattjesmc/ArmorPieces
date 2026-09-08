// Save round-trip: paint one net, force the save, prove the PNG on disk changed, blank it again.
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { readFileSync } from "node:fs";

const SERVER = "C:/Users/Matthijs/ArmorPieces/tools/mcp/server.mjs";
const MASTER = "C:/Users/Matthijs/ArmorPieces/tools/skin_masters/plate/humanoid.png";

const client = new Client({ name: "skin-test", version: "0.1.0" });
// The skin tools live in `kit_skin`. This used to work without saying so, because the default
// profile was `authoring` and served everything; the default is `kit` now (part tools only).
await client.connect(new StdioClientTransport({
  command: process.execPath, args: [SERVER],
  env: { ...process.env, ARMORPIECES_BB_PROFILE: "kit_skin" },
}));
const say = (label, result) => {
  const text = (result.content ?? []).map((c) => c.text).join("\n");
  console.log(`\n=== ${label}${result.isError ? " (ERROR)" : ""} ===\n${text.split("\n").slice(0, 6).join("\n")}`);
};

const before = readFileSync(MASTER).length;
say("open", await client.callTool({ name: "armorpieces_open_skin", arguments: { skin: "plate" } }));
say("paint", await client.callTool({
  name: "armorpieces_skin_paint",
  arguments: { sheet: "humanoid", region: "boot", face: "front", rows: ["3333", "5555"], },
}));
say("save forced", await client.callTool({ name: "armorpieces_save_skin", arguments: { force: true } }));
const after = readFileSync(MASTER).length;
console.log(`\nmaster on disk: ${before} -> ${after} bytes`);

say("blank again", await client.callTool({
  name: "armorpieces_skin_paint",
  arguments: { sheet: "humanoid", region: "boot", face: "front", rows: ["....", "...."] },
}));
say("save blank", await client.callTool({ name: "armorpieces_save_skin", arguments: { force: true } }));
say("close", await client.callTool({ name: "armorpieces_close_skin", arguments: {} }));

await client.close();
process.exit(0);
