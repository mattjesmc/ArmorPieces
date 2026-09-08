// List what an MCP stdio server serves, with per-tool manifest cost.
// usage: node _probe-list.mjs <command> [args...]   (env passed through)
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const [cmd, ...args] = process.argv.slice(2);
const t = new StdioClientTransport({ command: cmd, args, env: process.env, stderr: "inherit" });
const c = new Client({ name: "probe", version: "0" });
await c.connect(t);
const { tools } = await c.listTools();
const instr = c.getInstructions?.() ?? "";
const tok = (x) => Math.round(x.length / 4);
const cost = (x) => tok((x.description ?? "") + JSON.stringify(x.inputSchema ?? {}));
const total = tools.reduce((n, x) => n + cost(x), 0);
if (process.env.PER_TOOL) {
  for (const x of [...tools].sort((a, b) => cost(b) - cost(a))) console.log(`  ${String(cost(x)).padStart(5)}  ${x.name}`);
}
console.log(`TOOLS ${tools.length}: ${tools.map((x) => x.name).join(", ")}`);
console.log(`INSTRUCTIONS ~${tok(instr)} tok`);
console.log(`MANIFEST ~${total} tok`);
console.log(`PREFIX ~${total + tok(instr)} tok`);
await c.close();
process.exit(0);
