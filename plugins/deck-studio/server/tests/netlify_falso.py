"""A local stand-in for the Netlify API (what deck/tools/publish_netlify.py calls), for the smoke test: it creates
sites, takes each deploy's zip and says it is ready. Nothing leaves the machine. Standard library only."""
import http.server
import json
import threading


def start():
    """(the API base URL to put in NETLIFY_API, {site id: last deploy zip bytes}, the server)."""
    sites, deploys = {}, {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body):
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path.startswith("/api/v1/deploys/"):
                return self.send(200, {"id": "d", "state": "ready"})
            name = self.path.rsplit("/", 1)[1].removesuffix(".netlify.app")
            site = next((s for s in sites.values() if s["name"] == name), None)
            self.send(200, site) if site else self.send(404, {"message": "Not Found"})

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            if self.path == "/api/v1/sites":
                name = json.loads(body)["name"]
                sites[f"id-{name}"] = site = {"id": f"id-{name}", "name": name, "ssl_url": f"https://{name}.netlify.app"}
                return self.send(201, site)
            deploys[self.path.split("/")[4]] = body
            self.send(200, {"id": "d", "state": "uploaded"})

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_address[1]}/api/v1", deploys, server
