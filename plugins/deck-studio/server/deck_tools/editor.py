"""The plugin's visual editor: the project's studio build (every element carries data-loc="file:line:col") served on
127.0.0.1 with a token, plus a small script. The author clicks boxes (Shift adds), writes what to change and sends it;
ler_selecao gives that to Claude, which edits the sources. The page reloads, on the same slide, when the deck is
built again. No chat, no agent: the Claude Code session is the agent. Standard library only."""
import json
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

SCRIPT = r"""<script>
(() => {
  const T = new URLSearchParams(location.search).get('t');
  const css = document.createElement('style');
  css.textContent = `.ds-hover{outline:3px dashed #eb6834!important;outline-offset:3px!important}
    .ds-sel{outline:4px solid #eb6834!important;outline-offset:3px!important}
    #ds-panel{position:fixed;right:12px;bottom:12px;z-index:2147483647;width:360px;background:#fff;color:#111;
      border:1px solid #888;border-radius:8px;padding:10px 12px;font:14px/1.35 system-ui,sans-serif;box-shadow:0 6px 24px #0004}
    #ds-panel b{display:block;margin-bottom:4px}#ds-panel ol{max-height:150px;overflow:auto;margin:6px 0;padding-left:20px}
    #ds-panel li{margin:2px 0}#ds-panel code{font-size:12px;color:#555}#ds-panel textarea{width:100%;box-sizing:border-box;height:64px}
    #ds-panel button{margin:6px 6px 0 0;padding:6px 10px;font:inherit;cursor:pointer}#ds-panel p{margin:6px 0 0;color:#333}`;
  document.head.append(css);
  const panel = document.createElement('aside');
  panel.id = 'ds-panel';
  panel.setAttribute('aria-label', 'Seleção para o Claude');
  panel.innerHTML = '<b>Deck Studio: clique numa caixa (Shift soma)</b><ol></ol>' +
    '<textarea aria-label="O que mudar" placeholder="O que mudar nas caixas selecionadas"></textarea>' +
    '<button type="button" data-a="send">Enviar ao Claude</button><button type="button" data-a="clear">Limpar</button><p role="status"></p>';
  document.body.append(panel);
  const list = panel.querySelector('ol'), note = panel.querySelector('textarea'), status = panel.querySelector('p');
  let sel = [];
  const box = (e) => e.target.closest && e.target.closest('[data-loc]');
  const render = () => {
    list.replaceChildren(...sel.map((s) => {
      const li = document.createElement('li');
      li.textContent = `${s.texto.slice(0, 60) || s.tag} `;
      const c = document.createElement('code'); c.textContent = s.loc; li.append(c);
      return li;
    }));
  };
  document.addEventListener('mouseover', (e) => {
    document.querySelectorAll('.ds-hover').forEach((x) => x.classList.remove('ds-hover'));
    const t = box(e);
    if (t && !panel.contains(t)) t.classList.add('ds-hover');
  }, true);
  document.addEventListener('click', (e) => {
    if (panel.contains(e.target)) return;
    const t = box(e);
    if (!t) return;
    e.preventDefault(); e.stopPropagation();
    if (!e.shiftKey) { sel.forEach((s) => s.el.classList.remove('ds-sel')); sel = []; }
    const i = sel.findIndex((s) => s.el === t);
    if (i >= 0) { t.classList.remove('ds-sel'); sel.splice(i, 1); }
    else {
      const st = (window.deck && window.deck.state && window.deck.state()) || {};
      t.classList.add('ds-sel');
      sel.push({ el: t, loc: t.dataset.loc, tag: t.localName, slide: st.slide, passo: st.fragment,
                 texto: t.textContent.trim().replace(/\s+/g, ' ').slice(0, 400) });
    }
    render();
  }, true);
  panel.addEventListener('click', async (e) => {
    const a = e.target.dataset && e.target.dataset.a;
    if (a === 'clear') { sel.forEach((s) => s.el.classList.remove('ds-sel')); sel = []; note.value = ''; render(); status.textContent = ''; }
    if (a !== 'send') return;
    if (!sel.length && !note.value.trim()) { status.textContent = 'Selecione uma caixa ou escreva o pedido.'; return; }
    const body = { itens: sel.map(({ el, ...s }) => s), pedido: note.value.trim() };
    const r = await fetch(`/selecao?t=${T}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    status.textContent = r.ok ? 'Enviado. No Claude Code, diga: "aplique a seleção do editor".' : `Não foi (erro ${r.status}).`;
  });
  // the deck built again: reload on the same slide and step
  let version = null;
  const back = sessionStorage.getItem('ds-pos');
  if (back) {
    sessionStorage.removeItem('ds-pos');
    const [n, f] = JSON.parse(back);
    const go = () => (window.deck && window.deck.go ? window.deck.go(n, f) : setTimeout(go, 100));
    go();
  }
  setInterval(async () => {
    const r = await fetch(`/versao?t=${T}`).catch(() => null);
    if (!r || !r.ok) return;
    const v = await r.text();
    if (version !== null && v !== version) {
      const st = (window.deck && window.deck.state && window.deck.state()) || {};
      sessionStorage.setItem('ds-pos', JSON.stringify([st.slide || 1, st.fragment || 0]));
      location.reload();
    }
    version = v;
  }, 1000);
})();
</script>"""


class Editor:
    """One editor server per MCP process; it shows the project last opened."""

    def __init__(self):
        self.token = secrets.token_urlsafe(18)
        self.project = None
        self.selection = None
        self.server = None

    def deck(self):
        return Path(self.project) / "deck" / "build" / "studio" / "deck.html"

    def open(self, project):
        """The editor's URL on `project` (the server starts on first use, on a free port of 127.0.0.1)."""
        self.project, self.selection = Path(project), None
        if self.server is None:
            editor = self

            class Handler(BaseHTTPRequestHandler):
                def log_message(self, *args):  # stdout is the MCP channel: nothing may print there
                    pass

                def _ok(self):
                    if parse_qs(urlsplit(self.path).query).get("t", [""])[0] != editor.token:
                        self.send_error(403)
                        return False
                    return True

                def _send(self, body, kind):
                    self.send_response(200)
                    self.send_header("Content-Type", kind)
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

                def do_GET(self):
                    if not self._ok():
                        return
                    path = urlsplit(self.path).path
                    deck = editor.deck()
                    if path == "/versao":
                        return self._send(str(deck.stat().st_mtime_ns if deck.is_file() else 0).encode(), "text/plain")
                    if path != "/":
                        return self.send_error(404)
                    if not deck.is_file():
                        return self._send("<p>O deck ainda não foi construído: peça ao Claude para construir.</p>"
                                          .encode(), "text/html; charset=utf-8")
                    html = deck.read_text(encoding="utf-8")
                    at = html.lower().rfind("</body>")
                    html = html[:at] + SCRIPT + html[at:] if at >= 0 else html + SCRIPT
                    self._send(html.encode("utf-8"), "text/html; charset=utf-8")

                def do_POST(self):
                    if not self._ok() or urlsplit(self.path).path != "/selecao":
                        return
                    size = int(self.headers.get("Content-Length") or 0)
                    if size > 1_000_000:
                        return self.send_error(413)
                    try:
                        data = json.loads(self.rfile.read(size) or b"{}")
                    except ValueError:
                        return self.send_error(400)
                    editor.selection = {"recebida": time.strftime("%H:%M:%S"), **data}
                    out = Path(editor.project) / ".deck-studio" / "selecao.json"
                    out.parent.mkdir(exist_ok=True)
                    out.write_text(json.dumps(editor.selection, ensure_ascii=False, indent=1), encoding="utf-8")
                    self._send(b"{}", "application/json")

            self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            threading.Thread(target=self.server.serve_forever, name="deck-editor", daemon=True).start()
        return f"http://127.0.0.1:{self.server.server_address[1]}/?t={self.token}"

    def read(self):
        """The last selection sent (also saved in .deck-studio/selecao.json), or None."""
        if self.selection is None and self.project:
            saved = Path(self.project) / ".deck-studio" / "selecao.json"
            if saved.is_file():
                self.selection = json.loads(saved.read_text(encoding="utf-8"))
        return self.selection
