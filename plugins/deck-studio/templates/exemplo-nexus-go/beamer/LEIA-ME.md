# Versão Beamer da defesa

| Arquivo | Para quê |
|---|---|
| `nexus-go-defense.pdf` | apresentar (321 páginas: 53 slides com os passos, mais as páginas dos controles clicáveis) |
| `nexus-go-defense-notes.pdf` | o mesmo, com as notas do apresentador numa segunda tela à direita |
| `nexus-go-defense.tex` + `slides.tex` | fonte LaTeX (XeLaTeX) |
| `nexus-go-defense-overleaf.zip` | o projeto inteiro para subir no Overleaf (o `latexmkrc` faz o Overleaf compilar com XeLaTeX, mesmo com o compilador padrão, pdfLaTeX) |

## Como foi feito

O Beamer é gerado a partir do HTML, então os dois decks não divergem.

- **Texto:** todo o texto dos slides é LaTeX nativo, com as mesmas três fontes, nas mesmas posições e com as mesmas quebras de linha do HTML. Dá para selecionar, buscar e editar no `slides.tex`.
- **Figuras:** as figuras da tese entram por `\includegraphics` (pasta `figures/`).
- **Diagramas e gráficos:** o que não é texto nem figura, como os diagramas, os gráficos e as placas, entra como camada vetorial impressa do próprio HTML (`build/layers.pdf`).
- **Passos:** cada passo do HTML vira um overlay do Beamer, isto é, uma página.

## Passos que o PDF tem a mais que o HTML

| Slide | Páginas extras, no fim do slide |
|---|---|
| S21 | rota "All" com a animação das partículas |
| S23 | deduplicação por max (o passo anterior mostra sum) |
| S24 | T = 0 e T = 6, depois a animação da varredura de T e α |
| S38 | CC e MF em wF<sub>max</sub> (o passo anterior mostra BP) |

## Botões clicáveis (funcionam em qualquer leitor de PDF)

- **S21:** os botões de rota (All, /Fixed, /GNN, /Early, /Late) e "Dissertation figure".
- **S23:** sum e max.
- **S24:** os sliders T (de 0 a 10) e α (de 0.1 a 0.9), com os 99 estados possíveis, e o botão play, que leva à animação.
- **S38:** as abas BP, CC e MF. Clicar no seletor de métrica passa para a próxima métrica.

Os estados que não estão na sequência normal ficam no fim do PDF, depois dos backups. Clique no título do slide para voltar à apresentação.

## Animações (pacote `animate`)

- **Onde tocam:** o S21 (partículas nas rotas) e o S24 (varredura de T e α) tocam sozinhos no Adobe Acrobat Reader, e também no PDF-XChange e no Foxit.
- **Onde não tocam:** nos outros leitores (Chrome, Edge, Firefox, SumatraPDF, Preview do Mac) aparece o primeiro quadro, parado, e o slide continua correto.

## Regenerar depois de mudar o HTML

```
node deck/build.mjs
python -I -X utf8 beamer/tools/build.py
```

O `build.py` faz o seguinte:
- mede o HTML (`extract.py`) e escreve o `slides.tex` (`make_tex.py`);
- compila os dois PDFs com XeLaTeX, duas vezes cada;
- falha se houver Overfull box acima de 10 pt;
- refaz o zip do Overleaf.

Para recompilar sem medir o HTML de novo (por exemplo, depois de editar o `slides.tex` à mão), use `--tex`.

Para conferir o Beamer contra o HTML:
- **Imagens:** `beamer/tools/compare.py` grava, para cada estado, o HTML, o Beamer e a diferença lado a lado em `qa/beamer/`.
- **Texto e números:** `beamer/tools/check_text.py` confere o texto e os números e grava o resultado em `qa/beamer_text.md`.

## Overleaf

Suba o zip como projeto novo. A compilação é pesada: 321 páginas, cerca de 35 s por passada nesta máquina. No plano gratuito do Overleaf ela pode passar do tempo limite. O PDF daqui é o entregável; o zip serve para editar.
