# STORYLINE: o roteiro do deck, slide a slide

Copie este arquivo para `docs/STORYLINE.md` e preencha. Ele vem ANTES dos slides: o autor revisa a storyline (a parada
da fase C) e só então os slides são escritos, um a um, como estão aqui. `qa/check_deck.py` lê este arquivo para
conferir os passos de cada slide.

Como ler cada entrada:

- **Título**: o título na tela, afirmativo (diz a conclusão).
- **Na tela**: o único texto do slide. Itens curtos, nada de parágrafo.
- **Visual**: uma figura de `docs/FIGURES.md` (pelo rótulo, "Fig. 3"), uma tabela, um gráfico, ou nenhum.
- **Tipo**: o exemplo de the plugin skill `deck-studio:criar-apresentacao`, file `exemplos/` que o slide copia (03-bullets-com-figura...).
- **Passos**: a ordem dos cliques, `F1`, `F2`... (o que entra em cada um), ou `nenhum`. O número de passos do slide no
  deck tem de ser igual ao maior F daqui.
- **Notas**: o que dizer, de 2 a 4 frases.
- **Fonte**: a página (e a figura ou tabela) de onde vem cada número e cada afirmação.
- **Corte**: `pular na versão curta` marca o slide que sai da versão curta.

Regras do texto: as de `ESTILO.md` §5. Duração-alvo: [n] min (versão curta: [n] min).

---

## Parte 0. Abertura

### s01 · [Nome curto]

- **Título**: [Nome curto]
- **Na tela**: [subtítulo]; [autor]; [orientação]; [evento, instituição, data]
- **Visual**: régua longa
- **Tipo**: 01-titulo
- **Passos**: nenhum
- **Notas**: [abertura em duas frases]
- **Fonte**: p. 1
- **Corte**: não

### s02 · Roteiro

- **Título**: Roteiro
- **Na tela**: [as partes, cada uma com um gancho]
- **Visual**: nenhum
- **Tipo**: 02-roteiro
- **Passos**: nenhum
- **Notas**: [a ordem da fala]
- **Fonte**: -
- **Corte**: não

## Parte 1. [Nome da parte]

### s03 · [Título afirmativo]

- **Título**: [...]
- **Na tela**: F1 [item]; F2 [item]; F3 [item]
- **Visual**: Fig. [n] (entra em F2)
- **Tipo**: 03-bullets-com-figura
- **Passos**: F1–F3
- **Notas**: [...]
- **Fonte**: p. [p], Fig. [n]
- **Corte**: não
