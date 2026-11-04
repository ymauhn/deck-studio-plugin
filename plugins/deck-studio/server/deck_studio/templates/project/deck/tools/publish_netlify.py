"""Publish the deck on Netlify: deck/dist/deck.html as a one-page site (noindex), the same way the NEXUS-GO kit's
deck/tools/publish_netlify.ps1 does, in Python and for Windows, macOS and Linux.

Usage (from the project folder):
  python -I deck/tools/publish_netlify.py register --name NAME [--create]
        NAME is the site's name on Netlify (NAME.netlify.app). With --create, a new site with that name is made;
        without it, the site must already exist in the logged-in account. Either way, deck/tools/netlify-site.json
        keeps {id, name, url}, and Deck Studio shows Publicar from then on.
  python -I deck/tools/publish_netlify.py
        Uploads deck/dist/deck.html (build it first: python -I -X utf8 deck/build.py) to the registered site and
        waits until Netlify says it is ready. Prints the site's URL.
The token is the Netlify CLI's own (`netlify login` saves it): NETLIFY_AUTH_TOKEN, else the CLI's config file. It is
never printed. NETLIFY_API changes the API address (the tests use a local stand-in). Standard library only.
"""
import argparse
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(__file__).resolve().parent / "netlify-site.json"
DECK = ROOT / "deck" / "dist" / "deck.html"
API = os.environ.get("NETLIFY_API", "https://api.netlify.com/api/v1").rstrip("/")
HEADERS = "/*\n  X-Robots-Tag: noindex, nofollow\n"
ROBOTS = "User-agent: *\nDisallow: /\n"


def token():
    if os.environ.get("NETLIFY_AUTH_TOKEN"):
        return os.environ["NETLIFY_AUTH_TOKEN"]
    places = [Path(os.environ.get("APPDATA", "")) / "netlify" / "Config" / "config.json",  # Windows
              Path.home() / "Library" / "Preferences" / "netlify" / "config.json",  # macOS
              Path.home() / ".config" / "netlify" / "config.json"]  # Linux
    for place in places:
        try:
            users = json.loads(place.read_text(encoding="utf-8-sig")).get("users", {})
        except (OSError, ValueError):
            continue
        for user in users.values():
            t = (user.get("auth") or {}).get("token")
            if t:
                return t
    sys.exit("No Netlify login on this computer: run `npx netlify login` once, then try again.")


def call(method, path, body=None, content_type="application/json"):
    data = json.dumps(body).encode() if isinstance(body, dict) else body
    req = urllib.request.Request(f"{API}{path}", data=data, method=method,
                                 headers={"Authorization": f"Bearer {token()}", "Content-Type": content_type})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        sys.exit(f"Netlify answered {e.code} to {method} {path}: {detail}")


def register(name, create):
    name = name.strip().lower()
    if not name or not all(c.isalnum() or c == "-" for c in name):
        sys.exit("The site's name takes letters, digits and hyphens only.")
    site = call("POST", "/sites", {"name": name}) if create else call("GET", f"/sites/{name}.netlify.app")
    saved = {"id": site["id"], "name": site.get("name", name),
             "url": site.get("ssl_url") or site.get("url") or f"https://{name}.netlify.app"}
    SITE.write_text(json.dumps(saved, indent=2), encoding="utf-8")
    print(f"registered {saved['url']}")
    return saved


def publish():
    if not SITE.is_file():
        sys.exit("No site registered yet: python -I deck/tools/publish_netlify.py register --name NAME [--create]")
    if not DECK.is_file():
        sys.exit("No deck/dist/deck.html: build it first (python -I -X utf8 deck/build.py).")
    site = json.loads(SITE.read_text(encoding="utf-8"))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html", DECK.read_bytes())
        z.writestr("_headers", HEADERS)
        z.writestr("robots.txt", ROBOTS)
    deploy = call("POST", f"/sites/{site['id']}/deploys", buf.getvalue(), "application/zip")
    end = time.monotonic() + 300
    while deploy.get("state") not in ("ready", "error") and time.monotonic() < end:
        time.sleep(2)
        deploy = call("GET", f"/deploys/{deploy['id']}")
    print(f"{deploy.get('state')}: {site['url']}")
    return deploy.get("state") == "ready"


if __name__ == "__main__":
    p = argparse.ArgumentParser(prog="publish_netlify.py")
    sub = p.add_subparsers(dest="cmd")
    r = sub.add_parser("register")
    r.add_argument("--name", required=True)
    r.add_argument("--create", action="store_true")
    a = p.parse_args()
    if a.cmd == "register":
        register(a.name, a.create)
    else:
        sys.exit(0 if publish() else 1)
