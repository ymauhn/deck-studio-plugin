---
name: deck-componentes-interativos
description: "Use ao decidir, escrever ou testar um componente interativo ou animado (deck/src/components/) de um deck do Deck Studio: quando usar, contrato, dados do FACTS, sincronia com os passos e teste isolado."
---

# Componentes interativos e animados

Neste projeto, o FLUXO, as BARRAS, a ESCADA, os PONTOS e o NUMERO já existem em `deck/src/components/`, cada um com o exemplo dele na skill criar-apresentacao (exemplos 13 a 18). Escolha primeiro um deles, e o slide só traz `data-component` e `data-opts`. Escreva um componente novo só quando nenhum serve (um parâmetro que o público mexe, o exemplo numérico do texto, regra 2 e 3). O studio pede a aprovação do autor para gravar em `deck/src/components/`.

## Quando usar
1. Todo slide com mecanismo ou algoritmo ganha um componente que mostra o PROCESSO passo a passo (votos que chegam um por vez, barras que sobem), e não só o resultado. Foi o que o dono mais elogiou ("MUITO LEGAL!") (p01:31-35,67).
2. Quando o método tem um parâmetro central, o deck ganha um interativo-chave: o público mexe no parâmetro central do método (slider, mais um play que varre o intervalo) e vê o efeito, inclusive o caso-limite que o artigo ressalva. Ao lado ficam a fórmula fechada e os valores lidos (INT:148-169; DEC:79).
3. O exemplo numérico do próprio texto vira um interativo pequeno, com toggle, e os estados mostram os números do artigo (INT:137-146; p01:252).
4. Se o método tem um pipeline, o diagrama dele é o único momento orquestrado: um SVG nas cores semânticas, revelado ramo por ramo, com botões de rota que apagam o resto e um toggle para a figura original (INT:111-135).
5. O diagrama didático de conceito mostra uma ideia por passo, com valores ilustrativos fixos e ROTULADOS na tela ("esquemático, fora de escala") (INT:36-82; DEC:41,47).

## Contrato
6. O componente se registra como `COMPONENTS.NOME = (el, opts) => ({ step(n), pause() })` (e, se precisar, play(), state() e theme()). O step(n) define o estado inteiro e é idempotente, também ao voltar. O render(t) é determinístico. O state() devolve JSON simples para os testes (INT:3-17; COMP:23-38).
7. Cada componente é um arquivo `deck/src/components/<nome>.js` (o build junta todos, em ordem de nome), com o CSS de seletores prefixados num `<nome>.css` ao lado. Os helpers ficam em `_base.js` (K.svg, K.fmt, K.count, K.ticks, K.tips, K.table), e o estilo é copiado de um componente pronto (COMP:3-19).
8. Os dados vêm sempre de data-opts, com os números do `docs/FACTS.md` copiados exatos (a auditoria de números confere o que aparece). Nada de Math.random sem semente (COMP:60-62; INT:28-34).
9. A especificação escreve a fórmula exata da fonte e uma asserção dentro do componente (ex.: os pesos somam 1). Se a asserção falha, vira um erro de console que o teste pega (INT:148-169; DEC:45).

## Sincronia e controles
10. Um item por passo vale também dentro do componente. Mapeie o passo do slide para o passo do componente pelo campo `passo` de cada item em data-opts, sem fixar isso no código (DEC:168-169,188; p01:73).
11. Os controles são elementos reais (button, input range, select), com rótulo visível, id estável, aria-pressed e foco visível, e clicar neles não avança o slide. O controle só fica livre depois do último passo do slide (COMP:47-50; p01:305).
12. A animação é rápida: no NEXUS-GO o dono aprovou o ciclo do dobramento depois de cair de 12 s para cerca de 8 s; use isso como teto de referência, não como valor fixo. Com prefers-reduced-motion, o componente vai ao estado final e os controles continuam funcionando (p01:3-15; DES:122-132).
13. Quando o autor pede "outro estilo", implemente a alternativa atrás de uma opção (data-opts look=...) e mantenha a antiga como padrão. Mostre como alternar e ofereça uma terceira variante (p01:15-27).
14. O texto dentro do SVG segue as mesmas regras do slide: itálico no termo estrangeiro e o separador decimal do idioma (p01:137; DEC:187).

## Teste
15. Teste no próprio deck, no tamanho do canvas (1600x900): `mcp__plugin_deck-studio_deck__screenshot_slide` em cada passo e `mcp__plugin_deck-studio_deck__run_qa` (a checagem 19 confere que cada componente desenhou), erros de console capturados e screenshot de cada passo nos dois temas, olhados um a um. Nada pode sair do contêiner, e avançar e voltar deve dar o mesmo DOM (COMP:68-83).
16. O teste de valores lê os rótulos renderizados e compara com o JSON (QA:41-42).
17. Para PDF ou Beamer: cada estado vira um overlay, os botões viram links para os estados e a animação vira quadros. O primeiro quadro é um estado válido (DEC:58-63; p01:356-386).

Evidência: as regras foram mineradas das falas do autor do kit NEXUS-GO nas sessões do deck, das rodadas de crítica e dos documentos do kit; os códigos entre parênteses (p01, wfXXX, DEC, DES, INT, QA, COMP, STO, FIG, PED) apontam para essas fontes, que ficam fora do projeto. O NEXUS-GO aparece só como exemplo.
