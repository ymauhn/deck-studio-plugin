# Relatório de QA

## 0. Fonte usada

- Dissertação: `Downloads\Dissertacao_Yeonatan_pronto.zip` (projeto do Overleaf baixado em 15/10/2026), copiado para `source/thesis/`. Difere do zip de `ultimo_ajuste` apenas na §1.5 (Publications, com o CCIS aceito) e no `references.bib`.
- PDF de referência para a numeração impressa: `Downloads\Dissertacao_Yeonatan_pronto.pdf`, 145 páginas.
- `thesis_tables.json` e `numbering.json` regenerados do `.tex` novo, com conteúdo idêntico às cópias do kit (34 tabelas; 41 tabelas, 26 figuras e 52 equações numeradas).

## 1. Comparação com o repositório e com o CSV de 178 runs

Auditoria somente leitura, feita em 15/10/2026, com o script `qa/repo_audit.py`. As tabelas completas, valor por valor, estão em `qa/repo_audit_tables.md`, geradas pelo script e não digitadas. A referência é `thesis_tables.json`. A Tabela A.6 foi lida direto do `.tex`, porque o extrator a quebrava (ver 1.4).

### 1.1 Resumo

- **627 valores distintos da tese conferidos**, em 1.137 comparações valor × fonte:
  - late fusion com AVG;
  - coeficientes selecionados;
  - as três tabelas de teste (12 métodos × 6 métricas);
  - custo (Tabela 6.20 e Tabela A.6) e totais de custo do texto;
  - 8 tabelas de contexto de validação.
- **Resultado:**
  - 593 valores concordam exatamente com pelo menos uma fonte atual.
  - 16 concordam só por arredondamento (picos de 6.602,5 e 18.864,5 MiB impressos como 6.602 e 18.864; medianas 18,455 e 5,265 impressas 18,45 e 5,26; oito colunas AVG que a tese calcula sobre valores já arredondados).
  - **Nenhum valor diverge de todas as fontes.**
- **18 valores sem nenhuma fonte:** a linha *Naive baseline* das três tabelas de teste (6 métricas × 3 ontologias). Ela não aparece em nenhum `.md`/`.csv`/`.json`/`.txt`/`.log` do repositório nem das pastas de resultados da dissertação. Esses números não puderam ser conferidos.
- **59 divergências, todas contra o repositório.** A pasta `source/nexus-go/results/chapter6/` foi gerada em 05/08/2026 a partir da campanha de 96 runs, antes da atualização de CC. Diverge em três pontos:
  1. **Late fusion:** a coluna CC das 11 regras e, por consequência, as 11 médias AVG; além disso, o λ da regra combinada em CC (repo 0,5, tese 0,4).
  2. **Teste em CC:** NEXUS-GO/Fixed, NEXUS-GO/Early e NEXUS-GO/Late, nas 6 métricas.
  3. **Custo:** a Tabela 6.16 do repositório difere em 4 das 6 famílias e no total. Ela mistura as duas GPUs.

  Causa provável das três: o repositório não tem as runs de CC de 13 e 14/08 (α = 0,8 em T = 2, visão em T = 6, nova grade de early fusion) nem o novo ensemble de CC.
- **Contra as fontes atuais não há divergência:** o CSV de 170 runs, o `ensemble_cc_novo.log`, o `07_CONFRONTO_FINAL.md` pós-CC e o `ABLATIONS_summary.csv` batem com a tese. Os valores de BP e MF do repositório também batem integralmente.
- O `RESULTS.md` do repositório descreve a campanha antiga (96 runs, 121,5 GPU-horas, "0,32 h", "6,6 GB contra 21,2 GB"). **Sugestão: atualizar `results/chapter6/` e o `RESULTS.md` do repositório com a campanha pós-CC**, porque a dissertação cita o repositório como fonte das tabelas consolidadas. O deck mostra os números da dissertação.

### 1.2 As 8 runs de CC substituídas

O CSV não tem coluna de status. As 8 runs foram identificadas como configurações de CC rodadas com os campeões anteriores à atualização de CC e refeitas depois. Todas são mais antigas que as substitutas.

| Run excluída | Data | GPU | Substituída por |
|---|---|---|---|
| `cc_hybrid_add_gcn_mlp_h2_a07` | 03/08 | RTX | grade `cc_hybrid_*_mlp_h2_a08_*_emb{mlp,vision}` e `h6_a05_*` (14/08) |
| `cc_hybrid_add_gat_mlp_h2_a07` | 03/08 | RTX | idem |
| `cc_hybrid_concat_gcn_mlp_h2_a07` | 03/08 | RTX | idem |
| `cc_hybrid_concat_gat_mlp_h2_a07` | 03/08 | RTX | idem |
| `cc_hybrid_add_gcn_vision_h5_a05` | 04/08 | RTX | `cc_hybrid_add_*_vision_h6_a05_*` e `h2_a08_*` (14/08) |
| `cc_hybrid_add_gat_vision_h5_a05` | 04/08 | RTX | idem |
| `cc_fixed_vision_h5_a03` | 31/07 | GTX | varredura de α em T = 6 (14/08) |
| `cc_fixed_vision_h5_a07` | 01/08 | GTX | idem |

Com essas 8 runs excluídas, todos os totais da tese batem:
- famílias com 49 / 26 + 23 / 6 / 6 / 40 / 20 runs;
- 147 runs na RTX A5500 e 23 na GTX 1080 Ti;
- 136,3 GPU-horas no total, sendo 103,0 + 33,3 h;
- por rota: 52,9 h em 98 runs, 70,0 h em 12 e 13,4 h em 60.

As 8 runs somam 3,74 h. Nenhuma superaria um campeão de validação: a melhor tem wF<sub>max</sub> 0,6706, contra 0,6720 do campeão de early fusion em CC.

### 1.3 Convenções da comparação

- **Escala:** as métricas das fontes estão em fração e foram multiplicadas por 100. S<sub>min</sub> está em bits nas duas fontes.
- **GPU:** foi inferida por `sec_per_epoch`. As runs fixas de cabeça visual acima de 100 s/época são da GTX. Esse critério dá exatamente 23 e 147 runs.
- **Campeões:** para cada família, a run com maior wF<sub>max</sub> de validação. Dessas runs, comparam-se as métricas de teste.

### 1.4 Defeito encontrado no extrator do kit (corrigido)

`tools/extract_tables.py` lia as tabelas linha a linha e tirava todas as vírgulas de qualquer célula. Por isso:
- `cost_runs` (Tabela A.6) e `baselines_cost_coverage` (Tabela B.2) saíam com linhas partidas e com "230 [81250]" no lugar de "230 [81,250]";
- várias legendas de linha perdiam a vírgula ("Dropout prediction head").

A correção separa as linhas por `\\`, ignora comentários e só tira vírgulas de milhares. O resultado foi conferido contra a versão anterior: nenhum número de outra tabela mudou, só as duas tabelas acima e o texto das legendas. O deck lê a versão corrigida, gerada em `deck/build/thesis_tables.json`. A cópia do kit em `data/` ficou intacta.

## 2. Testes do deck (QA.md §2)

Rodada de 16/10/2026 sobre `deck/dist/nexus-go-defense.html` (2,91 MB), com `python -I qa/run_all.py` (resultado em `qa/results.json`): **16 de 16 checagens passam.**

| # | Checagem | Resultado |
|---|---|---|
| 1 | Carregamento sem erro de console | ok |
| 2 | 45 slides + 8 backups | ok |
| 3 | Passos de fragmento iguais ao STORYLINE; ida e volta restauram o estado | ok (143 passos) |
| 4 | Nada fora do canvas 1600×900, nenhum texto cortado | ok |
| 5 | Nenhuma caixa de texto sobreposta (fora dos componentes) | ok |
| 6 | As 26 figuras aparecem, todas com `alt` e carregadas | ok |
| 7 | Teclas →, ←, Space, PageDown, PageUp, Home, End, O, N, T, B e `#24` | ok |
| 8 | Contraste ≥ 4,5:1 no texto e ≥ 3:1 nas legendas, nos dois temas | ok |
| 9 | Movimento reduzido: mesmo estado final | ok |
| 10 | INT-PROP: T e α mudam as cores; Σ pesos = 1; iteração = forma fechada; nó isolado = α^T × norma inicial | ok (55 combinações de T e α) |
| 11 | INT-PIPE: cada rota acende os nós certos e esmaece o resto | ok |
| 12 | INT-TEST: rótulos de cada aba × métrica iguais ao JSON | ok (3 × 6 × 11) |
| 13 | INT-DEDUP: 0,81 / 0,19 (sum) e 0,46 / 0,54 (max) | ok |
| 14 | Todo gráfico tem tooltip e botão "Table" | ok (8 gráficos) |
| 15 | Tamanho < 12 MB | 2,91 MB |
| 16 | Offline: fontes embutidas e imagens renderizam com a rede bloqueada | ok |

Também: `qa/test_smoke.py` (motor; 53 slides, 143 passos, ida e volta com DOM idêntico em movimento reduzido) verde; screenshots de todos os slides nos dois temas em `qa/shots/light/` e `qa/shots/dark/`, contact sheets `qa/contact-light.png` e `qa/contact-dark.png`; tamanhos 1280×720, 1920×1080 e 390×844 em `qa/shots/sizes/` (sem rolagem horizontal; no celular o slide aparece reduzido em 16:9). Os agentes deixaram testes próprios dos componentes em `deck/dev/test_*.py`.

## 3. Auditoria de números (QA.md §3)

`python -I qa/audit_numbers.py` extrai todos os números do texto renderizado de cada slide no estado final (componentes incluídos) e procura cada um no `dissertation.tex`. Resultado em `qa/number_audit.md`: **nenhum número sem correspondência.** As exceções aceitas são as previstas no QA §3:
- dados de publicação (FACTS §1), anos das referências, números de camada, números de figura/tabela/equação, contagens pequenas;
- marcas de eixo dos gráficos (escala, não dado);
- os demos ilustrativos rotulados na tela (INT-PROP, INT-GBA, INT-MP, INT-PLM, INT-FOLD, INT-HERO);
- 0,81 do INT-DEDUP (4,00 / 4,95, o exemplo da própria dissertação).

A matemática renderizada como SVG não tem texto; os números dentro das fórmulas (3072, 1024, −7, …) foram conferidos lendo as fontes dos slides. Uma correção saiu da auditoria: S14 dizia "maximum near 800" (paráfrase do roteiro); agora diz "maximum 763 to 805", como na Tabela 4.4.

## 4. Inconsistências da dissertação (sugestões de correção; a tese não foi alterada)

1. **Fig. 5.6, caixa de late fusion.** Lista regras que não existem no texto ("average", "geometric mean", "validation-weighted", "stacked"); a §5.6.2 e a Tabela 6.14 definem onze regras (linear γ, máximo, mínimo, IC sigmoid, degree sigmoid, master equation e cinco stackings). Além disso, o fluxo desenha a late fusion consumindo a saída do head da early fusion, enquanto o texto (§5.6 e Fig. 5.10) diz que as duas rotas são alternativas. No deck a figura aparece recortada acima dessa caixa (botão "Dissertation figure" do S21), e a lista correta está no S29 (INT-RULES) e no S35. A caixa "stored embedding" tem um travessão.
2. **Nomes das regras:** a §5.6 chama três regras de *term-specific*, *protein-specific* e *combined weighting*; a Tabela 6.14 as chama de *IC sigmoid*, *Degree sigmoid* e *Master equation*.
3. **Ordem das métricas:** a §4.3 declara uma "ordem única" com S<sub>min</sub> em quarto; as Tabelas 6.17–6.19 põem S<sub>min</sub> por último. O deck segue as tabelas.
4. **Figs. 5.8 e 5.9:** rótulo "h = 6" onde a legenda e o texto usam T = 6 (h é o índice do passo, T o total).
5. **Fig. 5.7:** texto vazando das caixas; **Fig. 5.10:** "concat 4096 · block-wise average 3072" encosta na borda; **Fig. 6.1:** o rótulo "66.13, T = 2" fica sobre a curva de MF.
6. **Fig. 6.6 e Tabelas 6.23–6.25:** a rota se chama "Hybrid + vec."; no resto do texto é "Early fusion" / NEXUS-GO/Early.
7. **Travessões nos títulos internos** das Figs. 5.3, 5.5, 5.8 e 5.9 (regra de cópia do autor).
8. **Linha Naive baseline das Tabelas 6.17–6.19** sem fonte no repositório nem nas pastas de resultados (ver §1.1).
9. **Repositório desatualizado:** `results/chapter6/` e `RESULTS.md` descrevem a campanha antiga de 96 runs (ver §1.1).
10. **Funil de seleção (S30):** a deduplicação max não foi escolhida por validação (argumento analítico, §6.3.3), e o ConvNeXt-Tiny passou com margem de 0,57 pp mais a campanha VISAPP; o texto de §5.7 pode dar a entender que todas as etapas foram selecionadas em validação.
11. **CONTEXT.md do kit:** a nota sobre o CCIS "under review" ficou obsoleta (o `.tex` já diz "accepted"); o PDF tem 145 páginas, não 146.

## 5. Corte para 30 minutos

Os slides marcados "30-min cut: skip" no roteiro: **S09** (building blocks), **S10** (protein language models), **S23** (graph as an operator / INT-DEDUP), **S26** (GCN e GAT), **S28** (ProteinLoss) e **S33** (vision head, profundidade). Sem eles o deck tem 39 slides. Para pular durante a apresentação: digitar o número e `G` (por exemplo `11 G`).

## 6. Beamer (QA.md §5)

Gerado a partir do HTML por `beamer/tools/build.py`; detalhes em `beamer/LEIA-ME.md`.

| Checagem | Resultado |
|---|---|
| Compila duas vezes, sem erro | sim, XeLaTeX (MiKTeX), 321 páginas, 22 MB; versão com notas na segunda tela também |
| Overfull box acima de 10 pt | nenhum (0 no total) |
| Texto igual ao do HTML | 53/53 slides: todas as palavras do HTML aparecem na página final do slide (`qa/beamer_text.md`) |
| Números | nenhum número no PDF fora do slide HTML correspondente ou do `dissertation.tex` |
| Figuras | as 24 figuras raster por `\includegraphics` (`beamer/figures/`); as TikZ 2.4 e 2.5 e os 20 componentes como camada vetorial |
| Comparação visual | um painel HTML, Beamer e diferença por estado em `qa/beamer/`; as diferenças são de antialiasing e reamostragem |
| Links | todos os controles levam à página certa (conferido com pypdf: rotas do S21, sum/max do S23, 99 estados de T e α do S24, 18 estados do S38, volta pelo título) |
| Overleaf | `beamer/nexus-go-defense-overleaf.zip` compila sozinho numa pasta limpa |
