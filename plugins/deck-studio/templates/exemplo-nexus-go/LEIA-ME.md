# Como usar este kit com o Claude Code

1. Crie uma pasta vazia, por exemplo `C:\Users\voce\Documents\nexus-go-deck`, e copie
   para dentro dela todo o conteúdo deste kit (o `CLAUDE.md`, o `PROMPT.md`, as pastas
   `docs/`, `data/` e `tools/`).
2. Abra um terminal nessa pasta e rode `claude`.
3. Instale as skills (uma vez só), dentro do Claude Code:

   ```
   /plugin marketplace add anthropics/skills
   /plugin install example-skills@anthropic-agent-skills
   /plugin install document-skills@anthropic-agent-skills
   ```

4. Abra o `PROMPT.md`, copie tudo o que está abaixo da linha e cole no Claude Code.
5. Quando ele pedir permissão para instalar ferramentas (Node, Python, Playwright, Git,
   MiKTeX), aprove de uma vez. Se preferir não instalar LaTeX, ele entrega um zip para
   compilar no Overleaf.

O `CLAUDE.md` é lido automaticamente pelo Claude Code em toda conversa nessa pasta. Ele aponta
para os documentos em `docs/`, que trazem o roteiro dos 45 slides, os números verificados da
dissertação, o sistema visual, a especificação de cada animação e o plano de testes.

Quando ele terminar, o arquivo principal será `deck/dist/nexus-go-defense.html`. Se quiser
publicá-lo como artefato no claude.ai, traga esse arquivo de volta para a conversa no Cowork.

O código da pesquisa NEXUS-GO não vem neste exemplo: ele é público em https://github.com/ymauhn/nexus-go (MIT, com os resultados em CC BY 4.0). Para a conferência opcional dos resultados (`qa/repo_audit.py`, `docs/QA.md`), clone-o em `source/nexus-go/`.
