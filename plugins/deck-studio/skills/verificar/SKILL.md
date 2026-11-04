---
name: verificar
description: "Confere o que o Deck Studio precisa nesta máquina (Python, Chromium do Playwright, Node, TeX, Perl) e diz como instalar o que falta. Use na primeira vez, ou quando uma ferramenta do deck falhar por falta de programa."
---

# Verificar a instalação

1. Chame `mcp__plugin_deck-studio_deck__verificar` com `idioma`: `en` se o autor escreve em inglês, senão `pt`. Ela instala o Chromium do Playwright, se faltar (download gratuito), e lista o resto.
2. Responda ao autor no idioma em que ele escreve, com uma lista curta: o que está pronto e, para cada coisa que falta, o comando do sistema dele (Windows ou Ubuntu/Debian), como a ferramenta indicou.
3. O TeX e o Perl só fazem falta para o Beamer, e o Node só para o deck de exemplo. Diga isso, para o autor não instalar o que não vai usar.
