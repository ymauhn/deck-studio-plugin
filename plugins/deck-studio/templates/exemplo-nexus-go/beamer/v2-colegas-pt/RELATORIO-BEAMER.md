# Anotações do orientador no Beamer em português (04/11)

**PDF novo:** `beamer/v2-colegas-pt/nexus-go-v2-pt.pdf`
- 90 páginas;
- 64 frames, mais 2 de backup.

## Fonte

O PDF anotado (`Downloads/Defesa_de_Mestrado (anotacoes).pdf`) saiu desta `.tex`.
- Os dois PDFs têm 79 páginas. O atual já tinha 79, não 58.
- O texto das 79 páginas é idêntico. As únicas diferenças vêm de glifos de delimitadores matemáticos, porque o anotado foi compilado no Overleaf (TeX Live) e o local no MiKTeX.

## O que mudou nos arquivos

- **Backup antes de editar:** `beamer/v2-colegas-pt.backup-2026-11-04/`, com o `nexus-go-v2-pt-overleaf.zip` antigo dentro.
- **Arquivos editados:**
  - `nexus-go-v2-pt.tex`;
  - `gen_pt.py`, só o gerador em português; os geradores em inglês não mudaram;
  - `tables.tex` e `gains.tex`, regenerados pelo `gen_pt.py`;
  - `LEIA-ME.md`;
  - o zip do Overleaf.
- **Script das edições:** `C:\Users\voce\nexusgo-deck-sessao\work\patch_beamer.py`. Ele lê o backup e falha se algum trecho não aparecer exatamente uma vez.

## Compilação

- **Comando:** `latexmk` com o perl do Git só no PATH do processo (`C:\Program Files\Git\usr\bin`). Rodou pdfLaTeX, BibTeX e pdfLaTeX duas vezes.
- **Citações:** nenhum `[?]` nem `??` no PDF, que tem 22 referências.
- **Avisos:** nenhum overfull hbox. Há um único overfull vbox de 0,22 pt, que não se vê.

## Decisões do dono que segui

- **Fundamentação:** continua no lugar.
- **Itálico:** em todos os termos em inglês. Isso inclui as tabelas geradas (*Baseline*, *Stacking*, *gradient boosting*).
- **Questões de pesquisa:** texto completo, uma por passo.
- **Pontos sem anotação neste PDF:** "um item por passo" nos outros slides e a remoção de legendas não foram aplicados. O orientador não os pediu no Beamer, e as legendas numeradas são o padrão deste deck acadêmico.

## Anotações (59)

As páginas são as do PDF anotado.

| # | Página | Anotação | Status | O que foi feito e por quê |
|---|---|---|---|---|
| 1 | p4 | "embeddings": itálico | Feito | |
| 2 | p5 | "Gene Ontology:": itálico e negrito | Feito | "True Path Rule:" recebeu o mesmo tratamento, por consistência. |
| 3 | p5 | "Tarefa:": negrito | Feito | |
| 4 | p6 | "Redes de interação de proteínas (PPI):": negrito | Feito | |
| 5 | p7 | "Gene Ontology": itálico | Feito | |
| 6 | p8 | Deixar só o objetivo geral | Feito | Os objetivos específicos saíram. |
| 7 | p9 | Questões de pesquisa inteiras, mesmo em vários slides | Feito | Dois frames, QP1–4 e QP5–7, com uma questão por passo. O texto é a tradução fiel da Seção 1.3. |
| 8 | p10 | Cortar a Fundamentação | Não feito | Por decisão do dono, a Fundamentação fica no lugar. |
| 9 | p11 | "oversmoothing": itálico | Feito | |
| 10 | p12 | "Aqui: 2 camadas…": o que é "aqui"? | Feito | Virou "**Configuração neste trabalho:** 2 camadas de largura 1.024; na GAT, 4 cabeças de atenção…". |
| 11 | p13 | "congelado" em vermelho: por quê? | Feito | O `\alert` saiu, e o texto está na cor normal. |
| 12 | p13 | "embedding": itálico | Feito | "transformer" também ficou em itálico. |
| 13 | p15 | "embeddings": itálico | Feito | Também "*Transformers*" no título e nas caixas, e "*transformer*" na tabela da p16. |
| 14 | p17 | "Proposta:": negrito | Feito | |
| 15 | p17 | "embeddings": itálico | Feito | |
| 16 | p17 | "embedding": itálico | Feito | |
| 17 | p20 | "Graus:": negrito | Feito | |
| 18 | p21 | "Isoladas:": negrito | Feito | |
| 19 | p22 | Remover "(sem a raiz)," | Feito | |
| 20 | p22 | Remover "(bits, menor é melhor)," | Feito | |
| 21 | p23 | "Semente única:": negrito | Feito | O mesmo rótulo ficou em negrito também em "Limitações". |
| 22 | p24 | "Todo modelo:": negrito | Feito | |
| 23 | p24 | "Geração 1:": negrito | Feito | |
| 24 | p24 | "Cerca de um terço isolado" como subitem da Geração 1 | Feito | |
| 25 | p24 | "Geração 2 (NEXUS-GO):": negrito | Feito | |
| 26 | p25 | "Entrada:": negrito | Feito | |
| 27 | p25 | "Pooling:": negrito | Feito | Em negrito e itálico, junto com *raw*, *max* e *avg*. |
| 28 | p25 | "rota vetorial:" num item próprio, em negrito | Feito | |
| 29 | p25 | "Rota visual:": negrito | Feito | |
| 30 | p25 | Remover "externas \|vi − vj\|," se não couber | Feito | Agora diz "matriz de diferenças 224 × 224, …". |
| 31 | p25 | "Piso:": negrito | Feito | |
| 32 | p25 | "baseline": itálico | Feito | |
| 33 | p26 | "Requisito…" em vermelho | Feito | O `\alert` saiu. Ficou "**Requisito:** uma representação…", com o rótulo em negrito, como nos outros. |
| 34 | p27 | Título "Geração 2: NEXUS-GO" | Feito | Vale para os 5 passos do frame. |
| 35 | p33 | Tirar o negrito de "max," | Feito | "*cache*" também ficou em itálico. |
| 36 | p35 | "Backbones:": negrito | Feito | Em negrito e itálico. "*dropout*" também ficou em itálico. |
| 37 | p35 | Remover "Cuidado: a adjacência entre pixels…" | Feito | |
| 38 | p36 | Os 5,47 p.p. são resultado e deveriam estar nos resultados | Feito | O item saiu de ProteinLoss. O número já estava em "A Geração 1 Resolve Três Escolhas" e continua lá, agora na tabela. |
| 39 | p37 | "Onze regras tardias:": negrito | Feito | |
| 40 | p37 | "(stacking)": itálico | Feito | |
| 41 | p40 | "Baseline": itálico | Feito | |
| 42 | p40 | "wFmax médio na validação": colocar em tabela | Feito | Virou a tabela "Escolha / Opção / wFmax médio", com o vencedor (44,51) em negrito. Os números são os mesmos do slide anterior. |
| 43 | p44 | Tirar o negrito de "fixa" | Feito | |
| 44 | p44 | Tirar o negrito de "a GCN:" | Feito | |
| 45 | p47 | Tabela 6: melhor resultado em negrito | Feito | No `gen_pt.py`, a linha "Fusão precoce, Vetorial" ficou em negrito: é a melhor em BP, CC, MF e na média. O gerador em inglês já marcava essas células com chaves. |
| 46 | p49 | "Só ProtT5": falta a propagação via GNN? | Feito | O gráfico ganhou a barra GNN (63,32), entre Só ProtT5 e Fixed. O valor sai da tabela gerada, não foi digitado. A legenda explica que a GNN sozinha fica abaixo do Só ProtT5 por causa de MF. |
| 47 | p52 | Tirar o negrito de "baseline ProtT5" | Feito | Ficou sem negrito, com *baseline* em itálico. |
| 48 | p53 | "baseline": itálico | Feito | |
| 49 | p55 | "o baseline": itálico | Feito | |
| 50 | p56 | Tirar o negrito de "Primeira Geração," | Feito | |
| 51 | p56 | "baseline": itálico | Feito | |
| 52 | p57 | "baseline": itálico | Feito | |
| 53 | p59 | "o baseline": itálico | Feito | |
| 54 | p60 | "baseline": itálico | Feito | Vale também para as tabelas de teste ("*Baseline* ingênuo", "*Baseline* ProtT5"). |
| 55 | p63 | "Fixa + vetorial:": negrito | Feito | |
| 56 | p63 | "Só a GCN:": negrito | Feito | |
| 57 | p63 | "Iguala ou supera…" em vermelho | Feito | O `\alert` saiu. |
| 58 | p67 | Pergunta completa e resposta mais longa, mesmo em mais slides | Feito | Quatro frames, QP1–2, QP3–4, QP5–6 e QP7, com uma questão por passo: a pergunta inteira em itálico e uma resposta expandida a partir da Seção 7.1. Todos os números estão na Seção 7.1 da dissertação. |
| 59 | p69 | "Baselines": itálico | Feito | |

**Resultado:** das 59 anotações, 58 foram feitas. A que não foi feita é a #8, cortar a Fundamentação, por decisão do dono.

## Efeitos colaterais

- **Paginação e narração:** o PDF passou de 79 para 90 páginas. A página N não corresponde mais à página N do deck em inglês, e a narração em português, que seguia essa numeração, ficou desalinhada. O deck em inglês (`v2-colegas`) não foi alterado.
- **Zip do Overleaf:** `beamer/nexus-go-v2-pt-overleaf.zip` foi refeito com a mesma lista de arquivos de antes. O zip antigo está no backup.
