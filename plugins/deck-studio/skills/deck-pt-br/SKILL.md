---
name: deck-pt-br
description: "Use ao escrever, traduzir ou revisar a versão em português (PT-BR) de um deck do Deck Studio: separadores numéricos, itálico, glossário, calques, títulos e paridade com a versão em inglês."
---

# Deck em português do Brasil

## Números
1. O separador segue o idioma do SLIDE, não o da fonte: vírgula decimal e ponto de milhar em tudo, inclusive nas tabelas geradas, nos gráficos, nos tooltips, nas fórmulas (0{,}7) e nos números de 4 dígitos (1.024). Num conjunto, separe os itens com ponto e vírgula: {0,4; 1,1}. O valor não muda (wf681:14,15; wf772:15,17; wf7a4:16).
2. Depois de traduzir, compare os números slide a slide entre as versões (texto do último passo, com os decimais normalizados). Toda diferença precisa ser intencional e explicada. Foi assim que apareceu um "73,768" (milhar em inglês) lido como decimal (wf772:15; wf681:6).

## Termos
3. Termo em inglês dentro do texto em português vai em itálico em TODO lugar, inclusive nos gráficos, nas tabelas e nos textos de animação, aplicado a partir de uma lista explícita. Fórmulas, subscritos e nomes próprios ficam de fora (p01:60,84,137; DEC:187).
4. Depois de mudar um estilo inline, confira o layout de cada slide afetado: uma tag não pode virar coluna nem sobrepor texto (p01:112-116).
5. Os termos técnicos consagrados (baseline, backbone, nomes de métodos) ficam em inglês, iguais na tabela, no gráfico e no texto (wf772:15).
6. Use um glossário único: o mesmo termo nos slides, nas notas, na narração e nos componentes. Um conceito que aparece em dois slides tem a redação idêntica. Cada divergência vira correção ou pergunta ao autor (wf772:15,17; wf681:14).

## Redação
7. Revise calques e concordância: "contra" como tradução de "against"; o adjetivo colado ao substantivo errado; "onde" para o que não é lugar ("em que"); e "reporto" no lugar de "apresento" (wf681:14).
8. Os títulos seguem um padrão único de capitalização (ex.: maiúscula depois dos dois-pontos). O título também vira o capítulo do vídeo (wf681:14).
9. O título oficial do trabalho fica no idioma em que foi registrado (wf681:6; wf772:10; DEC:114).
10. Quando o texto estoura, reescreva ou encurte; nunca reduza a fonte. A fonte mediana das tabelas fica numa razão de cerca de 1,0 com a original, e um rótulo traduzido longo vira um cabeçalho mais curto (wf681:6; DEC:126-127).

## Tradução e paridade
11. A versão em português sai da mesma fonte (FACTS.md > EN > PT), e nenhum rótulo fica sem tradução, nem dentro do data-opts dos componentes (wf681:6).
12. Preserve a marcação, os ids, as classes, os data-* e as coordenadas. Os rótulos de seção visíveis (data-part) usam os mesmos nomes do Sumário (wf772:8,10,11).
13. Toda mudança pedida vale para as duas línguas, salvo uma adaptação de espaço justificada (p01:71,116,147).

Evidência: as regras foram mineradas das falas do autor do kit NEXUS-GO nas sessões do deck, das rodadas de crítica e dos documentos do kit; os códigos entre parênteses (p01, wfXXX, DEC, DES, INT, QA, COMP, STO, FIG, PED) apontam para essas fontes, que ficam fora do projeto. O NEXUS-GO aparece só como exemplo.
