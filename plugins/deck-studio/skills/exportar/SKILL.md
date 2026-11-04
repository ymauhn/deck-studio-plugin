---
name: exportar
description: "Exporta a apresentação do projeto: o PDF do deck HTML ou o zip do Overleaf do Beamer. Use quando o autor pedir o PDF, o arquivo para enviar ou para o Overleaf."
---

# Exportar

1. Rode `mcp__plugin_deck-studio_deck__run_qa`. Se algo falhar, conserte antes, ou diga ao autor o que falhou e pergunte se exporta assim mesmo.
2. Chame `mcp__plugin_deck-studio_deck__exportar`. Num projeto HTML, ela faz o build limpo e o PDF (`deck/dist/deck.pdf`); num projeto Beamer, o zip do Overleaf em `exports/`.
3. Diga ao autor o caminho do arquivo e, no Beamer, como subir no Overleaf: New Project > Upload Project, depois Recompile.
