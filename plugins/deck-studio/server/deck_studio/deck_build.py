"""DeckBuilder: the studio build of the deck, serialized and coalesced, announced as `build` events.
Edits to slide files alone reach the screen first through their part builds, swapped in place (`deck-swap`)."""
import asyncio
import json
import os
from pathlib import Path

from deck_studio.config import run_command


class DeckBuilder:
    def __init__(self, config, events):
        self.config = config
        self.events = events
        self.state = {"ok": None, "ms": None, "error": None, "running": False}  # replaced, never mutated
        # one build at a time, part builds included; the jobs' clean builds take it too (all of them write deck/build)
        self.lock = asyncio.Lock()
        self._queued = None  # the build not started yet: every request made meanwhile shares it
        self._last = None  # the newest build or swap task, queued or running

    async def build_studio(self):
        """A full studio build that starts after this call (shared with other waiting requests); returns the state."""
        if self._queued is None:
            self._queued = self._last = asyncio.ensure_future(self._build())
        return await asyncio.shield(self._queued)

    async def wait(self):
        """Return once no build or swap is running or queued."""
        if self._last:
            await asyncio.shield(self._last)

    async def current(self):
        """wait(), then a full build when a deck source changed after the last build's output: in an editor or by
        a shell command, which the studio does not hear about. Returns the state."""
        await self.wait()
        sources = self._sources()
        out = Path(self.config["kitRoot"]) / self.config["studioOut"]
        try:
            # the deck's CSP (csp.json next to it) comes from the same build: a deck without one is built again
            built = min(out.stat().st_mtime_ns, (out.parent / "csp.json").stat().st_mtime_ns)
            stale = any(p.stat().st_mtime_ns > built for p in [sources, *sources.rglob("*")])  # folders: deletions
        except OSError:  # no output yet, or a file went away meanwhile
            stale = True
        return await self.build_studio() if stale else self.state

    def _sources(self):
        """The deck's sources folder (deck/src): nothing else the studio writes feeds the studio build."""
        return Path(self.config["kitRoot"]) / Path(self.config["slidesDir"]).parent

    async def sources_changed(self, paths):
        """Files changed. Those outside the deck sources (a .tex or a context file, say) are left out, and with
        none left nothing is built. Slide files only: their part builds go out in one `deck-swap` event, then the
        full build runs with no reload. Anything else, or a part build that fails: the full build, then
        `deck-reload` when it is good. Returns the full build's state."""
        sources = self._sources().resolve()
        paths = [p for p in paths if (Path(self.config["kitRoot"]) / p).resolve().is_relative_to(sources)]
        if not paths:
            return self.state
        names = self._slide_files(paths)
        if not names:
            return await self._reload()
        # wait() covers the swap: a deck loaded during the part builds gets the build after them, not the one before
        self._last = swap = asyncio.ensure_future(self._swap(names))
        return await asyncio.shield(swap)

    async def _swap(self, names):
        parts = await self._part_builds(names)
        if not parts:
            return await self._reload()
        await self.events.publish("deck-swap", parts=parts)
        # queued before any other task runs: a deck that cannot swap reloads /deck, which waits for this build
        return await self.build_studio()

    async def _reload(self):
        state = await self.build_studio()
        if state["ok"]:
            await self.events.publish("deck-reload")
        return state

    def _slide_files(self, paths):
        """The file names when every path (absolute or kit-relative) is a slide file, else None."""
        root = Path(self.config["kitRoot"])
        slides = os.path.normcase((root / self.config["slidesDir"]).resolve())
        files = [(root / p).resolve() for p in paths]
        if all(os.path.normcase(f.parent) == slides and f.suffix.lower() == ".html" for f in files):
            return sorted({f.name for f in files})
        return None

    async def _part_builds(self, names):
        """{part, css, slides: [{id, html}]} of each file, or None when one fails."""
        if not self.config.get("partBuild"):
            return None
        out = Path(self.config["kitRoot"]) / self.config["partOut"]
        parts = []
        # ponytail: part builds are serialized, not coalesced; one per call is fine at an edit's pace
        async with self.lock:
            for name in names:
                code, _, _ = await run_command(self.config, [*self.config["partBuild"], name])
                if code != 0:
                    return None
                try:
                    parts.append(json.loads((out / f"{name}.json").read_text(encoding="utf-8")))
                except (OSError, ValueError):
                    return None
        return parts

    async def _build(self):
        async with self.lock:
            self._queued = None
            self.state = {**self.state, "running": True}
            await self.events.publish("build", **self.state)
            code, output, ms = await run_command(self.config, self.config["studioBuild"])
            ok = code == 0
            self.state = {"ok": ok, "ms": ms, "error": None if ok else output[-4000:], "running": False}
            await self.events.publish("build", **self.state)
            return self.state
