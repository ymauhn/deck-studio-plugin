# Versão acadêmica da defesa (Beamer, 20/10)

Versão nova, escrita à mão; não substitui a de 17/10 (`beamer/`, gerada do HTML).

| Arquivo | Para quê |
|---|---|
| `nexus-go-academic.pdf` | apresentar: 45 slides (S01 a S45) e 3 de backup (CC, MF, custo); 55 páginas com os passos |
| `nexus-go-academic.tex` | fonte (pdfLaTeX, tema sóbrio, Latin Modern, rodapé com seção e número) |
| `tables.tex` | tabelas geradas de `data/thesis_tables.json` por `gen_tables.py` (nada digitado à mão) |
| `cards.json`, `cards.html` | roteiro: um card por slide (3 a 5 pontos, tempo, transição); `make_cards.py` gera o HTML |
| `figures/` | cópias das figuras da tese (de `beamer/figures/`) |

Compilar: `python -I -X utf8 gen_tables.py` e depois `latexmk -pdf nexus-go-academic.tex` (0 erros, 0 overfull).
Cards publicados (privado): https://claude.ai/artifact/E1x88GCcc1KHRrfCKWEqa6

Os slides seguem o `docs/STORYLINE.md` um a um (o slide n do PDF é o Sn); os números vêm do roteiro auditado
contra o `.tex` e, nas tabelas, do JSON. Os componentes interativos viraram tabelas da tese ou figuras estáticas
(TikZ no S11, S21 e S37). Os tempos dos cards vêm da duração de cada capítulo do vídeo narrado (44 min),
arredondados a 15 s; os pontos estão em inglês, a língua da apresentação.
