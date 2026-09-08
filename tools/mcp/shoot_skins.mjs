/**
 * Screenshot finished skins on chosen materials, for a human to look at side by side.
 *
 * The bridge is the only thing that can pose the figure and bake it to a material, and a person
 * comparing eight skins wants them in one place rather than eight tabs. Images come back through the
 * proxy, so they arrive cropped and shrunk like any other look.
 *
 *   node tools/mcp/shoot_skins.mjs <out dir> <skin,skin,...> <material,material,...> [--full]
 *
 * --full asks the proxy to leave the pictures at viewport size, which is what you want when the
 * shots are going into a contact sheet for a person rather than into a session's context.
 */
import { writeFileSync, mkdirSync } from "node:fs";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const args = process.argv.slice(2);
const full = args.includes("--full");
const [out, skinArg, materialArg] = args.filter((a) => a !== "--full");
if (!out || !skinArg || !materialArg) {
  console.error("usage: shoot_skins.mjs <out dir> <skins> <materials> [--full]");
  process.exit(2);
}
mkdirSync(out, { recursive: true });

const client = new Client({ name: "shoot-skins", version: "0.1.0" });
await client.connect(new StdioClientTransport({
  command: "node",
  args: [new URL("./server.mjs", import.meta.url).pathname.slice(1)],
  // `full`, and by its real name: this asked for "authoring" through MCP_PROFILE, which nothing
  // reads, and got the upstream tools from the old default instead. A script wants everything.
  env: { ...process.env, ARMORPIECES_BB_PROFILE: "full", ...(full ? { ARMORPIECES_SHOT_MAX: "0" } : {}) },
}));

const imageOf = (r) => {
  const part = (r.content ?? []).find((p) => p.type === "image");
  return part ? (part.data ?? part.source?.data) : null;
};

for (const skin of skinArg.split(",")) {
  // Not `reload` - that closes the tab and rebuilds it on a timer, and a capture taken while the
  // rig is re-attaching shows the vanilla-textured figure instead of the skin.
  await client.callTool({ name: "armorpieces_open_skin", arguments: { skin } });
  await client.callTool({
    name: "set_camera_angle",
    arguments: { position: [0, 24, -44], target: [0, 16, 0], projection: "perspective" },
  });
  for (const material of materialArg.split(",")) {
    const r = await client.callTool({ name: "armorpieces_skin_material", arguments: { material } });
    const data = imageOf(r) ?? imageOf(await client.callTool({ name: "capture_screenshot", arguments: {} }));
    if (data) writeFileSync(`${out}/${skin}_${material}.png`, Buffer.from(data, "base64"));
    else console.log(`${skin} ${material}: no image came back`);
  }
  console.log(`${skin} done`);
}
await client.close();
process.exit(0);
