# ESTILO: o sistema visual e de texto do deck

Vem do kit da defesa NEXUS-GO (o `docs/DESIGN.md` dele e as regras de texto do `STORYLINE.md` e do `CONTEXT.md`), sem o conteúdo dele, mais as regras do orientador de 04/11/2026. Siga este arquivo, salvo o que o autor decidir no briefing (`docs/briefing.json`). Os padrões de cada tipo de slide estão em `exemplos/`.

O deck é uma fala científica, projetada numa sala e também aberta em notebooks. Ela precisa ser lida do fundo da sala e não pode ter cara de "slide de IA".

## 1. Conceito: três cores, três conceitos

- O deck tem três cores de conceito: `--c1` (azul), `--c2` (laranja) e `--c3` (verde). Ligue cada uma a um conceito central da fonte, como os dois insumos e o resultado, ou o problema, o método e o ganho. Registre a ligação em `docs/DECISIONS.md` e use cada cor só para o seu conceito.
- **Use a cor para:**
  - o marcador quadrado de um item de lista (`li.c1`);
  - a borda de uma frase `.accent`;
  - a barra de um gráfico que é daquele conceito.
- **Não use a cor para:**
  - o texto, que nunca sai numa cor de conceito: use `--ink`, `--ink-2` ou `--muted`;
  - decoração.
- **A régua de três cores** fica sob o título de cada slide (o motor a põe sozinho) e longa no título e no fechamento. Ela é a marca do deck.
- **Menos de três conceitos:** se a fonte tem só dois, use `--c1` e `--c2`, e o verde fica para o resultado ou some. Se não tem nenhum, ponha `class="c-off"` na seção, e os marcadores ficam em `--ink-2`.
- **Ressalva:** `--warn` (laranja escuro) marca ressalvas e limitações, nunca um conceito.

## 2. Tipografia (embutida, funciona sem internet)

| Papel | Fonte | Uso |
|---|---|---|
| Títulos | Bricolage Grotesque, 650 a 700 | títulos, frases de destaque, números grandes |
| Texto | Atkinson Hyperlegible Next, 400 e 700 | itens, rótulos, notas; feita para ser lida de longe |
| Dados | IBM Plex Mono, 400 e 500 | números de tabelas e gráficos, rótulos de parte, número do slide |

Escala na tela de 1600×900 (px): frase de destaque 76 · título 54 · lead 34 · corpo 30 · pequeno 24 · legenda 18. Nada abaixo de 18 px na tela, salvo as legendas de figura.

## 3. Grade e tipos de slide

- **Tela e cabeçalho:** a tela tem 1600×900 e margens de 88 px. O cabeçalho é o nome da parte (`data-part`), o título e a régua; o motor o monta a partir do `<h2 class="title">`.
- **Corpo:** `.bd` é uma grade de 12 colunas. Use `col-a` + `col-b` (5 + 7), `col-w` (12), `col-main` + `col-side` (8 + 4) ou `col-text` + `col-fig` (5 + 7).
- **Um tipo por slide**, sempre copiado de `exemplos/`: título, roteiro, bullets com figura, figura com máscara, frase de destaque, tabela, gráfico, questões de pesquisa, respostas, limitações, cards de próximos passos e agradecimento com referências.
- **Itens:** no máximo 4 por slide, ou 5 em limitações e próximos passos, com cerca de 12 palavras cada. Nada de parágrafo no slide: a narrativa vai nas notas.
- **Cards** (caixa com borda): só em próximos passos. A placa de figura é a única outra caixa.

## 4. Figuras

- **Placa:** toda figura da fonte fica numa placa (`figure > .plate > .fig > img`), clara nos dois temas, com alt real.
- **Legenda:** a legenda da fonte fica na `figcaption.cap` (`Fonte, Fig. 3, p. 7`). Ela é **oculta por padrão** (regra do orientador de 04/11), mas fica no HTML, porque é por ela que a checagem de figuras confere o uso de cada figura. Se o autor pedir no briefing para mostrar, ponha `class="cap-on"` na figura.
- **Partes da figura:** para mostrar uma figura por partes, use a máscara (exemplo 04). Nunca recorte o arquivo.
- **Resolução:** não amplie uma figura pequena além de 1,5×. Se ela fica ilegível no tamanho que cabe, dê a ela um slide inteiro ou deixe de fora e diga no resumo.

## 5. Texto

- **Título afirmativo:** o título diz a conclusão do slide ("A propagação fixa supera a aprendida"), não o assunto ("Resultados"). As exceções são o título, o roteiro, "Limitações", "Próximos passos" e os slides de abertura de uma parte.
- **Uma ideia por slide.** Se o slide tem duas, divida.
- **Um item por passo:** cada item da lista entra num clique (`class="f"` com `data-f` crescente). A figura entra no passo do item que fala dela.
- **Encurte em vez de diminuir:** se o texto não cabe, corte palavras ou divida o slide. Nunca reduza a fonte com estilo inline nem passe para `.sm` só para caber.
- **Negrito padronizado:** use `<b>` só no rótulo de um item ("**Dados:** ...") ou na linha do trabalho numa tabela. Em todos os itens que têm rótulo, ou em nenhum.
- **Idioma:**
  - **Português:** use a vírgula decimal (73,18), e os termos que ficam em inglês vão em itálico (`<i class="en">embedding</i>`), salvo siglas e nomes próprios.
  - **Inglês:** use o ponto decimal.
  - **Precisão:** a dos números é a da fonte.
- **Sem travessão** no slide e nas notas (use vírgula, dois-pontos ou parênteses), sem emoji e sem metacomentário ("este slide mostra", "como visto no PDF").
- **Citações:** "Silva et al. (2021)", nunca "[20]". As entradas ficam no slide de referências.
- **Notas:** de 2 a 4 frases em cada slide, com a página da fonte entre parênteses no fim: `(p. 12)` ou `(p. 12, Tab. 3)`.

## 6. Movimento

- **Passos:** aparecem com fade e sobem 8 px em 260 ms; voltar esconde na hora. O motor faz isso; não escreva animação.
- **Troca de slide:** cross-fade curto, sem 3D e sem zoom.
- **Movimento reduzido:** com `prefers-reduced-motion`, nada anima e cada slide mostra o estado final.

## 7. Gráficos

- **Forma:** um eixo por gráfico. Barras de até 24 px com 2 px de folga, linhas de 2 px.
- **Rótulos:** o texto nunca sai na cor de uma série; quem dá a identidade é a marca colorida ao lado.
- **Leitura:** cada marca tem um `<title>` (a dica ao passar o mouse), e os números ficam numa tabela em `<details><summary>Tabela</summary>`.
- **Separação:** validação e teste nunca no mesmo gráfico, e o subtítulo diz qual é.
- **Fonte dos números:** eles vêm da fonte e ficam registrados em `docs/FACTS.md`.

## 8. O que evitar

- fundo creme com detalhes em terracota, e degradê roxo-azul;
- emoji, ícone como marcador de seção e marcador numerado onde a ordem não importa;
- um card arredondado com sombra em volta de cada bloco, e texto do corpo centralizado;
- Inter ou Space Grotesk;
- ilustração genérica de "IA";
- texto nas cores das séries;
- número digitado à mão no gráfico que não esteja em `docs/FACTS.md`.
