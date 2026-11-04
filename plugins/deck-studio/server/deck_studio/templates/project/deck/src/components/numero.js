// NUMERO: a number that counts. The element's text is already the final value (what the PDF, search and the number
// audit read); when its step comes, it counts from "de" (0) to the value.
// <span data-component="NUMERO" data-opts='{"valor": 30, "casas": 0, "sufixo": " cm/s", "passo": 1}'>30 cm/s</span>
COMPONENTS.NUMERO = (el, o) => {
  const casas = o.casas ?? 0, txt = (v) => `${o.prefixo || ''}${K.fmt(v, casas)}${o.sufixo || ''}`;
  const passo = o.passo ?? 0;
  el.classList.add('cp-numero');
  let on = null, stop = () => {};
  return {
    step(n) {
      const now = n >= passo;
      if (now === on) return;
      on = now;
      stop();
      stop = now ? K.count(o, o.de ?? 0, o.valor, o.ms || 900, (v) => { el.textContent = txt(v); }) : () => {};
      if (!now) el.textContent = txt(o.de ?? 0);
    },
    pause() { stop(); el.textContent = txt(o.valor); },
  };
};
