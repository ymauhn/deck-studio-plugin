// Build the single-file deck: deck/dist/nexus-go-defense.html (docs/BUILD.md §2).
// Usage: node deck/build.mjs [--images] [--fonts]
//        node deck/build.mjs --page <slides.html>   isolated page -> deck/build/harness/<name>.html
//        (only the slides in that file and the components they use; for component work, GIFs, PDFs)
//        node deck/build.mjs --studio   Deck Studio deck with data-loc source locations
//        -> deck/build/studio/nexus-go-defense.html (never the dist file)
//        node deck/build.mjs --studio --part <part.html>   the sections of one deck/src/slides file, each exactly
//        as the studio build makes it -> deck/build/studio/parts/<part.html>.json {part, css, slides: [{id, html}]}
//        node deck/build.mjs --pt   Portuguese deck from deck/src-pt -> deck/dist/nexus-go-defesa-pt.html
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import * as esbuild from 'esbuild';

const require = createRequire(import.meta.url);
const DECK = path.dirname(fileURLToPath(import.meta.url));
const KIT = path.dirname(DECK);
const argv = process.argv.slice(2);
const args = new Set(argv);
const PT = args.has('--pt');
const SRC = path.join(DECK, PT ? 'src-pt' : 'src');
const BUILD = path.join(DECK, 'build');
const DIST = path.join(DECK, 'dist', PT ? 'nexus-go-defesa-pt.html' : 'nexus-go-defense.html');
const TEX = path.join(KIT, 'source', 'thesis', 'dissertation.tex');
const PAGE = args.has('--page') ? path.resolve(argv[argv.indexOf('--page') + 1]) : null;
const PART = args.has('--part') ? path.basename(argv[argv.indexOf('--part') + 1]) : null;
const STUDIO = args.has('--studio') || PART !== null;
const read = (p) => fs.readFileSync(p, 'utf8');
fs.mkdirSync(BUILD, { recursive: true });
fs.mkdirSync(path.dirname(DIST), { recursive: true });

// 1. tables from the current .tex (the kit copy in data/ stays as shipped)
const TABLES = path.join(BUILD, 'thesis_tables.json');
if (fs.existsSync(TEX) && !((PAGE || PART) && fs.existsSync(TABLES))) execFileSync('python', ['-I', path.join(KIT, 'tools', 'extract_tables.py'), TEX, TABLES], { stdio: 'pipe' });
const tables = JSON.parse(read(fs.existsSync(TABLES) ? TABLES : path.join(KIT, 'data', 'thesis_tables.json')));
// stacking importances are stated in the text of §6.3.4, not in a table: parse them from the .tex
{
  const t = read(TEX).replace(/\s+/g, ' ');
  const num = (s) => +s.replace(/\\times ?10\^\{(-?\d+)\}/, 'e$1');
  const a = /decision tree assigns \$([\d.]+)\$ and \$([\d.]+)\$, the random forest \$([\d.]+)\$ and \$([\d.]+)\$/.exec(t);
  const b = /receive \$([^$]+)\$ and \$([\d.]+)\$ in the tree, \$([\d.]+)\$ and \$([\d.]+)\$ in the forest/.exec(t);
  if (!a || !b) throw new Error('stacking importances not found in dissertation.tex');
  tables.importances = {
    label: 'sec:res_late (text)', caption: 'Fitted feature importances of the tree-based stacking models',
    rows: [['Model', 'Fixed prob.', 'GNN prob.', 'IC', 'log-degree'],
      ['Decision tree', num(a[1]), num(a[2]), num(b[1]), num(b[2])],
      ['Random forest', num(a[3]), num(a[4]), num(b[3]), num(b[4])]],
  };
}

// 2. images
const IMG = path.join(BUILD, 'img');
if (args.has('--images') || !fs.existsSync(IMG)) {
  execFileSync('python', ['-I', path.join(DECK, 'tools', 'process_images.py'), path.join(KIT, 'source', 'thesis'), IMG], { stdio: 'inherit' });
}

// 2b. TikZ figures of §2.2.3 -> SVG (needs latex + dvisvgm, e.g. MiKTeX)
const SVGDIR = path.join(BUILD, 'svg');
if (args.has('--images') || !fs.existsSync(path.join(SVGDIR, 'tikz_mlp.svg'))) {
  execFileSync('python', ['-I', path.join(DECK, 'tools', 'render_tikz.py'), TEX, SVGDIR, path.join(BUILD, 'tikz-work')], { stdio: 'inherit' });
}

// 3. fonts: WOFF2 latin subsets from the Google Fonts CSS API, embedded as data URIs (cached)
const FONTS = path.join(BUILD, 'fonts.css');
const FONT_URL = 'https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,600..700&family=IBM+Plex+Mono:wght@400;500&display=swap';
if (args.has('--fonts') || !fs.existsSync(FONTS)) {
  try {
    const ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36';
    const css = await (await fetch(FONT_URL, { headers: { 'User-Agent': ua } })).text();
    const blocks = [...css.matchAll(/\/\*\s*([\w-]+)\s*\*\/\s*(@font-face\s*\{[^}]*\})/g)].filter((m) => m[1] === 'latin').map((m) => m[2]);
    const out = [];
    for (const b of blocks) {
      const url = /url\((https:[^)]+)\)/.exec(b)[1];
      const buf = Buffer.from(await (await fetch(url)).arrayBuffer());
      out.push(b.replace(/url\([^)]+\)/, `url(data:font/woff2;base64,${buf.toString('base64')})`));
    }
    fs.writeFileSync(FONTS, out.join('\n'));
    console.log(`fonts: ${out.length} faces embedded`);
  } catch (e) {
    console.warn(`fonts: download failed (${e.message}); the deck falls back to system faces offline`);
    if (!fs.existsSync(FONTS)) fs.writeFileSync(FONTS, '');
  }
}

// 4. math: TeX -> SVG with MathJax, no runtime library
const { mathjax } = require('mathjax-full/js/mathjax.js');
const { TeX } = require('mathjax-full/js/input/tex.js');
const { SVG } = require('mathjax-full/js/output/svg.js');
const { liteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js');
const { AllPackages } = require('mathjax-full/js/input/tex/AllPackages.js');
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const mjdoc = mathjax.document('', { InputJax: new TeX({ packages: AllPackages }), OutputJax: new SVG({ fontCache: 'none' }) });
const decode = (s) => s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&');
// data-tex keeps the source for the Beamer exporter (beamer/tools/extract.py)
const attr = (s) => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
const tex2svg = (t, display) => adaptor.outerHTML(mjdoc.convert(decode(t).trim(), { display }))
  .replace('<mjx-container', `<mjx-container data-tex="${attr(decode(t).trim())}"`);
let nMath = 0;
// a studio data-loc on the placeholder moves to div.eq (display) or mjx-container (inline)
const renderMath = (html) => html
  .replace(/<div class="m d"( data-loc="[^"]*")?>([\s\S]*?)<\/div>/g, (_, loc = '', t) => { nMath++; return `<div class="eq"${loc}>${tex2svg(t, true)}</div>`; })
  .replace(/<span class="m"( data-loc="[^"]*")?>([\s\S]*?)<\/span>/g, (_, loc = '', t) => { nMath++; return tex2svg(t, false).replace('<mjx-container', `<mjx-container${loc}`); });
// math dictionary for components: src/math.json plus components/<id>.math.json
const COMP = path.join(SRC, 'components');
const mathSrc = Object.assign(JSON.parse(read(path.join(SRC, 'math.json'))),
  ...fs.readdirSync(COMP).filter((f) => f.endsWith('.math.json')).map((f) => JSON.parse(read(path.join(COMP, f)))));
const mathDict = PART ? {} : Object.fromEntries(Object.entries(mathSrc).map(([k, t]) => [k, tex2svg(t, !k.startsWith('i:'))]));

// 5. slides: concatenate, pull out <style> blocks, render math, inline images
// --studio: data-loc="<kit-relative file>:<line>:<col>" (parse5 start-tag location, 1-based) on every
// element inside a section.slide except style/script/template, spliced into the raw text back to front
let annotate = (f, text) => text;
if (STUDIO) {
  const { parseFragment } = await import('parse5');
  const SKIP = new Set(['style', 'script', 'template']);
  annotate = (f, text) => {
    const rel = path.relative(KIT, f).split(path.sep).join('/'), ins = [];
    const walk = (n, inSlide) => {
      for (const c of n.childNodes || []) {
        if (!c.tagName || SKIP.has(c.tagName)) continue;
        const slide = inSlide || (c.tagName === 'section' && /(^|\s)slide(\s|$)/.test(c.attrs.find((a) => a.name === 'class')?.value || ''));
        const loc = c.sourceCodeLocation, st = loc?.startTag;
        if (slide && st) {
          // before the '/' of '/>', unless that slash ends an unquoted attribute value
          const selfClosing = text[st.endOffset - 2] === '/' && !Object.values(loc.attrs || {}).some((a) => a.endOffset > st.endOffset - 2);
          ins.push([st.endOffset - (selfClosing ? 2 : 1), ` data-loc="${rel}:${st.startLine}:${st.startCol}"`]);
        }
        walk(c, slide);
      }
    };
    walk(parseFragment(text, { sourceCodeLocationInfo: true }), false);
    for (const [o, s] of ins.sort((a, b) => b[0] - a[0])) text = text.slice(0, o) + s + text.slice(o);
    return text;
  };
}
let slideCss = '';
const slideFiles = PART ? [path.join(SRC, 'slides', PART)] : PAGE ? [PAGE] : fs.readdirSync(path.join(SRC, 'slides')).filter((f) => f.endsWith('.html')).sort().map((f) => path.join(SRC, 'slides', f));
const partCss = new Map(slideFiles.map((f) => [path.basename(f), ''])); // the studio deck keeps each file's CSS apart
let slides = slideFiles.map((f) => annotate(f, read(f)).replace(/<style>([\s\S]*?)<\/style>/g, (_, c) => {
  slideCss += c;
  partCss.set(path.basename(f), partCss.get(path.basename(f)) + c);
  return '';
})).join('\n');
// --part: only the file's slide sections, NUL-separated, so the steps below process each one as the full build does
const partIds = [];
if (PART) {
  const { parseFragment } = await import('parse5');
  const cut = [];
  const walk = (n) => {
    for (const c of n.childNodes || []) {
      if (c.tagName === 'section' && /(^|\s)slide(\s|$)/.test(c.attrs.find((a) => a.name === 'class')?.value || '')) cut.push(c);
      else walk(c);
    }
  };
  walk(parseFragment(slides, { sourceCodeLocationInfo: true }));
  partIds.push(...cut.map((s) => s.attrs.find((a) => a.name === 'id')?.value));
  slides = cut.map(({ sourceCodeLocation: l }) => slides.slice(l.startOffset, l.endOffset)).join('\0');
}
// tables from the .tex: <div class="tbl" data-table="key" [data-rows="1-9"] [data-cols="0,2"] [data-head="1"]></div>
const numbering = JSON.parse(read(path.join(KIT, 'data', 'numbering.json')));
const numberOf = (kind, label) => Object.entries(numbering[kind] || {}).find(([, ls]) => ls.includes(label))?.[0];
// --pt: deck/src-pt/cells.json translates table cells ({"Ontology": "Ontologia"}); numbers take a decimal comma
const CELLS = PT && fs.existsSync(path.join(SRC, 'cells.json')) ? JSON.parse(read(path.join(SRC, 'cells.json'))) : {};
const GREEK = { alpha: 'α', gamma: 'γ', kappa: 'κ', lambda: 'λ', tau: 'τ', rho: 'ρ', Delta: 'Δ', sigma: 'σ', varepsilon: 'ε', mu: 'μ' };
const texCell = (c) => {
  let s = String(c).replace(/^\\multicolumn\{\d+\}\{[^}]*\}\{(.*)\}$/, '$1');
  for (let i = 0; i < 4; i++) s = s.replace(/\\(?:textbf|emph|textit|mathrm|text|operatorname|mathbf)\{([^{}]*)\}/g, '$1');
  s = s.replace(/Equation~\\eqref\{([^}]+)\}/g, (_, l) => `Eq. ${numberOf('equation', l) || '?'}`)
    .replace(/\\(alpha|gamma|kappa|lambda|tau|rho|Delta|sigma|varepsilon|mu)(?![a-z])/g, (_, g) => GREEK[g])
    .replace(/\\(max|min|deg)(?![a-z])/g, '$1').replace(/\\times/g, '×').replace(/\\in(?![a-z])/g, '∈')
    .replace(/\\approx/g, '≈').replace(/\\downarrow/g, '↓').replace(/\\geq|>=/g, '≥').replace(/\\quad ?/g, '')
    .replace(/\\,/g, ' ').replace(/\\\{/g, '\u0001').replace(/\\\}/g, '\u0002').replace(/\\_/g, '_').replace(/\\ /g, ' ')
    .replace(/_\{([^{}]*)\}/g, '<sub>$1</sub>').replace(/\^\{([^{}]*)\}/g, '<sup>$1</sup>').replace(/_(\w)/g, '<sub>$1</sub>').replace(/\^(\*|\w)/g, '<sup>$1</sup>')
    .replace(/~/g, ' ').replace(/--/g, '–').replace(/(^|[\s(\[])-(?=\d)/g, '$1−').replace(/[{}]/g, '').replace(/\u0001/g, '{').replace(/\u0002/g, '}');
  if (/\\[a-zA-Z]/.test(s)) throw new Error(`table cell with unconverted TeX: ${c}`);
  return PT ? (CELLS[s] ?? s).replace(/(\d)\.(\d)/g, '$1,$2') : s;
};
const rangeOf = (r, n) => { if (!r) return [...Array(n).keys()]; return r.split(',').flatMap((p) => { const [a, b] = p.split('-').map(Number); return b === undefined ? [a] : [...Array(b - a + 1).keys()].map((k) => a + k); }); };
slides = slides.replace(/<div class="tbl([^"]*)" data-table="(\w+)"([^>]*)><\/div>/g, (_, extra, key, attrs) => {
  const t = tables[key];
  if (!t) throw new Error(`no table ${key}`);
  const at = (n) => (new RegExp(`data-${n}="([^"]*)"`).exec(attrs) || [])[1];
  const head = +(at('head') ?? 1);
  const cols = at('cols') ? at('cols').split(',').map(Number) : null;
  const rowIdx = rangeOf(at('rows'), t.raw.length - head).map((i) => i + head);
  const cells = (r, tag) => {
    let out = '', ci = 0;
    r.forEach((c, j) => {
      const mc = /^\\multicolumn\{(\d+)\}/.exec(c);
      const span = mc ? +mc[1] : 1;
      const keep = !cols || cols.includes(ci);
      if (keep) out += `<${tag}${span > 1 ? ` colspan="${span}"` : ''}>${texCell(c)}</${tag}>`;
      ci += span;
    });
    return `<tr>${out}</tr>`;
  };
  const num = numberOf('table', t.label);
  const style = (/style="([^"]*)"/.exec(attrs) || [])[1];
  const loc = at('loc'); // studio build only
  // data-rank="4,5,6": in those output columns the best value gets class best (bold) and the
  // second best class second (underlined), as lib/chart.js does for the chart tables
  let body = rowIdx.map((i) => cells(t.raw[i], 'td'));
  if (at('rank')) {
    const grid = body.map((r) => [...r.matchAll(/<td([^>]*)>(.*?)<\/td>/g)].map((m) => m[0]));
    const val = (c) => { let x = (c || '').replace(/<[^>]*>/g, '').replace(/[−–]/g, '-'); if (x.includes(',')) x = x.replace(/\./g, '').replace(',', '.'); const m = /^[+-]?\d+(\.\d+)?/.exec(x.trim()); return m ? parseFloat(m[0]) : NaN; };
    for (const c of at('rank').split(',').map(Number)) {
      const vs = [...new Set(grid.map((r) => val(r[c])).filter((v) => !Number.isNaN(v)))].sort((a, b) => b - a);
      grid.forEach((r) => { const v = val(r[c]); const k = v === vs[0] ? 'best' : v === vs[1] ? 'second' : ''; if (k && r[c]) r[c] = r[c].replace('<td', `<td class="${k}"`); });
    }
    body = grid.map((r) => `<tr>${r.join('')}</tr>`);
  }
  return `<div class="tbl${extra}"${style ? ` style="${style}"` : ''}${loc ? ` data-loc="${loc}"` : ''}><table class="t"><thead>${t.raw.slice(0, head).map((r) => cells(r, 'th')).join('')}</thead>`
    + `<tbody>${body.join('')}</tbody></table>`
    + `<div class="cap">${PT ? 'Dissertação, Tabela' : 'Dissertation, Table'} ${num || '?'}</div></div>`;
});
slides = renderMath(slides);
const missing = [];
const within = (dir, p) => { const r = path.relative(dir, p); return r && !r.startsWith('..') && !path.isAbsolute(r); };
const dataUri = (name) => {
  const folder = name.split('/')[0]; // img or svg
  let p = path.join(BUILD, name);
  if (!fs.existsSync(p) && folder === 'img') p = path.join(SRC, name); // user images in deck/src/img
  // a name that leaves its image folder (img/../x) is missing: a slide never pulls another file into the deck
  if (!fs.existsSync(p) || ![path.join(BUILD, folder), path.join(SRC, 'img')].some((d) => within(d, p))) { missing.push(name); return name; }
  const ext = path.extname(p).slice(1);
  const mime = { webp: 'image/webp', png: 'image/png', svg: 'image/svg+xml', jpg: 'image/jpeg' }[ext];
  return `data:${mime};base64,${fs.readFileSync(p).toString('base64')}`;
};
slides = slides.replace(/src="((?:img|svg)\/[^"]+)"/g, (_, n) => `src="${dataUri(n)}"`);
if (missing.length) throw new Error(`missing assets: ${missing.join(', ')}`);

if (PART) {
  const out = path.join(BUILD, 'studio', 'parts', `${PART}.json`), html = slides.split('\0');
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify({ part: PART, css: slideCss, slides: partIds.map((id, k) => ({ id, html: html[k] })) }));
  console.log(`built ${path.relative(KIT, out)}: ${partIds.length} slides, ${nMath} equations`);
  process.exit(0);
}

// 6. script bundle; the registry maps components/int-foo.js to data-component="INT-FOO"
const used = new Set([...slides.matchAll(/data-component="([^"]+)"/g)].map((m) => m[1]));
const compFiles = fs.readdirSync(COMP).filter((f) => /^int-[\w-]+\.js$/.test(f))
  .filter((f) => !PAGE || used.has(f.slice(0, -3).toUpperCase()));
const entry = [
  "import { startDeck } from './engine.js';",
  ...compFiles.map((f, i) => `import { mount as c${i} } from './components/${f}';`),
  `const registry = { ${compFiles.map((f, i) => `'${f.slice(0, -3).toUpperCase()}': c${i}`).join(', ')} };`,
  'const ctx = { data: window.NX_DATA, math: window.NX_MATH };',
  'window.NX = { registry, ctx };',
  STUDIO ? `(${studioRuntime})(startDeck, registry, ctx);` : 'startDeck(registry, ctx);',
].join('\n');
const bundle = await esbuild.build({ stdin: { contents: entry, resolveDir: SRC, sourcefile: 'entry.js' }, bundle: true, format: 'iife', minify: !PAGE, target: 'es2020', write: false });
const js = bundle.outputFiles[0].text.replace(/<\/script/gi, '<\\/script');

// 7. assemble
const compCss = fs.readdirSync(COMP).filter((f) => f.endsWith('.css')).sort().map((f) => read(path.join(COMP, f))).join('\n');
// the studio deck closes the shell's <style> early: each slide file's CSS follows in a <style data-part> of its own
const css = read(FONTS) + '\n' + read(path.join(SRC, 'deck.css')) + '\n' + compCss + '\n'
  + (STUDIO ? [...partCss].map(([f, c]) => `</style><style data-part="${f}">${c}`).join('') : slideCss);
const json = (o) => JSON.stringify(o).replace(/</g, '\\u003c');
const html = read(path.join(SRC, 'shell.html'))
  .replace('/*__CSS__*/', () => css)
  .replace('<!--__SLIDES__-->', () => slides)
  .replace('/*__DATA__*/', () => json(tables))
  .replace('/*__MATH__*/', () => json(mathDict))
  .replace('/*__JS__*/', () => js);
const OUT = PAGE ? path.join(BUILD, 'harness', path.basename(PAGE)) : STUDIO ? path.join(BUILD, 'studio', 'nexus-go-defense.html') : DIST;
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, html);
// the studio serves its deck with a CSP that runs only the shell's own scripts (data and bundle), never one that a
// slide or a CSS file holds: their hashes, from the shell filled the same way but with no slides and no CSS
if (STUDIO) {
  const shell = read(path.join(SRC, 'shell.html')).replace('/*__CSS__*/', '').replace('<!--__SLIDES__-->', '')
    .replace('/*__DATA__*/', () => json(tables)).replace('/*__MATH__*/', () => json(mathDict)).replace('/*__JS__*/', () => js);
  const hash = (t) => `'sha256-${crypto.createHash('sha256').update(t.replace(/\r\n?/g, '\n')).digest('base64')}'`;
  const scripts = [...shell.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => hash(m[1]));
  fs.writeFileSync(path.join(BUILD, 'studio', 'csp.json'), JSON.stringify({ scripts }));
}
const mb = fs.statSync(OUT).size / 1024 / 1024;
const nSlides = (slides.match(/<section class="slide/g) || []).length;
console.log(`built ${path.relative(KIT, OUT)}: ${nSlides} slides, ${nMath} equations, ${mb.toFixed(2)} MB${mb > 12 ? '  (over the 12 MB target!)' : ''}`);
if (mb > 16) process.exit(1);

// Studio deck only (bundled from its source text): window.__studio.swap(slides, css?) puts the sections of one
// slide file, from its --part build, in place without a page reload, and css replaces that file's <style>.
// The engine has no hook for this, so the swap restarts it on untouched copies of every section: steps,
// components, numbering and notes come out as on a fresh load, on the same slide and step. It returns false
// when it cannot swap (slides added, removed or reordered); the caller then reloads the page.
// ponytail: a presenter window opened before a swap still drives the old engine; reload to present.
function studioRuntime(startDeck, registry, ctx) {
  const stage = document.getElementById('stage');
  const sections = () => [...stage.querySelectorAll('section.slide')];
  const fileOf = (s) => s.dataset.loc?.replace(/:\d+:\d+$/, '');
  const fresh = new Map(sections().map((s) => [s.id, s.cloneNode(true)])); // before the engine changes them
  const listeners = [], components = []; // what the running engine attached and mounted
  const mounts = Object.fromEntries(Object.entries(registry).map(([id, mount]) => [id, (...a) => {
    const c = mount(...a);
    components.push(c);
    return c;
  }]));
  // the engine's own listeners; those added by other handlers of its events (deck:change) are not the engine's
  const start = () => {
    const { addEventListener: add, dispatchEvent: dispatch } = EventTarget.prototype;
    let inEvent = 0;
    EventTarget.prototype.addEventListener = function (...a) { if (!inEvent) listeners.push([this, a]); return add.apply(this, a); };
    EventTarget.prototype.dispatchEvent = function (e) { inEvent++; try { return dispatch.call(this, e); } finally { inEvent--; } };
    try { startDeck(mounts, ctx); } finally { Object.assign(EventTarget.prototype, { addEventListener: add, dispatchEvent: dispatch }); }
  };
  start();
  window.__studio = {
    swap(slides, css) {
      try {
        const tpl = document.createElement('template');
        const next = slides.map(({ id, html }) => {
          tpl.innerHTML = html;
          const s = tpl.content.firstElementChild;
          return tpl.content.childElementCount === 1 && s.matches('section.slide') && s.id === id ? s : null;
        });
        const file = next[0] && fileOf(next[0]);
        const style = css === undefined ? null
          : [...document.querySelectorAll('style[data-part]')].find((el) => file?.endsWith(`/${el.dataset.part}`));
        const ids = (list) => list.map((s) => s?.id).join(' ');
        if (!file || next.some((s) => !s || fileOf(s) !== file) || (css !== undefined && !style)
          || ids(next) !== ids([...fresh.values()].filter((s) => fileOf(s) === file))) return false;
        const { slide, fragment } = window.deck.state();
        const current = sections()[slide - 1].id;
        const overview = document.getElementById('deck').classList.contains('ov');
        for (const [target, a] of listeners.splice(0)) target.removeEventListener(...a);
        for (const c of components.splice(0)) c?.pause?.();
        for (const s of next) fresh.set(s.id, s);
        if (style) style.textContent = css;
        for (const s of sections()) s.replaceWith(fresh.get(s.id).cloneNode(true));
        start();
        window.deck.go(sections().findIndex((s) => s.id === current) + 1, fragment);
        if (overview) window.deck.overview(true);
        return true;
      } catch (e) {
        console.error(e);
        return false;
      }
    },
  };
}
