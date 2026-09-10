"""Speak to the mcp-toolkit bridge in the running game.

The bridge is a plain HTTP endpoint (`POST /cmd`, `GET /tools`) that the toolkit opens inside a dev
game, and it is the whole of the gate's tier 2 and tier 3: everything the mod does that needs a
server - loading a datapack, filling a chest, running a command, answering a tooltip - is asked
through it. The MCP shim beside it is for a session; a suite talks HTTP.

Three rules here are scars rather than style:

  * **Prove the build before believing a reply.** A second game cannot bind 25599 and answers from
    the older JVM, silently, so a run against a stale instance passes tests for code that is not
    loaded. `ping.build` names the jar the game is running; `Bridge.attach` refuses one older than
    the tree.
  * **Send from Python, never from a shell.** A Windows path inside a `curl -d` JSON literal breaks
    the shell's escaping in a way that looks like a bridge error.
  * **An argument name is checked.** A wrong one is refused rather than ignored, which is a mercy;
    read `GET /tools` rather than guessing.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

DEFAULT_URL = "http://127.0.0.1:25599"
ROOT = Path(__file__).resolve().parent.parent.parent


class BridgeError(RuntimeError):
    """The bridge answered, and the answer was no."""


@dataclass
class Bridge:
    url: str = DEFAULT_URL
    timeout: int = 60

    # ---- the wire ------------------------------------------------------------------------

    def call(self, tool: str, /, **args) -> dict:
        """One tool call. Returns its `result`; raises {@link BridgeError} if the tool refused."""
        request = urllib.request.Request(
            f"{self.url}/cmd",
            data=json.dumps({"tool": tool, "args": args}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            envelope = json.load(response)
        if not envelope.get("ok"):
            raise BridgeError(f"{tool}: {envelope.get('error') or envelope}")
        result = envelope.get("result")
        return result if isinstance(result, dict) else {"value": result}

    def tools(self) -> list[dict]:
        with urllib.request.urlopen(f"{self.url}/tools", timeout=self.timeout) as response:
            return json.load(response)

    def wait_for_tool(self, tool: str, seconds: int = 300) -> None:
        """Block until the game offers `tool`, which is not the same moment as the first pong.

        The bridge answers while the game is still starting, and the CLIENT's own tools - the whole
        of tier 3 - are registered later still. A run that trusts the pong asks for `create_world`
        and is told there is no such tool, which reads like a toolkit that is too old.
        """
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            try:
                if any(offered.get("name") == tool for offered in self.tools()):
                    return
            except (urllib.error.URLError, OSError, ValueError):
                pass
            time.sleep(2)
        raise BridgeError(
            f"the game on {self.url} never offered `{tool}` within {seconds}s. A client-only tool "
            "on a dedicated server, or a toolkit older than this suite, both look like this.")

    def alive(self) -> bool:
        try:
            self.call("ping")
            return True
        except (urllib.error.URLError, OSError, BridgeError):
            return False

    def wait(self, seconds: int = 300, *, server: bool = False) -> dict:
        """Block until the bridge answers a ping, and return what it said.

        `server=True` waits for the world as well, which is not the same moment: the bridge opens
        while the game is still starting, so a run that trusts the first pong asks a server that is
        not there yet and reads the refusal as its own failure.
        """
        deadline = time.monotonic() + seconds
        last = None
        while time.monotonic() < deadline:
            try:
                last = self.call("ping")
                if not server or last.get("serverRunning"):
                    return last
            except (urllib.error.URLError, OSError, BridgeError):
                pass
            time.sleep(2)
        raise BridgeError(
            f"no game answered on {self.url} within {seconds}s"
            if last is None else
            f"the bridge on {self.url} answered but no world had loaded within {seconds}s: {last}")

    # ---- the game ------------------------------------------------------------------------

    def command(self, command: str) -> dict:
        """A server command at full permission. The reply carries the game's own feedback."""
        return self.call("run_command", command=command)

    def say(self, command: str) -> str:
        """A command's feedback as one string - what a player would have read in chat."""
        result = self.command(command)
        lines = result.get("feedback") or result.get("messages") or result.get("output") or []
        if isinstance(lines, str):
            return lines
        return "\n".join(str(line) for line in lines)

    def log(self, **filters) -> list[dict]:
        return self.call("get_log", **filters).get("lines", [])

    def push(self, path: str, text: str, reload: bool = True) -> dict:
        """Write a file into the live world datapack - a third-party pack with no file in this tree."""
        import base64

        return self.call(
            "push_data",
            path=path,
            base64=base64.b64encode(text.encode("utf-8")).decode("ascii"),
            reload=reload,
        )

    def clear(self, path: str | None = None, reload: bool = True) -> dict:
        args = {"reload": reload}
        if path:
            args["path"] = path
        return self.call("clear_data", **args)

    # ---- the instance --------------------------------------------------------------------

    def build(self) -> dict:
        """What `ping` says about the jar this game is running. Empty on an older toolkit."""
        return self.call("ping").get("build") or {}

    def names_this_mod(self) -> bool:
        """Whether the attached game has Armor Pieces loaded at all."""
        mods = self.build().get("mods") or {}
        if isinstance(mods, dict):
            return "armorpieces" in mods
        return any("armorpieces" in str(mod) for mod in mods)
