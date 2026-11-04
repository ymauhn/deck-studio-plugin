---
name: novo-projeto
description: "Cria um projeto de apresentação a partir de um PDF (artigo, tese) ou de uma pasta de materiais. Use quando o autor pedir uma apresentação nova a partir de um arquivo ou de uma pasta."
---

# Novo projeto

1. Pergunte, numa mensagem só e só o que faltar: o arquivo ou a pasta de origem, o título, o idioma dos slides (português ou inglês) e o formato (HTML, o padrão, ou Beamer).
2. Chame `mcp__plugin_deck-studio_deck__novo_projeto`. Por padrão, o projeto vai para uma pasta nova dentro da pasta desta sessão.
3. Depois, siga a skill `deck-studio:criar-apresentacao` no projeto novo. As ferramentas do deck já trabalham nele; para trocar de projeto, passe `projeto` com a pasta.
