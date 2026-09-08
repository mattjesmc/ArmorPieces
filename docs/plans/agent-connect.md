# Investigation: "Connect to agent" — an MCP surface for the web editor

**Status: PAUSED, low priority (2026-09-08). Investigation only — nothing built, nothing decided.**
Parked deliberately, not blocked: section 8's stage 1 (the consumer tool table) is the cheapest way
back in if it is ever picked up, and section 10's five questions are still unanswered. The external
facts below have expiry dates — the WebMCP origin trial, the Chrome milestones and the connector
dialogs will all have moved on by the time this is read again, so re-check section 2's table and
section 3's status before acting on either. The question asked was:
can the Blockbench MCP plugin the toolkit built (`mcptoolkit_bridge.js`,
`mcp-toolkit/docs/models/BLOCKBENCH_BRIDGE_DESIGN.md`) get a *web* version, so that
`armorpieces.com/editor/` grows a **Connect to agent** button — the browser hands the session to
Claude, ChatGPT or Copilot, and a player who has never seen a terminal gets the same agent authoring
we use headlessly.

The short answer: **yes, and the desktop half is already 90% of the way there — but not by the route
in the question.** A browser cannot be handed to a program the way the question imagines. What it
can do is three other things, and one of them is close enough that the button reads exactly as
described.

---

## 1. The wall, stated once

The desktop bridge works because a Blockbench plugin can **listen**. It asks Blockbench 5's sandbox
for the `process` grant, pulls `process.getBuiltinModule('http')`, and serves
`127.0.0.1:25801`. The shim dials it. Everything — sessions, `held_by`, the manifest, the reply
envelope — hangs off that one fact.

**A browser tab cannot listen.** There is no port, no `http` module, no address an outside program
can reach. Every design below is a way of inverting that: the tab **dials out**, and something else
holds the door open.

That single inversion is the whole engineering cost, and it is smaller than it sounds, because the
toolkit's plugin already separates the door from the room. `call(name, args, sessionBlock)` is at
line 1985 of 2293; everything Node-shaped is the http server after it; and the file already ends by
publishing

```js
globalThis.mcptoolkitBridge = { start, stop, status, manifest, call, settings, sessions };
```

which the design records as being there "so the harness and an eval can drive the tool layer without
the transport" (section 10). The seam we need already exists and is already tested through — the
2,293-line plugin's 116-check harness drives `call` directly, not the socket. Everything else in it
is browser-safe already: settings in `localStorage`, files through `Blockbench.read` /
`Blockbench.writeFile`, pictures off the Three.js canvas.

And our own nine tools cost nothing at all. `tools/mcp/server.mjs` is a stdio MCP server whose every
tool is a `risky_eval` string into `window.armorpieces_api` — `open`, `openFor`, `save`, `paintFaces`,
`close`, `packs`, `library`. In the web build **that object is simply there**, on the page, no eval
and no bridge: `ArmorPiecesBlockbench/src/start.js` already calls fourteen of its methods to draw the
start screen, and the site already calls `armorpieces_api.preview` for the coloured thumbnails. A web
MCP surface over the nine is a function table, not a port.

---

## 2. Route A — the hosted relay, and a capability URL

The one that matches the button in the question.

```
  the tab                         armorpieces.com                    the agent app
  ────────                        ───────────────                    ─────────────
  [Connect to agent]  ──wss──▶  /agent/socket  ◀──── relay ────▶  POST /agent/s/<token>/mcp
  window.armorpieces_api                                            (Streamable HTTP MCP)
  window.mcptoolkitBridge.call
```

1. The tab clicks Connect. It opens a WebSocket to its **own origin** — same host, same port as the
   page, so no CORS, no mixed content, no Local Network Access prompt, and `connect-src 'self'`
   already allows it (see section 6).
2. The relay mints a session and hands back a **capability URL**:
   `https://armorpieces.com/agent/s/<token>/mcp`.
3. The tab shows that URL, a copy button, and the per-client shortcuts that exist.
4. The agent app connects to it as an ordinary remote MCP server. `tools/list` and `tools/call` go
   down the socket to the tab; the tab runs them against `armorpieces_api` (and Pyodide, which is
   where `check_part.py` already runs); results — including `_image` screenshots, which become MCP
   image content exactly as the shim already does it — go back up.
5. Closing the tab kills the session. There is nothing left running anywhere.

### What the button can actually *do* per client, today

This is the part of the question that does not survive contact. There is no cross-vendor
"open my agent and load this MCP server" handshake; there are two proprietary deep links, and
otherwise a URL you paste.

| Client | Takes a remote MCP URL? | One click from a web page? |
| --- | --- | --- |
| **VS Code / Copilot** | yes, `{"type":"http","url":…}` | **yes** — `vscode:mcp/install?` + `encodeURIComponent(JSON.stringify(cfg))` (also `vscode-insiders:`) |
| **Cursor** | yes | **yes** — `cursor://anysphere.cursor-deeplink/mcp/install?name=…&config=<base64>` |
| **Claude Desktop / claude.ai** | yes — *Customize → Connectors → Add custom connector*; **Authentication: None** is a supported choice, and request headers exist in beta | **no install link.** `claude://claude.ai/new?q=…` opens a prefilled chat and nothing more |
| **Claude Code** | yes — `claude mcp add --transport http armorpieces <url>` | a copyable command; `claude://code/new?q=…&folder=…` opens a session |
| **ChatGPT** | yes — *Settings → Apps → Advanced → Developer mode → Add custom connector*; Plus/Pro/Business+ | **no** |

So the honest UX is: **two one-click buttons, three "copy this URL and paste it once" cards, and a
30-second animation showing where.** After the first time, the connector is saved in the client and
the *only* thing that changes per session is the token — which is the part that hurts, and section 5
is what to do about it.

Claude's plan gate is worth checking before promising anything: the current connectors documentation
lists **Free, Pro and Max** as able to add custom connectors, while the older help-centre article
says Pro and up. That difference is exactly the "commoners" question, so confirm it on a free
account before the button ships.

**Cost.** A relay service on the VPS (`/opt/armorpieces`, already Compose behind Caddy), an
`upgrade` handler on `ArmorPiecesSite/server.mjs` (already a bare `node:http` server — line 102), a
Streamable HTTP MCP endpoint, a session table, and the tab-side executor. Call it the size of the
overlay pass, not the size of the website.

---

## 3. Route B — WebMCP, where there is no URL at all

The thing that did not exist when the desktop bridge was designed, and the closest anyone has come
to the button as imagined.

**WebMCP** is a W3C Web Machine Learning Community Group draft (latest report 4 September 2026, *not*
on the standards track) in which the *page itself* registers tools and the *browser's own agent*
calls them. No relay, no URL, no token, no connector setup — the user opens the editor in a browser
that has an agent, and the agent can already drive it.

```js
navigator.modelContext.registerTool({
  name: 'open_piece',
  description: 'Open one Armor Pieces piece for editing',
  inputSchema: { type: 'object', properties: { key: { type: 'string' } }, required: ['key'] },
  async execute({ key }) { return { content: [{ type: 'text', text: await api.open(key) }] }; },
});
```

Status, precisely, because it matters:

- Chrome **146** (February 2026) shipped it as an Early Preview behind `chrome://flags/#enable-webmcp-testing`.
- Chrome **149** opened an **origin trial** — which we can join, because we own `armorpieces.com`
  and serve our own headers. That is the only way to get it in front of a real player today.
- Chrome-only. Edge follows by engine; Firefox and Safari have committed to nothing.
- The entry point is **in flux**: Chrome ships `navigator.modelContext`, the September spec draft
  says `document.modelContext`. Feature-detect both, in that order, and never assume either.
- The consumer is the **browser's** agent — Gemini in Chrome, Claude for Chrome, the Model Context
  Tool Inspector extension. Claude Desktop and ChatGPT cannot reach it. The spec is explicit that
  external agents do not use the API directly; the browser exposes the tools "via Model Context
  Protocol, other proprietary function-calling methods, or any other way", implementation-defined.

**Two traps that are ours specifically.**

1. **The editor is in an iframe.** `/editor/` is a site page that frames `/editor/app/`
   (`server.mjs`, `editorApp()`; `frame-ancestors 'self'`). Tool registration from a nested document
   is the least-settled corner of the spec. Register from the **top** document and forward over
   `postMessage` into the frame — which is a boundary worth having anyway, because it is where the
   consumer tool surface gets narrowed (section 4).
2. It is an origin trial. It expires. It cannot be the only route.

**Verdict: build it, but as a second adapter over the same tool table as Route A, never as the
plan.** If the table is a plain array of `{name, description, inputSchema, execute}`, WebMCP is
perhaps eighty lines and the relay is the same eighty tools. If we build Route A first and bolt
WebMCP on later, we will have written the table twice.

---

## 4. The surface is the real design question, not the transport

The strongest finding of this investigation is not about transports at all.

**The authoring kit is the wrong surface for a player.** `.mcptoolkit/loop.json` is a keep-list of 18
Blockbench tools plus our nine, priced deliberately — "every name here is paid on EVERY turn of every
session in this workspace, and a part session is 40+ turns" — and tuned for a headless `part-author`
that opens a rig, places cubes on bones, paints greyscale masks against a trim ramp, and is judged by
`check_part.py`. That agent needs `place_cube`, `modify_cube`, `inspect faces`. It costs ~$0.78 a
skin and forty turns a part, and it took nine measured runs and a written-down rig-frame trap to make
it work at all.

A player who clicks **Connect to agent** does not want `place_cube`. They want *"make the crest on my
helmet gold"*, *"give me a piece like the kelp mantle but shorter"*, *"put this on the wardrobe"*.
Handing them the authoring kit gives them a tool list they will burn tokens on and an agent that
will make a mess of a piece and then fail the check.

So the web surface should be **its own small, task-shaped table** — six to ten tools, not
twenty-seven — over the same `armorpieces_api`:

- `list_pieces`, `open_piece`, `describe_piece` (the check, in prose)
- `recolour` / `set_material`
- `preview` (the picture — `armorpieces_api.preview`, which the site already uses)
- `save_to_library`, `add_to_outfit`
- and, gated behind an explicit *"let it model"* toggle, the geometry tools.

That table is also what makes Route B viable: WebMCP tool descriptions are read by a general-purpose
browser agent with no Armor Pieces briefing, and twenty-seven modelling primitives with a rig-frame
trap will not survive that. Ten task tools will.

**This decision is independent of every transport below it, and it should be made first.**

---

## 5. Route C — a local bridge, and why it is the fallback and not the plan

The browser dials `ws://127.0.0.1:<port>`, where a small local MCP server listens; the user installs
that server once, one click, as an `.mcpb` bundle dropped into Claude Desktop (the format is
`modelcontextprotocol/mcpb`, and Claude Desktop ships its own Node runtime, so there is nothing to
install underneath it).

Two hard facts:

- **Chrome's Local Network Access gate applies.** A public HTTPS origin reaching loopback now needs
  an explicit permission prompt: shipped in Chrome **142** for fetch, extended to **WebSockets and
  WebTransport in Chrome 147**. The permission is remembered per origin. This is not a blocker — it
  is arguably the "browser asks" moment from the question, made literal — but it is a prompt the
  user must understand, and on a denial there is no fallback.
- **Our own CSP blocks it.** `EDITOR_CSP` is `connect-src 'self' https://cdn.jsdelivr.net`. A
  loopback socket needs `ws://127.0.0.1:*` added explicitly, which widens the editor's CSP for a
  path most users will never take.

It requires an install, which is the exact thing the question wants to avoid. Keep it in the
back pocket for the person who will not point their editor at our server — and note that for *that*
person the desktop editor already exists and already works.

---

## 6. Site-side traps, already visible

- **`connect-src 'self'`** covers a same-origin `wss://` under CSP3, so Route A needs no CSP change.
  Routes B and C do. Do not widen `EDITOR_CSP` for a route we are not shipping.
- **The editor is framed.** Everything agent-facing belongs in the top document at `/editor/`, with
  `postMessage` into `/editor/app/`. Same boundary as the WebMCP one; build it once.
- **The site's server is a plain `node:http` server** (`ArmorPiecesSite/server.mjs:102`) — a
  `server.on('upgrade', …)` attaches directly. Astro is not in the way.
- **Caddy** is in front on the VPS and must be told to pass the upgrade through.
- **Auth.js is already there**, so a session can be bound to a signed-in account, which is what makes
  `save_to_library` and `add_to_outfit` meaningful rather than dangerous.
- **`repo.tar.gz` / Pyodide** means the tab is already carrying the Python. A relayed `describe_piece`
  runs the *real* `check_part.py`, not a JS restatement of it — the same principle the whole web
  editor was built on.

---

## 7. Security, said plainly

A capability URL is a bearer token in a URL. Whoever holds it drives someone's editor.

- **Short-lived to claim** (minutes), then bound to the first MCP session that uses it.
- **A pairing code shown in the tab** that the agent must echo back, so pasting a stale or wrong URL
  fails visibly instead of silently attaching to a stranger.
- **A persistent "an agent is connected" banner**, and a Disconnect that actually kills the socket.
- **Confirmation in the tab** for anything destructive — `save`, `close`, overwrite, publish. The
  agent proposes; the human clicks. This is also the honest answer to prompt injection: pack
  content, piece names and pack descriptions are third-party text, they will end up in the agent's
  context, and the only thing standing between that and a bad write is a human clicking.
- **Never expose a filesystem tool.** The desktop nine include `save` into a pack directory; on the
  web that is the virtual FS, which is fine, but `armorpieces_api.packs()` names real things and the
  library is real. Scope by account.
- **Rate-limit the relay** per session and per account; a runaway agent loop is a plausible incident.

---

## 8. Recommendation

Staged, cheapest-first, each stage useful on its own:

1. **Define the consumer tool table** (section 4) as a plain array in the web plugin, with
   `execute` over `window.armorpieces_api`. No transport. Ship it behind
   `window.armorpieces_tools` and drive it from the console. *This is the whole design; everything
   else is a socket.*
2. **Route B, WebMCP**, as an eighty-line adapter over that array, behind feature detection and a
   Chrome 149 origin-trial token. It is the only route with no server, no token and no paste, so it
   is the one that actually reaches "commoners" — for the subset of them on Chrome. Ship it as an
   experiment and measure whether anyone uses it.
3. **Route A, the relay**, once the table has proven itself. This is where Claude and ChatGPT come
   in, and it is the stage with real cost — a service, a session store, a security surface, and
   support load from five different paste-this-URL flows.
4. **Ask the toolkit for the transport split** (section 9) only if and when the modelling tools are
   wanted on the web. Stages 1–3 do not need them.

The thing to *not* do is start at stage 3 because it is the one that looks like the question.

---

## 9. What the toolkit would have to do, if we get that far

One ask, and it is small, and it is already half-done:

> **Split `mcptoolkit_bridge.js` into a tool half and a transport half, and let a build choose the
> transport.** `call()` at line 1985 and the published `mcptoolkitBridge` object at line 2275 are
> already the seam; the design already states the harness drives the tool layer without the
> transport; `localStorage`, `Blockbench.read`/`writeFile` and the canvas work are already
> browser-safe. What is Node is the http server and the `process.getBuiltinModule` grant around it.
> A `transport: 'ws-client'` build dials out instead of listening, and 90% of the file is untouched.

That is a better ask than "please make a web version", because it is the shape the file is already
in, and because it is the same seam the toolkit will need the day it wants a bridge over anything
that is not a loopback socket.

Note also the precedent on our side: `ArmorPiecesBlockbench/build/make_plugin.mjs` already builds the
web plugin from the desktop one with exactly three substitutions **and fails the build if any of them
stops matching**. A transport swap fits that machine.

---

## 10. Open questions — these are yours, not mine

1. **Who is this for?** A player who wants to recolour a piece, or an author who wants agent
   modelling without a terminal? The answer picks the tool table, and the two tables barely overlap.
2. **Does an agent get to write to the account** — library, wardrobe, packs — or only to the open
   tab? Writing is what makes it useful and what makes it dangerous.
3. **Do we pay for the relay's traffic?** It is small (JSON and the occasional PNG), but it is
   unbounded per session and an agent loop is a plausible bill.
4. **Is a Chrome-only feature acceptable as the headline?** If yes, stage 2 is most of the value for
   a fraction of the cost. If no, stage 3 is unavoidable and stage 2 is a curiosity.
5. **Support.** Five clients, three of which need a paste, and every one of them will produce a
   "connect to agent doesn't work" message. Who answers those?
