<!-- gerado por audit.py; não editar à mão -->
Valores distintos da tese conferidos: **627**. Melhor resultado em pelo menos uma fonte: concorda 593, só arredondamento 16, diverge em todas as fontes 0, sem fonte 18.

- sem confirmação (ausente): Teste BP (tab:confronto_bp) / Naive baseline | fmax
- sem confirmação (ausente): Teste BP (tab:confronto_bp) / Naive baseline | fmax_star
- sem confirmação (ausente): Teste BP (tab:confronto_bp) / Naive baseline | wfmax
- sem confirmação (ausente): Teste BP (tab:confronto_bp) / Naive baseline | auprc
- sem confirmação (ausente): Teste BP (tab:confronto_bp) / Naive baseline | iauprc
- sem confirmação (ausente): Teste BP (tab:confronto_bp) / Naive baseline | smin
- sem confirmação (ausente): Teste CC (tab:confronto_cc) / Naive baseline | fmax
- sem confirmação (ausente): Teste CC (tab:confronto_cc) / Naive baseline | fmax_star
- sem confirmação (ausente): Teste CC (tab:confronto_cc) / Naive baseline | wfmax
- sem confirmação (ausente): Teste CC (tab:confronto_cc) / Naive baseline | auprc
- sem confirmação (ausente): Teste CC (tab:confronto_cc) / Naive baseline | iauprc
- sem confirmação (ausente): Teste CC (tab:confronto_cc) / Naive baseline | smin
- sem confirmação (ausente): Teste MF (tab:confronto_mf) / Naive baseline | fmax
- sem confirmação (ausente): Teste MF (tab:confronto_mf) / Naive baseline | fmax_star
- sem confirmação (ausente): Teste MF (tab:confronto_mf) / Naive baseline | wfmax
- sem confirmação (ausente): Teste MF (tab:confronto_mf) / Naive baseline | auprc
- sem confirmação (ausente): Teste MF (tab:confronto_mf) / Naive baseline | iauprc
- sem confirmação (ausente): Teste MF (tab:confronto_mf) / Naive baseline | smin

### Contagem por fonte

| Fonte | comparações | concorda | arredondamento | diverge | ausente |
|---|---|---|---|---|---|
| CSV 170 | 491 | 369 | 14 | 0 | 108 |
| CSV 170 (RTX) | 38 | 36 | 2 | 0 | 0 |
| atual | 18 | 18 | 0 | 0 | 0 |
| atual (log CC novo) | 11 | 11 | 0 | 0 | 0 |
| log CC novo | 6 | 1 | 0 | 0 | 5 |
| média atual (BP/MF repo + CC log) | 11 | 11 | 0 | 0 | 0 |
| média repo | 11 | 0 | 0 | 11 | 0 |
| pós-CC 07 | 216 | 198 | 0 | 0 | 18 |
| repo 01 | 18 | 17 | 0 | 1 | 0 |
| repo 01 Tab. 6.13 | 33 | 22 | 0 | 11 | 0 |
| repo 01 Tab. 6.13 (teste) | 12 | 2 | 0 | 0 | 10 |
| repo 01 Tab. 6.16 | 38 | 14 | 0 | 18 | 6 |
| repo 07 | 216 | 180 | 0 | 18 | 18 |
| repo ABLATIONS_summary.csv | 18 | 18 | 0 | 0 | 0 |
| **Total** | **1137** | **897** | **16** | **59** | **165** |

### 1.3 Late fusion (tab:late_fusion, wFmax de validação, %)

Fonte "repo": `source/nexus-go/results/chapter6/01_TABELAS_dedupmax.md`, Tabela 6.13 (campanha de 96 runs). Fonte "atual": BP e MF do mesmo arquivo do repo; CC de `late_fusion/ensemble_cc_novo.log` (bloco RESUMO). AVG recalculado como média simples de BP, CC e MF com os valores de 4 casas da fonte. Legenda: `=` concorda a 2 casas, `≈` difere só por arredondamento, `≠` diverge, `-` ausente.

| Regra | BP tese | BP repo | CC tese | CC repo | CC log novo | MF tese | MF repo | AVG tese | AVG repo | AVG atual |
|---|---|---|---|---|---|---|---|---|---|---|
| Linear interpolation (γ) | 57.96 | 57.96 = | 68.79 | 68.49 ≠ | 68.79 = | 74.44 | 74.44 = | 67.06 | 66.96 ≠ | 67.06 = |
| Maximum | 57.35 | 57.35 = | 67.79 | 67.57 ≠ | 67.79 = | 72.59 | 72.59 = | 65.91 | 65.84 ≠ | 65.91 = |
| Minimum | 56.38 | 56.38 = | 68.09 | 67.84 ≠ | 68.09 = | 72.69 | 72.69 = | 65.72 | 65.64 ≠ | 65.72 = |
| IC sigmoid | 57.03 | 57.03 = | 67.57 | 67.33 ≠ | 67.57 = | 73.88 | 73.88 = | 66.16 | 66.08 ≠ | 66.16 = |
| Degree sigmoid | 57.02 | 57.02 = | 67.76 | 67.26 ≠ | 67.76 = | 72.42 | 72.42 = | 65.73 | 65.57 ≠ | 65.73 = |
| Master equation | 57.42 | 57.42 = | 68.10 | 67.75 ≠ | 68.10 = | 73.93 | 73.93 = | 66.48 | 66.37 ≠ | 66.48 = |
| Stacking (decision tree) | 56.22 | 56.22 = | 67.35 | 67.77 ≠ | 67.35 = | 73.76 | 73.76 = | 65.78 | 65.92 ≠ | 65.78 = |
| Stacking (logistic regression) | 57.53 | 57.53 = | 68.50 | 68.07 ≠ | 68.50 = | 72.47 | 72.47 = | 66.17 | 66.02 ≠ | 66.17 = |
| Stacking (MLP) | 56.92 | 56.92 = | 68.12 | 68.08 ≠ | 68.12 = | 73.92 | 73.92 = | 66.32 | 66.31 ≠ | 66.32 = |
| Stacking (random forest) | 56.65 | 56.65 = | 68.21 | 68.10 ≠ | 68.21 = | 74.14 | 74.14 = | 66.33 | 66.30 ≠ | 66.33 = |
| Stacking (gradient boosting) | 56.67 | 56.67 = | 67.72 | 66.85 ≠ | 67.72 = | 74.18 | 74.18 = | 66.19 | 65.90 ≠ | 66.19 = |

Consistência interna: `resultados_novos_pos_CC_update/tabelas/01_TABELAS_dedupmax.md` (Tabela 6.13) reproduz exatamente o log de CC e os valores BP/MF do repo, em validação e teste.

Coeficientes selecionados (tab:ape_fusao_sel): γ, IC_thr, κ_IC, d_thr, κ_deg, λ (λ = `alpha` da regra mestra).

| Ont | Fonte | tese | fonte | status |
|---|---|---|---|---|
| BP | repo 01 | 0.5, 1.1, 1, 3, 0.25, 0.5 | 0.5, 1.1, 1, 3, 0.25, 0.5 | = = = = = = |
| BP | atual | 0.5, 1.1, 1, 3, 0.25, 0.5 | 0.5, 1.1, 1, 3, 0.25, 0.5 | = = = = = = |
| CC | repo 01 | 0.55, 0.4, 1, 14, 0.25, 0.4 | 0.55, 0.4, 1, 14, 0.25, 0.5 | = = = = = ≠ |
| CC | atual | 0.55, 0.4, 1, 14, 0.25, 0.4 | 0.55, 0.4, 1, 14, 0.25, 0.4 | = = = = = = |
| MF | repo 01 | 0.55, 0.4, 1, 28, 0.25, 0.9 | 0.55, 0.4, 1, 28, 0.25, 0.9 | = = = = = = |
| MF | atual | 0.55, 0.4, 1, 28, 0.25, 0.9 | 0.55, 0.4, 1, 28, 0.25, 0.9 | = = = = = = |

### 1.4 Tabelas de teste (tab:confronto_bp/cc/mf)

Fontes: "repo 07" = `source/nexus-go/results/chapter6/07_CONFRONTO_FINAL.md` (seção TESTE); "pós-CC 07" = `resultados_novos_pos_CC_update/tabelas/07_CONFRONTO_FINAL.md` (suplementar, mesma pasta do CSV); "CSV" = linha de teste do CSV de 170 runs para o campeão escolhido pelo wFmax de validação (First Generation: `results/ppi_only/ABLATIONS_summary.csv` do repo; Late: só wFmax de teste, do log de CC e da Tabela 6.13 do repo). Métricas ×100, Smin em bits. Cada célula mostra três marcas na ordem repo 07 / pós-CC 07 / CSV.

**BP**

| Método | Fmax | F*max | wFmax | AuPRC | IAuPRC | Smin |
|---|---|---|---|---|---|---|
| Naive baseline | 44.26 `---` | 42.23 `---` | 40.22 `---` | 40.42 `---` | 37.28 `---` | 22.28 `---` |
| DeepGraphGO | 55.29 `==-` | 52.21 `==-` | 48.92 `==-` | 54.04 `==-` | 57.89 `==-` | 20.11 `==-` |
| SEGT-GO | 52.05 `==-` | 48.22 `==-` | 44.57 `==-` | 42.82 `==-` | 50.71 `==-` | 21.24 `==-` |
| Mashup | 43.58 `==-` | 41.86 `==-` | 39.64 `==-` | 34.82 `==-` | 32.57 `==-` | 23.22 `==-` |
| MELISSA | 41.94 `==-` | 40.08 `==-` | 37.72 `==-` | 32.72 `==-` | 31.17 `==-` | 23.42 `==-` |
| deepNF | 35.59 `==-` | 31.14 `==-` | 26.95 `==-` | 34.15 `==-` | 33.66 `==-` | 25.73 `==-` |
| First Generation | 46.25 `===` | 39.86 `===` | 37.30 `===` | 45.57 `===` | 47.37 `===` | 23.68 `===` |
| ProtT5 baseline | 59.61 `===` | 56.31 `===` | 53.74 `===` | 58.53 `===` | 62.92 `===` | 18.92 `===` |
| NEXUS-GO/Fixed | 61.27 `===` | 58.13 `===` | 55.61 `===` | 60.39 `===` | 65.09 `===` | 18.30 `===` |
| NEXUS-GO/GNN | 62.05 `===` | 59.17 `===` | 56.95 `===` | 60.97 `===` | 66.27 `===` | 17.66 `===` |
| NEXUS-GO/Early | 62.87 `===` | 59.81 `===` | 57.51 `===` | 62.42 `===` | 65.73 `===` | 17.35 `===` |
| NEXUS-GO/Late | 63.74 `==-` | 60.96 `==-` | 58.69 `===` | 64.02 `==-` | 68.83 `==-` | 17.12 `==-` |

**CC**

| Método | Fmax | F*max | wFmax | AuPRC | IAuPRC | Smin |
|---|---|---|---|---|---|---|
| Naive baseline | 58.43 `---` | 56.52 `---` | 48.13 `---` | 56.26 `---` | 51.22 `---` | 10.84 `---` |
| DeepGraphGO | 73.74 `==-` | 71.11 `==-` | 60.35 `==-` | 71.88 `==-` | 78.59 `==-` | 9.67 `==-` |
| SEGT-GO | 71.18 `==-` | 68.07 `==-` | 55.52 `==-` | 63.24 `==-` | 74.74 `==-` | 10.42 `==-` |
| Mashup | 59.37 `==-` | 57.44 `==-` | 48.28 `==-` | 51.27 `==-` | 50.30 `==-` | 11.06 `==-` |
| MELISSA | 58.54 `==-` | 56.51 `==-` | 47.19 `==-` | 49.78 `==-` | 48.97 `==-` | 11.23 `==-` |
| deepNF | 62.49 `==-` | 57.59 `==-` | 36.51 `==-` | 58.44 `==-` | 65.10 `==-` | 13.52 `==-` |
| First Generation | 67.38 `===` | 63.46 `===` | 48.39 `===` | 63.83 `===` | 72.20 `===` | 12.03 `===` |
| ProtT5 baseline | 76.79 `===` | 74.29 `===` | 64.78 `===` | 73.30 `===` | 82.06 `===` | 9.47 `===` |
| NEXUS-GO/Fixed | 78.20 `≠==` | 75.85 `≠==` | 66.93 `≠==` | 74.32 `≠==` | 83.78 `≠==` | 8.85 `≠==` |
| NEXUS-GO/GNN | 78.42 `===` | 76.01 `===` | 66.70 `===` | 74.41 `===` | 84.07 `===` | 8.44 `===` |
| NEXUS-GO/Early | 78.42 `≠==` | 76.02 `≠==` | 67.18 `≠==` | 74.33 `≠==` | 83.72 `≠==` | 8.57 `≠==` |
| NEXUS-GO/Late | 79.72 `≠=-` | 77.52 `≠=-` | 69.02 `≠==` | 76.73 `≠=-` | 86.26 `≠=-` | 8.22 `≠=-` |

**MF**

| Método | Fmax | F*max | wFmax | AuPRC | IAuPRC | Smin |
|---|---|---|---|---|---|---|
| Naive baseline | 52.54 `---` | 48.26 `---` | 43.38 `---` | 49.41 `---` | 45.93 `---` | 8.46 `---` |
| DeepGraphGO | 76.98 `==-` | 73.14 `==-` | 68.96 `==-` | 74.03 `==-` | 80.41 `==-` | 5.67 `==-` |
| SEGT-GO | 73.40 `==-` | 68.76 `==-` | 64.12 `==-` | 58.64 `==-` | 75.15 `==-` | 6.37 `==-` |
| Mashup | 54.52 `==-` | 49.82 `==-` | 44.22 `==-` | 47.87 `==-` | 47.29 `==-` | 8.30 `==-` |
| MELISSA | 53.57 `==-` | 48.65 `==-` | 42.86 `==-` | 46.43 `==-` | 46.31 `==-` | 8.47 `==-` |
| deepNF | 58.43 `==-` | 48.70 `==-` | 39.00 `==-` | 54.55 `==-` | 53.49 `==-` | 9.36 `==-` |
| First Generation | 61.04 `===` | 53.38 `===` | 48.62 `===` | 49.34 `===` | 62.42 `===` | 9.20 `===` |
| ProtT5 baseline | 79.75 `===` | 76.02 `===` | 72.57 `===` | 73.75 `===` | 82.25 `===` | 5.31 `===` |
| NEXUS-GO/Fixed | 79.75 `===` | 76.02 `===` | 72.57 `===` | 73.75 `===` | 82.25 `===` | 5.31 `===` |
| NEXUS-GO/GNN | 76.09 `===` | 71.74 `===` | 67.77 `===` | 67.50 `===` | 80.64 `===` | 6.04 `===` |
| NEXUS-GO/Early | 80.22 `===` | 76.54 `===` | 72.94 `===` | 81.88 `===` | 82.05 `===` | 5.22 `===` |
| NEXUS-GO/Late | 80.89 `==-` | 77.41 `==-` | 73.89 `===` | 76.53 `==-` | 84.92 `==-` | 5.14 `==-` |

Campeões (escolhidos em validação) usados na coluna CSV:

- BP First Generation: `bp_mlp_raw_protein_seed1337`
- BP ProtT5 baseline: `bp_fixed_mlp_h0_a05_thr010_dedupmax`
- BP NEXUS-GO/Fixed: `bp_fixed_mlp_h1_a07_thr010_dedupmax`
- BP NEXUS-GO/GNN: `bp_gnn_gcn_mlp_thr010_dedupmax`
- BP NEXUS-GO/Early: `bp_hybrid_add_gcn_mlp_h1_a07_thr010_dedupmax`
- CC First Generation: `cc_mlp_raw_protein_seed1337`
- CC ProtT5 baseline: `cc_fixed_mlp_h0_a05_thr010_dedupmax`
- CC NEXUS-GO/Fixed: `cc_fixed_mlp_h2_a08_thr010_dedupmax`
- CC NEXUS-GO/GNN: `cc_gnn_gcn_mlp_thr010_dedupmax`
- CC NEXUS-GO/Early: `cc_hybrid_concat_gcn_mlp_h2_a08_thr010_dedupmax_embvision`
- MF First Generation: `mf_mlp_raw_protein_seed1337`
- MF ProtT5 baseline: `mf_fixed_mlp_h0_a05_thr010_dedupmax`
- MF NEXUS-GO/Fixed: `mf_fixed_mlp_h0_a05_thr010_dedupmax`
- MF NEXUS-GO/GNN: `mf_gnn_gcn_mlp_thr010_dedupmax`
- MF NEXUS-GO/Early: `mf_hybrid_add_gcn_mlp_h0_a05_thr010_dedupmax`

### 1.5 Custo (tab:custo, 147 runs na RTX A5500)

CSV: famílias das 147 runs RTX A5500 do CSV de 170; s/época = mediana de `sec_per_epoch`; h/run = mediana de `wall_seconds`/3600; Total h = soma; VRAM = máximo de `peak_vram_mb`/1024; Épocas = mediana de `epochs_run`. Repo: Tabela 6.16 de `results/chapter6/01_TABELAS_dedupmax.md` (96 runs, mistura as duas GPUs, sem coluna s/época).

| Família | Runs tese / CSV / repo | s/época tese / CSV | h/run tese / CSV / repo | Total h tese / CSV / repo | VRAM tese / CSV / repo | Épocas tese / CSV / repo |
|---|---|---|---|---|---|---|
| Fixed propagation + vector head | 49 / 49 = / 41 ≠ | 5.24 / 5.24 = | 0.35 / 0.35 = / 0.32 ≠ | 15.1 / 15.1 = / 12.5 ≠ | 6.4 / 6.4 = / 6.4 = | 250 / 250 = / 243 ≠ |
| Fixed propagation + vision head | 26 / 26 = / 25 ≠ | 18.45 / 18.45 ≈ | 0.17 / 0.17 = / 1.39 ≠ | 4.5 / 4.5 = / 36.2 ≠ | 6.4 / 6.4 = / 6.4 = | 35 / 35 = / 34 ≠ |
| End-to-end GNN + vector head | 6 / 6 = / 6 = | 102.14 / 102.14 = | 6.09 / 6.09 = / 6.09 = | 38.7 / 38.7 = / 38.7 = | 20.7 / 20.7 = / 20.7 = | 213 / 213 = / 213 = |
| End-to-end GNN + vision head | 6 / 6 = / 6 = | 108.41 / 108.41 = | 4.35 / 4.35 = / 4.35 = | 31.3 / 31.3 = / 31.3 = | 21.1 / 21.1 = / 21.1 = | 138 / 138 = / 138 = |
| Early fusion + vector head | 40 / 40 = / 12 ≠ | 5.26 / 5.26 ≈ | 0.27 / 0.27 = / 0.14 ≠ | 10.2 / 10.2 = / 1.8 ≠ | 6.4 / 6.4 = / 6.4 = | 205 / 205 = / 112 ≠ |
| Early fusion + vision head | 20 / 20 = / 6 ≠ | 18.63 / 18.63 = | 0.16 / 0.16 = / 0.17 ≠ | 3.2 / 3.2 = / 1.0 ≠ | 6.4 / 6.4 = / 6.4 = | 30 / 30 = / 32 ≠ |
| Total | 147 / 147 / 96 | | | 103.0 / 103.0 / 121,5 | | |

Tabela A.6 (tab:ape_custo), CSV de 170 runs; `best_epoch` = época selecionada. Pico em MiB, wall em horas.

| Família ou run | Runs | Pico MiB | Wall mediana | Wall máx. | Época sel. mediana | mín. | máx. |
|---|---|---|---|---|---|---|---|
| Fixed, vector head (RTX A5500) | 49 / 49 = | 6602 / 6602.5 ≈ | 0.35 / 0.35 = | 0.38 / 0.38 = | 230 / 230 = | 81 / 81 = | 250 / 250 = |
| Fixed, vision head (RTX A5500) | 26 / 26 = | 6602 / 6602.5 ≈ | 0.17 / 0.17 = | 0.22 / 0.22 = | 14 / 14 = | 9 / 9 = | 20 / 20 = |
| Fixed, vision head (GTX 1080 Ti) | 23 / 23 = | 6602 / 6602.5 ≈ | 1.39 / 1.39 = | 2.00 / 2.00 = | 13 / 13 = | 9 / 9 = | 24 / 24 = |
| Early fusion, vector head (RTX A5500) | 40 / 40 = | 6602 / 6602.5 ≈ | 0.27 / 0.27 = | 0.38 / 0.38 = | 184 / 184 = | 30 / 30 = | 250 / 250 = |
| Early fusion, vision head (RTX A5500) | 20 / 20 = | 6602 / 6602.5 ≈ | 0.16 / 0.16 = | 0.19 / 0.19 = | 9 / 9 = | 7 / 7 = | 13 / 13 = |
| GCN, vector head (BP, run único) | 1 / 1  | 12953 / 12952.8 = | 4.77 / 4.77 = |  | 234 / 234 = |  |  |
| GAT, vector head (BP, run único) | 1 / 1  | 18864 / 18864.5 ≈ | 7.40 / 7.40 = |  | 144 / 144 = |  |  |
| GCN, vision head (BP, run único) | 1 / 1  | 13355 / 13355.2 = | 1.96 / 1.96 = |  | 73 / 73 = |  |  |
| GAT, vision head (BP, run único) | 1 / 1  | 19267 / 19267 = | 9.72 / 9.72 = |  | 186 / 186 = |  |  |

### 1.6 Totais da campanha (texto da Seção 6 e Apêndice A.7)

| Item | tese | CSV 170 | status |
|---|---|---|---|
| runs na campanha | 170 | 170.00 | = |
| GPU-horas da campanha | 136.3 | 136.32 | = |
| runs RTX A5500 | 147 | 147.00 | = |
| horas RTX A5500 | 103 | 103.01 | = |
| runs GTX 1080 Ti | 23 | 23.00 | = |
| horas GTX 1080 Ti | 33.3 | 33.32 | = |
| rota fixa: runs | 98 | 98.00 | = |
| rota fixa: horas | 52.9 | 52.93 | = |
| rota aprendida: runs | 12 | 12.00 | = |
| rota aprendida: horas | 70 | 70.00 | = |
| early fusion: runs | 60 | 60.00 | = |
| early fusion: horas | 13.4 | 13.39 | = |
| GCN (vetor) s/época, mediana 3 ont. | 68.76 | 68.76 | = |
| GCN (vetor) VRAM GiB, pico 3 ont. | 14.1 | 14.09 | = |
| GAT (vetor) s/época, mediana 3 ont. | 161.41 | 161.41 | = |
| GAT (vetor) VRAM GiB, pico 3 ont. | 20.7 | 20.71 | = |
| GAT/GCN memória, BP vetor (+%) | 46 | 45.64 | = |
| GAT/GCN tempo, BP vetor (+%) | 55 | 54.93 | = |

### 1.7 Tabelas de contexto (validação), CSV de 170 runs

Tabelas `hops_vector`, `hops_vision`, `alpha_vector`, `alpha_vision`, `gnn`, `early_grid`, `early_best`, `vector_vs_vision` (células e colunas AVG): 246 valores conferidos. Exceções:

| Tabela | Célula | tese | CSV | status |
|---|---|---|---|---|
| hops_vision | T=6 AVG | 59.38 | 59.3739 | ≈ |
| alpha_vector | alpha=0.2 AVG(BP,CC) | 57.48 | 57.4734 | ≈ |
| alpha_vector | alpha=0.4 AVG(BP,CC) | 60.15 | 60.1435 | ≈ |
| alpha_vector | alpha=0.8 AVG(BP,CC) | 60.72 | 60.7128 | ≈ |
| alpha_vision | alpha=0.5 AVG(BP,CC) | 57.62 | 57.6113 | ≈ |
| alpha_vision | alpha=0.8 AVG(BP,CC) | 55.81 | 55.8038 | ≈ |
| alpha_vision | alpha=0.9 AVG(BP,CC) | 54.16 | 54.1534 | ≈ |
| gnn | gat/mlp AVG | 57.15 | 57.1439 | ≈ |

### 1.8 Lista completa de divergências e arredondamentos

| Seção | Item | tese | Fonte | valor da fonte | status |
|---|---|---|---|---|---|
| Custo (tab:custo) | Fixed propagation + vector head / Runs | 49 | repo 01 Tab. 6.16 | 41.0000 | diverge |
| Custo (tab:custo) | Fixed propagation + vector head / h/run | 0.35 | repo 01 Tab. 6.16 | 0.3200 | diverge |
| Custo (tab:custo) | Fixed propagation + vector head / Total h | 15.1 | repo 01 Tab. 6.16 | 12.5000 | diverge |
| Custo (tab:custo) | Fixed propagation + vector head / Epochs | 250 | repo 01 Tab. 6.16 | 243.0000 | diverge |
| Custo (tab:custo) | Fixed propagation + vision head / Runs | 26 | repo 01 Tab. 6.16 | 25.0000 | diverge |
| Custo (tab:custo) | Fixed propagation + vision head / s/epoch | 18.45 | CSV 170 (RTX) | 18.4550 | arredondamento |
| Custo (tab:custo) | Fixed propagation + vision head / h/run | 0.17 | repo 01 Tab. 6.16 | 1.3900 | diverge |
| Custo (tab:custo) | Fixed propagation + vision head / Total h | 4.5 | repo 01 Tab. 6.16 | 36.2000 | diverge |
| Custo (tab:custo) | Fixed propagation + vision head / Epochs | 35 | repo 01 Tab. 6.16 | 34.0000 | diverge |
| Custo (tab:custo) | Early fusion + vector head / Runs | 40 | repo 01 Tab. 6.16 | 12.0000 | diverge |
| Custo (tab:custo) | Early fusion + vector head / s/epoch | 5.26 | CSV 170 (RTX) | 5.2650 | arredondamento |
| Custo (tab:custo) | Early fusion + vector head / h/run | 0.27 | repo 01 Tab. 6.16 | 0.1400 | diverge |
| Custo (tab:custo) | Early fusion + vector head / Total h | 10.2 | repo 01 Tab. 6.16 | 1.8000 | diverge |
| Custo (tab:custo) | Early fusion + vector head / Epochs | 205 | repo 01 Tab. 6.16 | 112.0000 | diverge |
| Custo (tab:custo) | Early fusion + vision head / Runs | 20 | repo 01 Tab. 6.16 | 6.0000 | diverge |
| Custo (tab:custo) | Early fusion + vision head / h/run | 0.16 | repo 01 Tab. 6.16 | 0.1700 | diverge |
| Custo (tab:custo) | Early fusion + vision head / Total h | 3.2 | repo 01 Tab. 6.16 | 1.0000 | diverge |
| Custo (tab:custo) | Early fusion + vision head / Epochs | 30 | repo 01 Tab. 6.16 | 32.0000 | diverge |
| Custo (tab:custo) | Total / Runs | 147 | repo 01 Tab. 6.16 | 96.0000 | diverge |
| Custo (tab:custo) | Total / Total h | 103 | repo 01 Tab. 6.16 | 121.5000 | diverge |
| Custo por família/run (tab:ape_custo) | Fixed, vector head RTX A5500 / Peak MiB | 6602 | CSV 170 | 6602.5000 | arredondamento |
| Custo por família/run (tab:ape_custo) | Fixed, vision head RTX A5500 / Peak MiB | 6602 | CSV 170 | 6602.5000 | arredondamento |
| Custo por família/run (tab:ape_custo) | Fixed, vision head GTX 1080 Ti / Peak MiB | 6602 | CSV 170 | 6602.5000 | arredondamento |
| Custo por família/run (tab:ape_custo) | Early fusion, vector head RTX A5500 / Peak MiB | 6602 | CSV 170 | 6602.5000 | arredondamento |
| Custo por família/run (tab:ape_custo) | Early fusion, vision head RTX A5500 / Peak MiB | 6602 | CSV 170 | 6602.5000 | arredondamento |
| Custo por família/run (tab:ape_custo) | GAT, vector head BP / Peak MiB | 18864 | CSV 170 | 18864.5000 | arredondamento |
| Late fusion (tab:late_fusion) | Linear interpolation (γ) / CC | 68.79 | repo 01 Tab. 6.13 | 68.4900 | diverge |
| Late fusion (tab:late_fusion) | Linear interpolation (γ) / AVG | 67.06 | média repo | 66.9633 | diverge |
| Late fusion (tab:late_fusion) | Maximum / CC | 67.79 | repo 01 Tab. 6.13 | 67.5700 | diverge |
| Late fusion (tab:late_fusion) | Maximum / AVG | 65.91 | média repo | 65.8367 | diverge |
| Late fusion (tab:late_fusion) | Minimum / CC | 68.09 | repo 01 Tab. 6.13 | 67.8400 | diverge |
| Late fusion (tab:late_fusion) | Minimum / AVG | 65.72 | média repo | 65.6367 | diverge |
| Late fusion (tab:late_fusion) | IC sigmoid / CC | 67.57 | repo 01 Tab. 6.13 | 67.3300 | diverge |
| Late fusion (tab:late_fusion) | IC sigmoid / AVG | 66.16 | média repo | 66.0800 | diverge |
| Late fusion (tab:late_fusion) | Degree sigmoid / CC | 67.76 | repo 01 Tab. 6.13 | 67.2600 | diverge |
| Late fusion (tab:late_fusion) | Degree sigmoid / AVG | 65.73 | média repo | 65.5667 | diverge |
| Late fusion (tab:late_fusion) | Master equation / CC | 68.1 | repo 01 Tab. 6.13 | 67.7500 | diverge |
| Late fusion (tab:late_fusion) | Master equation / AVG | 66.48 | média repo | 66.3667 | diverge |
| Late fusion (tab:late_fusion) | Stacking (decision tree) / CC | 67.35 | repo 01 Tab. 6.13 | 67.7700 | diverge |
| Late fusion (tab:late_fusion) | Stacking (decision tree) / AVG | 65.78 | média repo | 65.9167 | diverge |
| Late fusion (tab:late_fusion) | Stacking (logistic regression) / CC | 68.5 | repo 01 Tab. 6.13 | 68.0700 | diverge |
| Late fusion (tab:late_fusion) | Stacking (logistic regression) / AVG | 66.17 | média repo | 66.0233 | diverge |
| Late fusion (tab:late_fusion) | Stacking (MLP) / CC | 68.12 | repo 01 Tab. 6.13 | 68.0800 | diverge |
| Late fusion (tab:late_fusion) | Stacking (MLP) / AVG | 66.32 | média repo | 66.3067 | diverge |
| Late fusion (tab:late_fusion) | Stacking (random forest) / CC | 68.21 | repo 01 Tab. 6.13 | 68.1000 | diverge |
| Late fusion (tab:late_fusion) | Stacking (random forest) / AVG | 66.33 | média repo | 66.2967 | diverge |
| Late fusion (tab:late_fusion) | Stacking (gradient boosting) / CC | 67.72 | repo 01 Tab. 6.13 | 66.8500 | diverge |
| Late fusion (tab:late_fusion) | Stacking (gradient boosting) / AVG | 66.19 | média repo | 65.9000 | diverge |
| Coeficientes selecionados (tab:ape_fusao_sel) | lambda / CC | 0.4 | repo 01 | 0.5000 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Fixed / fmax | 78.2 | repo 07 | 78.1600 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Fixed / fmax_star | 75.85 | repo 07 | 75.8600 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Fixed / wfmax | 66.93 | repo 07 | 67.0000 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Fixed / auprc | 74.32 | repo 07 | 74.2700 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Fixed / iauprc | 83.78 | repo 07 | 83.8800 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Fixed / smin | 8.85 | repo 07 | 8.7600 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Early / fmax | 78.42 | repo 07 | 78.8200 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Early / fmax_star | 76.02 | repo 07 | 76.4400 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Early / wfmax | 67.18 | repo 07 | 67.4700 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Early / auprc | 74.33 | repo 07 | 82.6900 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Early / iauprc | 83.72 | repo 07 | 83.2100 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Early / smin | 8.57 | repo 07 | 8.3400 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Late / fmax | 79.72 | repo 07 | 79.5200 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Late / fmax_star | 77.52 | repo 07 | 77.2600 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Late / wfmax | 69.02 | repo 07 | 68.6500 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Late / auprc | 76.73 | repo 07 | 76.4800 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Late / iauprc | 86.26 | repo 07 | 86.1700 | diverge |
| Teste CC (tab:confronto_cc) | NEXUS-GO/Late / smin | 8.22 | repo 07 | 8.1900 | diverge |
| Contexto hops_vision | T=6 AVG | 59.38 | CSV 170 | 59.3739 | arredondamento |
| Contexto alpha_vector | alpha=0.2 AVG(BP,CC) | 57.48 | CSV 170 | 57.4734 | arredondamento |
| Contexto alpha_vector | alpha=0.4 AVG(BP,CC) | 60.15 | CSV 170 | 60.1435 | arredondamento |
| Contexto alpha_vector | alpha=0.8 AVG(BP,CC) | 60.72 | CSV 170 | 60.7128 | arredondamento |
| Contexto alpha_vision | alpha=0.5 AVG(BP,CC) | 57.62 | CSV 170 | 57.6113 | arredondamento |
| Contexto alpha_vision | alpha=0.8 AVG(BP,CC) | 55.81 | CSV 170 | 55.8038 | arredondamento |
| Contexto alpha_vision | alpha=0.9 AVG(BP,CC) | 54.16 | CSV 170 | 54.1534 | arredondamento |
| Contexto gnn | gat/mlp AVG | 57.15 | CSV 170 | 57.1439 | arredondamento |

Ausentes (sem valor na fonte):

- repo 01 Tab. 6.16, Custo (tab:custo): 6 valores (Early fusion + vector head, Early fusion + vision head, End-to-end GNN + vector head, End-to-end GNN + vision head, Fixed propagation + vector head, Fixed propagation + vision head)
- repo 07, Teste BP (tab:confronto_bp): 6 valores (Naive baseline)
- pós-CC 07, Teste BP (tab:confronto_bp): 6 valores (Naive baseline)
- CSV 170, Teste BP (tab:confronto_bp): 36 valores (DeepGraphGO, MELISSA, Mashup, Naive baseline, SEGT-GO, deepNF)
- repo 01 Tab. 6.13 (teste), Teste BP (tab:confronto_bp): 5 valores (NEXUS-GO/Late)
- repo 07, Teste CC (tab:confronto_cc): 6 valores (Naive baseline)
- pós-CC 07, Teste CC (tab:confronto_cc): 6 valores (Naive baseline)
- CSV 170, Teste CC (tab:confronto_cc): 36 valores (DeepGraphGO, MELISSA, Mashup, Naive baseline, SEGT-GO, deepNF)
- log CC novo, Teste CC (tab:confronto_cc): 5 valores (NEXUS-GO/Late)
- repo 07, Teste MF (tab:confronto_mf): 6 valores (Naive baseline)
- pós-CC 07, Teste MF (tab:confronto_mf): 6 valores (Naive baseline)
- CSV 170, Teste MF (tab:confronto_mf): 36 valores (DeepGraphGO, MELISSA, Mashup, Naive baseline, SEGT-GO, deepNF)
- repo 01 Tab. 6.13 (teste), Teste MF (tab:confronto_mf): 5 valores (NEXUS-GO/Late)
