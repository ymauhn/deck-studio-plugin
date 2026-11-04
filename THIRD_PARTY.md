# Terceiros

O plugin instala estas dependências (no `server/pyproject.toml`, nas versões travadas do `uv.lock`), e o modelo de projeto traz as fontes abaixo, embutidas no deck.

| Componente | Uso | Licença |
|---|---|---|
| mcp (Model Context Protocol, SDK Python) | o servidor MCP do plugin | MIT |
| FastAPI | rotas do módulo Beamer reaproveitado do app | MIT |
| PyMuPDF | extrair o texto e as figuras dos PDFs; páginas do Beamer | AGPL-3.0 |
| Playwright | capturas, checagens e QA dos slides no Chromium | Apache-2.0 |
| Pillow | imagens do deck de exemplo (o build dele) | MIT-CMU |
| esbuild, MathJax, parse5 | o build do deck de exemplo (`npm ci` em `deck/`) | MIT, Apache-2.0, MIT |
| Atkinson Hyperlegible Next | fonte do texto dos slides | SIL Open Font License 1.1 |
| Bricolage Grotesque | fonte dos títulos | SIL Open Font License 1.1 |
| IBM Plex Mono | fonte dos números | SIL Open Font License 1.1 |

O deck de exemplo (`templates/exemplo-nexus-go`) é a defesa de mestrado NEXUS-GO, com o texto, os números, as figuras e os nomes, publicado com a autorização do autor. O código do NEXUS-GO é MIT, e os resultados, CC BY 4.0 (github.com/ymauhn/nexus-go).

Os artigos usados nos testes e exemplos de aceite são do arXiv, com licença CC BY 4.0, e os créditos estão nas referências de cada deck.
