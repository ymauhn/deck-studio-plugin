// Injected by beamer/tools/extract.py into deck/dist/nexus-go-defense.html.
// Finds the text leaves of the active slide (text that becomes native LaTeX), measures every
// word on the 1600×900 canvas, and switches the page into "layer" mode, where those words,
// raster figures and figure masks are hidden so Chromium prints only the remaining visuals.
window.BX = (() => {
  const css = `
  html.bx #chrome, html.bx #notes, html.bx #help, html.bx #presenter { display: none !important; }
  html.bx *, html.bx *::before, html.bx *::after { transition: none !important; caret-color: transparent !important; }
  html.bx-layer .bx-t, html.bx-layer img.bx-img, html.bx-layer .bx-mask { visibility: hidden !important; }
  html.bx-solo .bx-off { visibility: hidden !important; }`;
  const st = document.createElement('style');
  st.textContent = css;
  document.head.append(st);
  document.documentElement.classList.add('bx');

  const slide = () => document.querySelector('section.slide.active');
  let box = null;
  const geo = (r) => ({ x: (r.left - box.left) / box.k, y: (r.top - box.top) / box.k, w: r.width / box.k, h: r.height / box.k });
  const frame = () => { const r = slide().getBoundingClientRect(); box = { left: r.left, top: r.top, k: r.width / 1600 }; };

  const SKIP = '[data-component], svg, aside.notes, script, style, img, .mask, select, input, button, mjx-container';
  const inlineLevel = (el) => { const d = getComputedStyle(el).display; return d.startsWith('inline') || d === 'contents' || d === 'none'; };
  const hasText = (nodes) => nodes.some((n) => (n.nodeType === 3 && n.textContent.trim()) || (n.nodeType === 1 && (n.tagName === 'MJX-CONTAINER' || n.querySelector?.('mjx-container') || (!n.closest(SKIP) && n.textContent.trim()))));
  // an inline subtree qualifies when everything in it is inline-level and not a visual
  const inlineOk = (el) => el.tagName === 'MJX-CONTAINER' || (!el.matches('[data-component], svg, select, input, button') && inlineLevel(el) && [...el.children].every(inlineOk));

  // leaves: {el, nodes} where nodes are the child nodes that hold the inline run
  function findLeaves(root) {
    const out = [];
    const walk = (el) => {
      if (el.matches(SKIP)) return;
      const kids = [...el.childNodes].filter((n) => n.nodeType === 1 || n.nodeType === 3);
      const blocky = kids.filter((n) => n.nodeType === 1 && !inlineOk(n));
      if (!blocky.length) { if (hasText(kids) && !inlineLevel(el)) out.push({ el, nodes: kids }); return; }
      // mixed: group consecutive inline nodes into anonymous runs, recurse into block children
      let run = [];
      const flush = () => { if (hasText(run)) out.push({ el, nodes: run }); run = []; };
      for (const n of kids) {
        if (n.nodeType === 1 && !inlineOk(n)) { flush(); walk(n); } else run.push(n);
      }
      flush();
    };
    walk(root);
    return out;
  }

  // wrap text nodes in span.bx-t so layer mode can hide glyphs without touching boxes and markers
  function wrapText(nodes) {
    const wrap = (n) => {
      if (n.nodeType === 3) {
        if (!n.textContent.trim()) return n;
        const s = document.createElement('span');
        s.className = 'bx-t';
        n.replaceWith(s); s.append(n);
        return s;
      }
      if (n.tagName === 'MJX-CONTAINER') { n.classList.add('bx-t'); return n; }
      [...n.childNodes].forEach(wrap);
      return n;
    };
    return nodes.map(wrap);
  }

  const descCache = new Map();
  function descent(cs) {
    const key = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    if (descCache.has(key)) return descCache.get(key);
    const d = document.createElement('div');
    d.style.cssText = `position:absolute;left:0;top:0;white-space:nowrap;line-height:normal;font:${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    d.textContent = 'Hxgy';
    const p = document.createElement('span');
    p.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
    d.append(p);
    slide().append(d);
    const r = document.createRange(); r.selectNodeContents(d.firstChild);
    const v = r.getBoundingClientRect().bottom - p.getBoundingClientRect().bottom;
    d.remove();
    descCache.set(key, v / box.k);
    return v / box.k;
  }

  const famKey = (f) => (f.includes('Bricolage') ? 'd' : f.includes('Plex') ? 'm' : 'b');
  function fontOf(el) {
    const cs = getComputedStyle(el);
    const fv = /"opsz"\s+([\d.]+)/.exec(cs.fontVariationSettings);
    let va = 0;
    for (let e = el; e && e.tagName !== 'LI' && e.tagName !== 'P' && e.tagName !== 'DIV'; e = e.parentElement) {
      if (e.tagName === 'SUB') va = -1; else if (e.tagName === 'SUP') va = 1;
    }
    return {
      fam: famKey(cs.fontFamily), w: +cs.fontWeight, it: cs.fontStyle === 'italic', size: parseFloat(cs.fontSize),
      color: cs.color, ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing) / parseFloat(cs.fontSize),
      opsz: fv ? +fv[1] : null, va, desc: descent(cs),
    };
  }

  // tokens of a leaf in reading order: words, math, gaps; each with canvas rects
  function tokens(nodes) {
    const out = [];
    let space = false;
    const word = (node, a, b, font) => {
      const r = document.createRange(); r.setStart(node, a); r.setEnd(node, b);
      const rs = [...r.getClientRects()].filter((q) => q.width > 0);
      if (rs.length > 1) {   // the word wraps (after a hyphen or slash): split it where the line changes
        for (let i = a + 1; i < b; i++) {
          const q = document.createRange(); q.setStart(node, i); q.setEnd(node, i + 1);
          const c = q.getClientRects()[0];
          if (c && c.top > rs[0].bottom - 2) { word(node, a, i, font); word(node, i, b, font); return; }
        }
      }
      if (!rs.length) return;
      out.push({ k: 'w', s: node.textContent.slice(a, b), sp: space, r: geo(rs[0]), f: font });
      space = false;
    };
    const walk = (n) => {
      if (n.nodeType === 3) {
        const t = n.textContent;
        const font = fontOf(n.parentElement);
        const re = /\S+|\s+/g; let m;
        while ((m = re.exec(t))) {
          if (/^\s/.test(m[0])) space = true; else word(n, m.index, m.index + m[0].length, font);
        }
        return;
      }
      if (n.nodeType !== 1) return;
      const cs = getComputedStyle(n);
      if (cs.display === 'none') return;
      if (n.tagName === 'BR') { space = false; return; }
      if (n.tagName === 'MJX-CONTAINER') {
        const svg = n.querySelector('svg');
        const r = svg.getBoundingClientRect();
        const vb = svg.viewBox.baseVal;
        const va = parseFloat(getComputedStyle(svg).verticalAlign) || 0;
        // vertical-align (CSS px, pre-transform) moves the svg bottom below the parent baseline
        out.push({ k: 'm', tex: n.dataset.tex, display: n.getAttribute('display') === 'true', sp: space, r: geo(r),
          em: (r.height / box.k) / (vb.height / 1000), base: (r.bottom - box.top) / box.k + va, color: getComputedStyle(n).color, f: fontOf(n) });
        space = false;
        return;
      }
      if (!n.textContent.trim() && !n.querySelector('mjx-container')) {   // inline visual (bar, chip): keep its room
        const r = n.getBoundingClientRect();
        if (r.width > 0) {
          const ml = parseFloat(cs.marginLeft) || 0, mr = parseFloat(cs.marginRight) || 0;
          out.push({ k: 'g', sp: space, r: geo(r), w: r.width / box.k + ml + mr });
          space = false;
        }
        return;
      }
      [...n.childNodes].forEach(walk);
    };
    nodes.forEach(walk);
    return out;
  }

  const visible = (el) => el.checkVisibility({ opacityProperty: true, visibilityProperty: true });
  let leaves = [], imgs = [], masks = [];

  return {
    // once per slide, at its final state: find and wrap leaves, tag raster figures and masks
    prepare() {
      frame();
      const s = slide();
      leaves = findLeaves(s).map((l, i) => ({ ...l, id: i, nodes: wrapText(l.nodes) }));
      imgs = [...s.querySelectorAll('img')].filter((im) => !im.closest('[data-component]') && !/\.svg$/.test(im.getAttribute('src') || '') && !im.src.startsWith('data:image/svg'));
      imgs.forEach((im) => im.classList.add('bx-img'));
      masks = [...s.querySelectorAll('.fig .mask')].filter((m) => !m.closest('[data-component]'));
      masks.forEach((m) => m.classList.add('bx-mask'));
      return { leaves: leaves.length, imgs: imgs.length, masks: masks.length };
    },
    // measurements of the current state: visible leaves (with tokens), figures and masks
    snapshot(want) {
      frame();
      const vis = [];
      const data = {};
      for (const l of leaves) {
        const host = l.nodes.find((n) => n.nodeType === 1) || l.el;
        if (!visible(host.nodeType === 1 ? host : l.el) || !visible(l.el)) continue;
        vis.push(l.id);
        if (want.includes(l.id)) {
          const cs = getComputedStyle(l.el);
          data[l.id] = { align: cs.textAlign, lh: cs.lineHeight === 'normal' ? null : parseFloat(cs.lineHeight) / box.k,
            font: fontOf(l.el), toks: tokens(l.nodes), tag: l.el.tagName.toLowerCase(), cls: l.el.className };
        }
      }
      const fit = (im) => {   // drawn rect of an <img> with object-fit
        const r = geo(im.getBoundingClientRect());
        const cs = getComputedStyle(im);
        const pl = parseFloat(cs.paddingLeft) + parseFloat(cs.borderLeftWidth), pt = parseFloat(cs.paddingTop) + parseFloat(cs.borderTopWidth);
        const cw = r.w - pl - parseFloat(cs.paddingRight) - parseFloat(cs.borderRightWidth), ch = r.h - pt - parseFloat(cs.paddingBottom) - parseFloat(cs.borderBottomWidth);
        let w = cw, h = ch;
        if (cs.objectFit === 'contain') { const k = Math.min(cw / im.naturalWidth, ch / im.naturalHeight); w = im.naturalWidth * k; h = im.naturalHeight * k; }
        return { x: r.x + pl + (cw - w) / 2, y: r.y + pt + (ch - h) / 2, w, h };
      };
      return {
        vis, data,
        imgs: imgs.map((im, i) => ({ i, src: im.getAttribute('src'), vis: visible(im), r: fit(im) })),
        masks: masks.map((m, i) => ({ i, vis: visible(m), r: geo(m.getBoundingClientRect()) })),
      };
    },
    layer(on) { document.documentElement.classList.toggle('bx-layer', on); },
    // hide everything on the slide except sel (for cropped animation and explorer frames)
    solo(sel) {
      const h = document.documentElement;
      document.querySelectorAll('.bx-off').forEach((e) => e.classList.remove('bx-off'));
      h.classList.toggle('bx-solo', !!sel);
      if (!sel) return null;
      const t = slide().querySelector(sel);
      for (let e = t; e && e !== slide(); e = e.parentElement) {
        for (const sib of e.parentElement.children) if (sib !== e) sib.classList.add('bx-off');
      }
      frame();
      return geo(t.getBoundingClientRect());
    },
    rect(sel) { frame(); const e = slide().querySelector(sel); return e ? geo(e.getBoundingClientRect()) : null; },
    // slide-number chrome (hidden in bx mode): right edge and baseline of its text
    num() {
      const h = document.documentElement, e = document.getElementById('num');
      h.classList.remove('bx'); frame();
      const q = document.createRange(); q.selectNodeContents(e);
      const r = q.getBoundingClientRect();
      const out = { right: (r.right - box.left) / box.k, base: (r.bottom - box.top) / box.k - descent(getComputedStyle(e)), font: fontOf(e) };
      h.classList.add('bx');
      return out;
    },
  };
})();
