---
name: criar-apresentacao
description: Cria a apresentação inteira a partir dos materiais deste projeto (PDFs, notas e imagens em context/), com o método do kit NEXUS-GO, em fases. Faz um briefing com o autor, levanta os fatos e as figuras, escreve a storyline e espera a aprovação, faz os slides a partir dos exemplos por tipo, passa pelo QA e pelo juiz até ficar verde, e entrega o resumo. Use no primeiro pedido de um projeto novo, ou quando o autor pedir para refazer a apresentação.
---

# Criar a apresentação, no nível do kit

Esta skill reproduz o método do kit da defesa NEXUS-GO. O deck nasce de uma especificação em `docs/`, não direto em HTML. Siga as fases na ordem. As regras visuais e de texto estão em [ESTILO.md](ESTILO.md), e os padrões de slide em [exemplos/](exemplos/), um arquivo por tipo.

Seis skills do projeto trazem as decisões que deram certo no deck do kit, e você as lê na fase indicada (pela ferramenta Skill, como `deck-studio:<nome>`):
- `deck-leituras-de-resultado` e `deck-componentes-interativos`: na storyline (fase C) e nos slides (fase D);
- `deck-pt-br`: nos slides (fase D), quando os slides são em português;
- `deck-roteiro-de-fala`: no roteiro de narração (fase F);
- `deck-checklist-de-entrega`: antes do resumo (fase G);
- `deck-rodada-de-ajustes`: no resumo (o formato do relatório) e em toda correção que o autor mandar depois.

O autor fala com você em português. Escreva toda mensagem a ele em português do Brasil, curto, inclusive as notas curtas entre as ferramentas, mesmo quando a fonte está em inglês.

## A. Briefing: uma mensagem, e espere

1. Leia por cima o que há em `context/`:
   - o `info.json` de cada PDF extraído (título, autores, páginas, figuras com legenda);
   - as notas `.md` e `.txt`;
   - os nomes das imagens.
   Não leia o texto inteiro ainda.
2. Preencha `docs/briefing.json`, a partir do modelo que já está lá, com o padrão que os materiais sugerem para cada decisão. O que o primeiro pedido traz em "Instruções do autor" e o que as notas pedem valem mais que o padrão.
3. Mande **uma única mensagem** com as decisões numeradas, cada uma com o padrão já marcado, para o autor mudar só o que quiser:
   1. duração (e se quer uma versão curta);
   2. evento e público;
   3. idioma dos slides e da fala, números com vírgula decimal, itálico nos termos em inglês;
   4. formatos: HTML e PDF; Beamer gerado do HTML; ou Beamer no formato dos colegas (Madrid);
   5. narração: só as notas, ou também o `roteiro.md` (texto por passo, para gravar);
   6. identidade visual: o tema do kit com 2 ou 3 cores ligadas aos conceitos do material (diga quais, por exemplo "azul = método, laranja = dados, verde = resultado"), ou o Beamer dos colegas;
   7. interatividade: o padrão é o nível do kit, com 1 diagrama animado do método (FLUXO) e de 2 a 3 gráficos animados com números da fonte (BARRAS, ESCADA, PONTOS), mais números que contam; o autor pode baixar para menos, ou para só passos;
   8. figuras: quais entram, e se a legenda "Fonte: Fig. n" aparece (o padrão é oculta, com a fonte nas notas);
   9. fatos: só os números da fonte, ou também números externos citados (só com autorização);
   10. paradas de revisão: depois da storyline e no fim (padrão), ou só no fim.
4. **Termine aqui o pedido** e espere a resposta. Exceções: as instruções do autor já dizem "não pergunte", ou a resposta já veio ("pode seguir", ou as mudanças). Então marque `"confirmado": true` no `briefing.json`, registre as escolhas em `docs/DECISIONS.md` e siga.

## B. Fatos e figuras

1. Leia a fonte: o `texto.md` de cada PDF em `context/<pasta>/` e as notas. Numa tese longa, comece pelo resumo, pela introdução e pelas conclusões, e use o Grep no `texto.md` para achar o resto. Não use busca semântica.
2. Escreva `docs/FACTS.md` a partir de `docs/FACTS.template.md`:
   - cada número que o deck pode mostrar, com a página e o trecho;
   - os valores derivados, com a conta;
   - as pessoas, a instituição e o evento.
   Um número que não está aqui nem na fonte não entra no deck.
3. Escreva `docs/FIGURES.md` a partir de `docs/FIGURES.template.md`: as figuras que sustentam a fala, cada uma com o rótulo ("Fig. 3"), o arquivo, a página, o slide, a máscara se a figura vai por partes, o alt e a licença da fonte. Olhe a página de cada figura com a ferramenta Read antes de escolher.

## C. Storyline, e a parada para o autor

Leia antes `deck-leituras-de-resultado` e `deck-componentes-interativos`.

1. Escreva `docs/STORYLINE.md` a partir de `docs/STORYLINE.template.md`, slide a slide, com estes campos:
   - um id estável (`s01`, `s02`... e `b1` para os de reserva);
   - o título afirmativo;
   - o texto na tela;
   - o visual;
   - o tipo, ou seja, o exemplo que o slide copia;
   - os passos (`F1–F3` ou `nenhum`);
   - as notas;
   - a fonte com a página;
   - o corte da versão curta.
2. **Tamanho:** cerca de um slide por minuto de fala.
3. **Arco:**
   - título e roteiro;
   - o problema e por que importa;
   - o objetivo ou as questões de pesquisa;
   - o método;
   - os resultados, que levam mais slides;
   - as conclusões ou respostas;
   - as limitações;
   - os próximos passos;
   - o agradecimento;
   - as referências como reserva.
4. **Visuais:** o deck tem o nível do kit, não só texto e imagens. A storyline marca no campo "visual" de cada slide o componente que ele usa, e tem, salvo se o briefing baixou:
   - pelo menos 1 diagrama animado do método (exemplo 13, FLUXO), com rotas quando o trabalho tem variantes;
   - de 2 a 3 gráficos animados com números reais da fonte (14 BARRAS, 15 ESCADA, 16 PONTOS), escolhidos pelo "quando usar" de cada exemplo; cada valor vem do `FACTS.md`;
   - números que contam (18) no resultado principal, e tabelas que revelam linha por linha (17) quando a fala percorre uma tabela.
   Sem números na fonte, os gráficos ficam de fora, e o `briefing.json` diz isso.
5. **Cores:** registre em `docs/DECISIONS.md` qual cor (`--c1`, `--c2`, `--c3`) é qual conceito.
6. Se o briefing tem a parada da storyline, mande ao autor a lista numerada de títulos, com os passos de cada slide, e **termine o pedido**. Ao voltar, aplique o que ele mudou na `STORYLINE.md` antes de seguir.

## D. Slides, parte por parte

Com os slides em português, leia antes `deck-pt-br`.

1. Para cada slide da storyline:
   - abra o exemplo do tipo dele em `exemplos/`;
   - copie a estrutura e as classes;
   - troque os colchetes pelo conteúdo da storyline.
   Não invente classe nova: o que não cabe num exemplo é sinal de que o slide tem ideia demais.
   **Componentes** (exemplos 13 a 18): o FLUXO, as BARRAS, a ESCADA, os PONTOS e o NUMERO já estão no deck (`deck/src/components/`). Você não escreve JavaScript nem SVG para eles: o slide só traz `data-component` e `data-opts`, com os números do `FACTS.md` copiados exatos (ponto decimal no JSON; o componente escreve a vírgula). Confira com `mcp__plugin_deck-studio_deck__screenshot_slide` no último passo, onde tudo já entrou.
2. **Arquivos:** `deck/src/slides/00-titulo.html`, depois um arquivo por parte (`01-problema.html`, `02-metodo.html`...). Cada `<section>` tem o `id` da storyline e o `data-part` com o nome da parte. Os de reserva levam `class="slide backup"` e ficam no último arquivo.
3. **Figuras:** use `mcp__plugin_deck-studio_deck__add_image` com o arquivo da fonte em `context/`, e escreva o alt e a legenda da fonte, que fica oculta, como o exemplo mostra.
4. **Conferência:** depois de cada parte, rode `mcp__plugin_deck-studio_deck__screenshot_slide` e `mcp__plugin_deck-studio_deck__check_slide` nos slides novos e corrija o que transborda, encurtando o texto.

## E. QA e juiz, até ficar verde

1. Rode `mcp__plugin_deck-studio_deck__run_qa`, que faz o build limpo, as checagens, a auditoria de números e a contact sheet. Corrija cada FAIL e cada UNMATCHED, até tudo passar:
   - os passos batem com a storyline;
   - nada transborda nem se sobrepõe;
   - as figuras de `FIGURES.md` estão nos slides;
   - há contraste nos dois temas;
   - cada slide tem notas terminando com a página;
   - não há travessão;
   - o deck tem os visuais do briefing (o diagrama e os gráficos);
   - todo número tem fonte.
2. Chame o subagente `deck-studio:juiz` (ferramenta Agent). Ele não fez o deck, só lê o projeto e segue `qa/RUBRICA.md`; grave o relatório dele, como veio, em `qa/JUIZ.md`. Corrija todo item **BLOQUEANTE**, e os outros quando forem baratos. Rode `run_qa` e o juiz de novo, no máximo três rodadas.
3. O que o juiz pediu e você não fez vai para `docs/DECISIONS.md`, com o motivo.

## F. Opcionais do briefing

- **Beamer no formato dos colegas:** `beamer/apresentacao/apresentacao.tex` já é o modelo deles (tema Madrid, barra de título azul-marinho, rodapé em três azuis, legendas numeradas). Escreva nele os mesmos slides da storyline, um `frame` por slide, com `\section` por parte. Compile com `mcp__plugin_deck-studio_deck__compile_beamer` até 0 erros e nenhum Overfull.
- **Roteiro de narração** (`roteiro.md`, só texto; leia antes `deck-roteiro-de-fala`): um `## s07 · Título` por slide, e um parágrafo `[0]`, `[1]`... por estado de passo, com o que dizer quando o slide aparece e a cada clique. Todo número vem de `docs/FACTS.md`. Mire em cerca de 130 palavras por minuto da duração do briefing.

## G. Resumo

Antes, passe pela `deck-checklist-de-entrega`. O resumo segue o formato de relatório da `deck-rodada-de-ajustes` (regra 15).

Termine com um resumo curto, em português:
- quantos slides e partes;
- as cores de conceito;
- o resultado do QA (as checagens e os números sem fonte);
- os itens do juiz que ficaram, se ficou algum;
- o que o autor deve conferir: os números marcados, os colchetes que a fonte não preencheu, como `[evento e data]`, e as figuras deixadas de fora.

Complete o `docs/DECISIONS.md`.
