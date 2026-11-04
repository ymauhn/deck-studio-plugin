# Versão 2 da defesa em português (Beamer, 28/10)

Tradução para o português do Brasil do deck em `beamer/v2-colegas/`, já com a data de 16/11 e os resultados de teste de CC e MF nos resultados principais. Até 28/10, a página N deste PDF era a página N do PDF em inglês. Em 04/11, as anotações do orientador entraram só aqui (ver `RELATORIO-BEAMER.md`), então essa correspondência acabou, e a narração em português não acompanha mais as páginas.

| Arquivo | Para quê |
|---|---|
| `nexus-go-v2-pt.pdf` | apresentar: 64 frames, mais 2 de backup; 90 páginas com os passos |
| `nexus-go-v2-pt.tex` | fonte (tema Madrid, Latin Modern Sans, 16:9, `babel` em `brazilian`) |
| `tables.tex` | tabelas, geradas por `gen_pt.py` a partir do `tables.tex` em inglês |
| `gains.tex` | barras do gráfico "De Onde Vêm os Ganhos", geradas por `gen_pt.py` a partir do `gains.tex` em inglês |
| `gen_pt.py` | traduz os rótulos das tabelas e do gráfico e passa os números para o formato brasileiro |
| `references.bib` | cópia da bibliografia da tese, com vírgula no lugar do travessão do VISAPP; o slide lista só as 22 entradas citadas |
| `figures/`, `logos/` | as mesmas figuras e logos da versão em inglês |
| `latexmkrc` | diz ao latexmk e ao Overleaf para usar pdfLaTeX |

## Convenções

- **Título:** a capa mantém o título oficial em inglês, porque a tese não tem título em português.
- **Rodapé:** "Defesa de Mestrado" e "16 de novembro de 2026".
- **Números:** vírgula decimal (65,80) e ponto de milhar (2.422.234), como no resumo da tese e nos decks do Wilson e da Juliana, também nos números de quatro dígitos (1.024, 3.072), como nas legendas do vídeo. Pontos percentuais aparecem como p.p.
- **Termos:** questões de pesquisa QP1 a QP7; fusão precoce e fusão tardia; cabeça vetorial e visual; propagação fixa e agregação aprendida; saltos e retenção α. As rotas mantêm os nomes das tabelas (Fixed, GNN, Early, Late).
- **Tabelas:**
  - a regra de fusão tardia por empilhamento aparece como "Stacking (...)", para a tabela não encolher em relação à versão em inglês;
  - no backup de custo, "cabeça" foi para o cabeçalho, "Família (rota + cabeça)", pelo mesmo motivo.
- **Figuras:** as figuras da tese continuam com o texto em inglês, porque são imagens.
- **Legendas:** o `babel` escreve "Figura", "Tabela" e o "Sumário" sai no título do frame.
- **Referências:** ficam em inglês, como nos decks dos colegas, e são compostas com a hifenização do inglês, o que mantém os 4 frames da versão em inglês.

## Compilar

- **Aqui:** `latexmk nexus-go-v2-pt.tex`. Ele faz pdfLaTeX, BibTeX e as passadas extras.
- **Overleaf:** suba `beamer/nexus-go-v2-pt-overleaf.zip` em *New Project > Upload Project* e compile. O `latexmkrc` já escolhe o pdfLaTeX.

## Se mudar números

1. Atualize primeiro a versão em inglês, como diz o `LEIA-ME.md` de `beamer/v2-colegas/`.
2. Depois rode `python -I -X utf8 beamer/v2-colegas-pt/gen_pt.py`.

O `gen_pt.py` lê os arquivos gerados em inglês, que vêm do `data/thesis_tables.json`, e para se encontrar um rótulo que não conhece. Nenhum número é digitado à mão, e os geradores em inglês não mudam.
