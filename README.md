# Deck Studio para o Claude Code

Um plugin do Claude Code que cria e edita apresentações (HTML e Beamer) a partir de um artigo, uma tese ou uma pasta de materiais. Ele segue um método em fases:
- briefing;
- fatos com a página da fonte;
- storyline aprovada pelo autor;
- slides a partir de exemplos;
- diagramas e gráficos animados com os números reais;
- QA de layout e de números;
- um juiz que dá nota a cada slide.

## Requisitos

- **Claude Code instalado e logado com a sua própria conta:** um plano Pro ou acima, ou uma chave de API do Console.
- **`uv`:** ele baixa o Python 3.12 sozinho.
- **Chromium do Playwright:** a skill `/deck-studio:verificar` instala.
- **Opcionais:**
  - para o Beamer, TeX (MiKTeX no Windows, TeX Live no Linux) e Perl;
  - o Node, só para o deck de exemplo.

Funciona no Windows e no Linux (Ubuntu ou Debian).

## Instalar

No Claude Code:

```
/plugin marketplace add ymauhn/deck-studio-plugin
/plugin install deck-studio@ymauhn-deck
```

Abra uma sessão nova e rode `/deck-studio:verificar`. Ela diz o que falta nesta máquina e como instalar.

**Windows:**
1. Instale o Claude Code (code.claude.com) e entre com a sua conta.
2. Instale o Git for Windows: ele traz o Git Bash e o Perl que o `latexmk` usa.
3. Instale o `uv`: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`.
4. Para o Beamer, instale o MiKTeX, com "instalar pacotes na hora" ligado.

**Ubuntu ou Debian:**
1. Instale o Claude Code e entre com a sua conta.
2. Rode `sudo apt install -y git perl curl`.
3. Instale o `uv` pelo instalador oficial (astral.sh/uv).
4. Para o Beamer, rode `sudo apt install -y texlive-latex-extra texlive-fonts-recommended latexmk`.
5. O Chromium precisa das bibliotecas do sistema: `uv run playwright install --with-deps chromium` (pede `sudo`).

## Primeiro deck

1. Numa pasta de trabalho, abra o Claude Code e peça: "crie uma apresentação a partir de artigo.pdf" (ou de uma pasta). A ferramenta `novo_projeto` monta o projeto e extrai o texto e as figuras do PDF.
2. A skill `/deck-studio:criar-apresentacao` conduz o resto. Ela para duas vezes para você decidir: no briefing e na storyline.
3. No fim, o QA e o juiz ficam verdes. O deck é um arquivo HTML único em `deck/dist/deck.html`, e `exportar` dá o PDF (ou o zip do Overleaf, no Beamer).

## O deck de exemplo

Peça "abra o deck de exemplo", que usa a ferramenta `abrir_exemplo`. Ela copia para uma pasta nova a defesa de mestrado NEXUS-GO, feita com este método, com:
- storyline e fatos com fonte;
- componentes interativos;
- QA;
- versões em inglês e em português;
- Beamer.

O build dele precisa do Node.

## Privacidade

Os artigos e os decks ficam no seu computador, e o plugin não envia nada a servidor próprio. O que vai para a Anthropic é o que o Claude Code envia na sua sessão, sob os termos da sua conta.

## Uso da assinatura

Este plugin roda dentro do Claude Code oficial, sem modificação, e usa a conta com que **você** entrou nele. O autor do plugin não fornece, não revende nem intermedeia acesso ao Claude. Os limites de uso são os do seu plano, sujeitos aos termos da Anthropic.

## Licença e terceiros

- **Licença:** AGPL-3.0 ([LICENSE](LICENSE)).
- **Terceiros:** em [THIRD_PARTY.md](THIRD_PARTY.md).
- **Não afiliado à Anthropic:** "Claude Code" aparece aqui só para dizer para qual ferramenta é o plugin.

## Como o plugin é montado

O código vem do Deck Studio (o app), pelo script `scripts/montar_plugin.py` do repositório dele:
- as skills do método e o juiz;
- o modelo de projeto;
- os módulos `deck_studio` de que o servidor MCP precisa.

Não edite à mão o que ele gera: `plugins/deck-studio/skills/criar-apresentacao` e `deck-*`, `agents/juiz.md` e `server/deck_studio/`.
