# RUBRICA do juiz

O juiz confere o que as checagens automáticas não medem. Ele junta a revisão visual "do fundo da sala" do kit NEXUS-GO (`docs/QA.md` §4), a lista do que evitar (`docs/DESIGN.md` §8) e as regras do método. Ele só lê. Quem corrige é o agente do autor.

## Como dar a nota

Cada slide leva uma nota de 0 a 3 em cada critério. Um item é **BLOQUEANTE** quando o slide não pode ir para a sala assim: alguém lê errado, um número não tem fonte, o texto não se lê do fundo, ou o slide contradiz a fonte.

## Critérios por slide

1. **Uma ideia.** O slide defende uma coisa só. Duas ideias pedem dois slides.
2. **Título afirmativo.** O título diz a conclusão, não o assunto. As exceções são o título da fala, o roteiro, "Limitações", "Próximos passos" e os slides de abertura de parte.
3. **Do fundo da sala.**
   - nada menor que 18 px na tela, salvo legendas;
   - nenhuma figura pequena demais para ler;
   - o slide não está lotado;
   - o alinhamento entre irmãos é o mesmo;
   - o texto não foi encolhido em vez de cortado.
4. **Números com fonte.** Cada número está na fonte ou em `docs/FACTS.md`, com a precisão da fonte e a vírgula decimal no português. Um número sem fonte é sempre BLOQUEANTE.
5. **Notas.** De 2 a 4 frases, que dizem o que falar, terminando com a página da fonte: `(p. 12)`.
6. **Cores com sentido.**
   - `--c1`, `--c2` e `--c3` só para os conceitos registrados em `docs/DECISIONS.md`;
   - `--warn` só para ressalvas;
   - texto nunca na cor de uma série.
7. **Passos.** Um item por clique; a figura entra com o item que fala dela; nada aparece antes da hora nem fica faltando no fim.
8. **Fiel à fonte.** O slide não diz mais do que a fonte diz: nenhuma conclusão inventada, nenhum resultado exagerado e as limitações declaradas.
9. **O que evitar.**
   - cards em toda parte, emoji, ícone como marcador;
   - texto centralizado, degradê;
   - ilustração genérica;
   - travessão;
   - metacomentário ("este slide mostra").

## Critérios do deck inteiro

- **Interatividade e visualização de dados (BLOQUEANTE quando falta).** O deck tem o nível do kit:
  - um diagrama animado do método (FLUXO) que explica o caminho dos dados;
  - de 2 a 3 gráficos animados (BARRAS, ESCADA, PONTOS) com os números reais da fonte, quando a fonte tem números;
  - os passos revelam a fala, e os números do resultado principal contam.
  Um deck só de texto e imagens não passa. Também é BLOQUEANTE:
  - um gráfico cujo tipo não serve aos dados, como barras para uma etapa que se soma, que é caso da ESCADA;
  - um gráfico com números fora do `FACTS.md`;
  - um diagrama que não bate com o método da fonte.
  A exceção é o `docs/briefing.json` ter baixado a interatividade: então o critério segue o que ele pede.

- **Arco:** problema, objetivo, método, resultados, conclusões, limitações e próximos passos, nessa ordem, com os resultados ocupando mais slides.
- **Duração:** o número de slides combina com a duração do briefing, cerca de um por minuto.
- **Storyline:** os slides são os da `docs/STORYLINE.md`, na mesma ordem.
- **Figuras:** as de `docs/FIGURES.md` aparecem, e a licença está nas referências.

## Critérios das skills do projeto

As skills em `.claude/skills/deck-*` trazem as regras que os revisores do kit pegaram. Estes itens são **BLOQUEANTES**:
- **Leitura falsa noutra coluna:** uma leitura (callout) vale numa métrica e é falsa noutra coluna do mesmo slide, ou diz "melhor" ou "empate" contra os limiares do próprio deck (`deck-leituras-de-resultado`, regras 6 e 8).
- **Marcação do melhor valor errada:** o sentido da métrica foi ignorado, ou só o primeiro dos empatados recebeu a marca (`deck-leituras-de-resultado`, regra 2).
- **Forma do gráfico contra o dado:** barras truncadas, ou um donut para escores que não somam 1 (`deck-leituras-de-resultado`, regra 10).
- **Afirmação qualitativa ou conta derivada errada:** "diminui", "monotônico" ou a margem a − b não batem com a série da fonte (`deck-checklist-de-entrega`, regras 2 e 3).
- **Placeholder com cara de conteúdo**, ou o apresentador, a data e a instituição tirados do PDF quando quem apresenta pode ser outra pessoa (`deck-checklist-de-entrega`, regra 11; `deck-rodada-de-ajustes`, regra 3).
  - Um campo que só o autor sabe, deixado entre colchetes e listado no resumo, **não** é bloqueante: vai em "Precisa de você".
- **Separador decimal errado no português**, em qualquer lugar, inclusive gráficos, tooltips e tabelas (`deck-pt-br`, regra 1).
- **Termo em inglês sem itálico** no texto em português, quando o briefing pede o itálico (`deck-pt-br`, regra 3).
- **Componente que mostra só o resultado** num slide de mecanismo, quando o processo podia ser mostrado passo a passo (`deck-componentes-interativos`, regra 1).

## Formato da resposta

```
# Juiz

Resumo: <uma frase>. Bloqueantes: <n>. Nota média: <x,x> de 3.

## Bloqueantes
- s07: <o que está errado> -> <a correção exata>

## Por slide
| Slide | Nota | Correções |
|---|---|---|
| s01 | 3,0 | - |
| s07 | 1,5 | <correção> |

## Deck inteiro
- <observação> -> <correção>
```
