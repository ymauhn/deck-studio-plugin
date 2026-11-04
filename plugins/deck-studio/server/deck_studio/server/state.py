"""StudioState: the one object every route and feature shares, as request.app.state.studio."""
import asyncio
import json
import secrets
from pathlib import Path

from deck_studio.core.history import create_history
from deck_studio.core.write_guard import create_guard
from deck_studio.deck_build import DeckBuilder
from deck_studio.server.events import EventHub


class StudioState:
    def __init__(self, config, data_dir, port, fake_agent=None, home=None, config_path=None):
        self.config = config
        self.kit_root = Path(config["kitRoot"])
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Deck Studio's home (--home): projects.json and the projects' data dirs, projects/<slug>; the data dir by default
        self.home = Path(home) if home else self.data_dir
        self.port = port
        self.token = secrets.token_urlsafe(24)
        self.fake_agent = Path(fake_agent) if fake_agent else None  # scenarios dir of the scripted agent
        self.config_path = config_path  # the --config file, if any: a project's studio gets it too
        self.events = EventHub()
        self.builder = DeckBuilder(config, self.events)
        self.history = create_history(self.data_dir / "history", self.kit_root)
        self.guard = create_guard(config)
        self.chats = {}  # id -> Chat
        # one agent turn (or direct edit) at a time across all chats; busy = turn_lock.locked()
        self.turn_lock = asyncio.Lock()
        self.settings = self._load_settings()
        self.selection = []  # the last selection sent with a message
        self.extras = {}  # free room for features
        self.auth = "unknown"  # last auth gate result: "ok" or "refused"
        self.usage = {"five_hour": None, "seven_day": None}

    def _load_settings(self):
        try:
            return json.loads((self.data_dir / "settings.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def save_settings(self):
        (self.data_dir / "settings.json").write_text(json.dumps(self.settings, indent=2), encoding="utf-8")

    def status(self):
        return {"auth": self.auth, "build": self.builder.state, "busy": self.turn_lock.locked(), "usage": self.usage}

    async def publish_status(self):
        await self.events.publish("status", **self.status())
