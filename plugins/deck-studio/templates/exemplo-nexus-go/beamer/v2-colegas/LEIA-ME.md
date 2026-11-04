# Versão 2 da defesa, no formato dos colegas (Beamer, 28/10)

Versão nova, escrita à mão em pdfLaTeX. Segue o formato das defesas do Wilson (14/05/2026) e da Juliana (29/04/2026), que têm o mesmo orientador. Não substitui as versões de 17/10 (`beamer/`, gerada do HTML) e de 20/10 (`beamer/academico/`).

| Arquivo | Para quê |
|---|---|
| `nexus-go-v2.pdf` | apresentar: 61 frames, mais 2 de backup; 79 páginas com os passos |
| `nexus-go-v2.tex` | fonte (tema Madrid, Latin Modern Sans, 16:9) |
| `tables.tex` | tabelas geradas de `data/thesis_tables.json` (cópia do `beamer/academico`) |
| `gains.tex` | barras do gráfico "Where the gains come from", geradas por `gen_gains.py` do mesmo JSON |
| `references.bib` | cópia da bibliografia da tese, com vírgula no lugar do travessão do VISAPP; o slide lista só as 22 entradas citadas |
| `figures/`, `logos/` | figuras da tese; logo da Unicamp (da tese) e do IC |
| `latexmkrc` | diz ao latexmk e ao Overleaf para usar pdfLaTeX |

## Data e resultados no teste

- **Data:** a capa e o rodapé dizem November 16, 2026.
- **Teste:** BP, CC e MF têm um frame cada na seção de resultados (frames 43, 44 e 45), com a tabela à esquerda e três leituras da própria ontologia, uma por clique. A leitura que vale para as três (o NEXUS-GO/Late é o melhor em todas as colunas, menos AuPRC em MF) fecha o frame do MF.
- **Backup:** ficam só o custo por família e a deduplicação dos registros do STRING.

## O que veio de cada colega

- **Dos dois:**
  - tema Madrid, com rodapé em três partes: autor (IC/Unicamp), "Master's Defense", data e página;
  - título numa caixa com sombra, com orientador e coorientadores;
  - sumário no começo e de novo no início de cada seção;
  - legendas numeradas ("Figure n", "Table n");
  - referências numeradas em ordem alfabética.
- **Do Wilson:**
  - barra de título azul-marinho e rodapé em três tons de azul;
  - objetivos seguidos das questões de pesquisa (RQ1 a RQ7), respondidas uma a uma no fim;
  - caixas de equação com sombra;
  - nos resultados, comentários que aparecem num segundo clique;
  - o diagrama das quatro rotas percorrido parte por parte;
  - "Contributions and Publications";
  - agradecimentos com os logos da Unicamp e do IC.
- **Da Juliana:**
  - blocos claros: "Problem", "General objective", "Reading" e o lilás de "Open question";
  - uma seção só de trabalhos relacionados, com tabela;
  - "Limitations of the Study";
  - a página de título repetida no fim, para as perguntas.

## Compilar

- **Aqui:** `latexmk nexus-go-v2.tex`. Ele faz pdfLaTeX, BibTeX e as passadas extras.
- **Overleaf:** suba `nexus-go-v2-overleaf.zip` em *New Project > Upload Project* e compile. O `latexmkrc` já escolhe o pdfLaTeX.

## Se mudar números

- **Tabelas:** rode `python -I -X utf8 beamer/academico/gen_tables.py` e copie o `tables.tex` para cá.
- **Gráfico:** rode `python -I -X utf8 beamer/v2-colegas/gen_gains.py`.

Os dois scripts leem o `data/thesis_tables.json`, então nenhum número é digitado à mão.
