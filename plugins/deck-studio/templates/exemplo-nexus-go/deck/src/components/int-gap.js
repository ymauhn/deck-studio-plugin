// INT-GAP (S03): sequence records vs manually reviewed records, to scale. Numbers from the
// reference the dissertation cites for this gap (UniProt Consortium, NAR 2025, release
// 2024_04: about 246 million records in UniProtKB) and the Swiss-Prot statistics of the same
// release (571,864 entries). At the component's step 2 both bars grow over GROW s with the
// same easing; the reviewed bar is 0.23% of the other, so it gets a hairline minimum width.

const GROW = 1.2;
const SEQ = 246e6, REV = 571864;
const TARGET = [1, REV / SEQ];
const MIN_PX = 3;
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : 1 - Math.pow(1 - x, 3)); // matches the CSS curve closely

export function mount(el, { reduced = false } = {}) {
  el.classList.add('gp');
  el.innerHTML = `
    <div class="gp-row"><span class="gp-lab">sequence records in UniProtKB: about <b class="num">246 million</b></span><i class="gp-bar gp-seq"></i></div>
    <div class="gp-row"><span class="gp-lab">manually reviewed (Swiss-Prot): <b class="num">571,864</b> (<b class="num">0.23%</b>)</span><i class="gp-bar gp-fuse"></i></div>
    <p class="cap">UniProt release 2024_04, to scale</p>`;
  const bars = [...el.querySelectorAll('.gp-bar')];
  let n = 0, f = 0;

  // f in [0, 1] is the growth progress; animate only when growing on a live slide
  function set(p, animate) {
    f = p;
    el.classList.toggle('gp-anim', animate);
    bars.forEach((b, i) => { b.style.width = p > 0 ? `max(${MIN_PX}px, ${(p * TARGET[i] * 100).toFixed(3)}%)` : '0'; });
  }
  set(0, false);

  return {
    step(k) { n = k; set(k >= 2 ? 1 : 0, k >= 2 && !reduced); },
    render(t) { set(ease(t / GROW), false); },
    play() {}, pause() {},
    destroy() { el.innerHTML = ''; },
    state() { return { step: n, grown: f === 1, widths: TARGET.map((w) => +(w * f).toFixed(4)), duration: GROW }; },
  };
}
