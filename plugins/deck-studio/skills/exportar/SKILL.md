---
name: exportar
description: "Exporta a apresentação do projeto: o PDF do deck HTML ou o zip do Overleaf do Beamer. Use quando o autor pedir o PDF, o arquivo para enviar ou para o Overleaf."
---

# Exportar

1. Rode `mcp__plugin_deck-studio_deck__run_qa`. Se algo falhar, conserte antes, ou diga ao autor o que falhou e pergunte se exporta assim mesmo.
2. Chame `mcp__plugin_deck-studio_deck__exportar` com `formato`: `"pdf"` faz o build limpo e o PDF do deck HTML (`deck/dist/deck.pdf`); `"overleaf"` faz o zip do Beamer (`beamer/apresentacao`) em `exports/`, conferido compilando uma cópia sozinha, sem nenhum `[?]`. Sem formato, vale o do projeto. Para o Overleaf, o Beamer precisa estar escrito: veja a fase F da `deck-studio:criar-apresentacao`.
3. Diga ao autor o caminho do arquivo e, no Beamer, como subir no Overleaf: New Project > Upload Project, depois Recompile.
