"""Renderer: a persistent headless Chromium page on the studio deck, for the agent's screenshots and slide checks
(SPEC "Deep modules" 7). It shows the built studio deck file itself (no picker, no network, no other local file)
at 1600x900, so one CSS pixel is one slide unit, and reloads it whenever a build has rewritten that file."""
import asyncio

from playwright.async_api import async_playwright

# outline the elements at these data-locs (and no other); returns the locs no element has
MARK = """(locs) => {
  for (const e of document.querySelectorAll('.studio-mark')) e.classList.remove('studio-mark');
  if (!document.getElementById('studio-mark-css')) document.head.append(Object.assign(document.createElement('style'), {
    id: 'studio-mark-css',
    textContent: '.studio-mark { outline: 4px solid #eb6834 !important; outline-offset: 4px !important; }',
  }));
  const all = [...document.querySelectorAll('[data-loc]')];
  return locs.filter((loc) => {
    const el = all.find((e) => e.dataset.loc === loc);
    el?.classList.add('studio-mark');
    return !el;
  });
}"""


# every visible element of the slide that leaves the 1600x900 frame, or whose box clips its content (the kit's own
# QA rules, qa/run_all.py, in slide units: a box that lets its content show is left to the screenshot, since font
# metrics alone make most text a few px taller than its line box); an element inside one already reported is left out
CHECK = """(s) => {
  const o = s.getBoundingClientRect(), k = o.width / 1600;
  const shown = (el) => { for (let e = el; e && e !== s; e = e.parentElement) { const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < 0.05) return false; } return true; };
  const where = (el) => {
    const at = el.closest('[data-loc]');
    return `${el.localName}${at ? ` (${at.dataset.loc})` : ''}`;
  };
  const out = [], seen = [];
  for (const el of s.querySelectorAll('*')) {
    if (el.closest('aside.notes, [hidden]') || seen.some((p) => p.contains(el)) || !shown(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;
    const [x0, y0, x1, y1] = [r.left - o.left, r.top - o.top, r.right - o.left, r.bottom - o.top]
      .map((v) => Math.round(v / k));
    const cs = getComputedStyle(el);
    if (x0 < -1 || y0 < -1 || x1 > 1601 || y1 > 901) {
      out.push(`outside the frame: ${where(el)} at x ${x0}..${x1}, y ${y0}..${y1}`);
      seen.push(el);
    } else if (!el.closest('svg') && /block|flex|grid|list-item|table-cell/.test(cs.display) && el.clientWidth > 0
               && cs.overflow !== 'visible'
               && (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1)) {
      out.push(`clipped: ${where(el)} holds ${el.scrollWidth}x${el.scrollHeight}`
               + ` in a ${el.clientWidth}x${el.clientHeight} box`);
      seen.push(el);
    }
  }
  return out;
}"""


class Renderer:
    def __init__(self, state):
        self.state = state
        self._lock = asyncio.Lock()  # one page: one screenshot or check at a time
        self._playwright = self._browser = self._page = None
        self._shown = None  # mtime of the deck file the page shows

    async def close(self):
        if self._playwright:
            await self._browser.close()
            await self._playwright.stop()
            self._playwright = self._browser = self._page = None

    async def screenshot(self, slide, step=None, highlight=()):
        """(PNG of the slide at 1600x900, its label); `highlight` lists the data-locs to outline."""
        async with self._lock:
            section, label = await self._show(slide, step)
            if missing := await self._page.evaluate(MARK, list(highlight)):
                label += f" Nothing has data-loc {', '.join(missing)} on this deck."
            try:
                return await section.screenshot(type="png"), label
            finally:
                await self._page.evaluate(MARK, [])

    async def check(self, slide, step=None):
        """(the slide's problems as text lines, its label)."""
        async with self._lock:
            section, label = await self._show(slide, step)
            return await section.evaluate(CHECK), label

    async def _show(self, slide, step):
        """Put the current build on the page at that slide (1-based) and step (None: the last one, everything
        shown); returns the slide's section and a label such as "Slide 13 (s13), step 3 of 3."."""
        await self.state.builder.current()  # a deck source changed outside the studio: built again first
        file = self.state.kit_root / self.state.config["studioOut"]
        mtime = file.stat().st_mtime_ns
        if self._page is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch()
            context = await self._browser.new_context(viewport={"width": 1600, "height": 900},
                                                      reduced_motion="reduce", color_scheme="light")
            # the deck file alone: it inlines its images and fonts (and also links fonts on the web), while a slide
            # may point at any file on the disk, which the agent would then see in its screenshots
            deck = file.as_uri()
            await context.route("**/*", lambda route: route.continue_() if route.request.url == deck
                                else route.abort())
            self._page = await context.new_page()
        if mtime != self._shown:
            await self._page.goto(file.as_uri())
            await self._page.wait_for_function("() => window.deck && window.deck.steps")
            self._shown = mtime
        steps = await self._page.evaluate("() => window.deck.steps()")
        if not 1 <= slide <= len(steps):
            raise ValueError(f"There is no slide {slide}: the deck has slides 1 to {len(steps)}.")
        last = steps[slide - 1]
        step = last if step is None else max(0, min(step, last))
        await self._page.evaluate("([n, f]) => window.deck.go(n, f)", [slide, step])
        await self._page.wait_for_timeout(300)  # components draw their step
        section = self._page.locator("#stage section.slide").nth(slide - 1)
        return section, f"Slide {slide} ({await section.get_attribute('id')}), step {step} of {last}."
