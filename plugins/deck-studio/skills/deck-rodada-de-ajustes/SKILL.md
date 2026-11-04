---
name: deck-rodada-de-ajustes
description: "Use quando o autor ou o orientador manda correções num deck do Deck Studio (lista, comentário ou captura de tela): como interpretar, propagar a todos os slides, registrar e relatar."
---

# Rodada de ajustes do autor

## Antes do primeiro build
1. Depois do briefing, se o autor disser "pode ir", entregue logo uma primeira versão COMPLETA. A decisão estética aberta fica com o padrão e volta como pendência (p01:284,333-335).
2. A parada de visual usa 3 slides reais, de tipos diferentes, nos dois temas (p01:247-255; DEC:8-9).
3. Um fato de capa (data, local, apresentador) que diverge entre as fontes do autor vira pergunta, feita uma vez; não escolha em silêncio. Não preencha o apresentador, a data ou a instituição com os do PDF quando quem apresenta pode ser outra pessoa. O que faltar vai no resumo, e não num placeholder (wf97b:3,5; wf7a4:16; wf13f:3).

## Aplicando cada pedido
4. Um pedido apontado num slide vale para o deck inteiro, inclusive os componentes, as notas e as duas línguas. Procure os casos irmãos antes de fechar (p01:47-49,60,62-64,137).
5. Um item por passo: nunca agrupe itens no mesmo clique, salvo pedido explícito (p01:44-55; PED:28).
6. A legenda numerada sai do slide: esconda-a por CSS e mantenha a fonte no DOM para o QA. Uma legenda útil vira um rótulo curto, que diz o que se vê (p01:75,138; DEC:170,185).
7. A pergunta de pesquisa e a pergunta final vão com o texto completo; se não couberem, divida em mais slides. A resposta sai da seção de conclusões, e não de uma frase de efeito (p01:52-53,82,136,593).
8. Negrito só no rótulo antes dos dois-pontos, a partir de uma lista explícita; nunca no meio da frase (p01:125,131; DEC:177).
9. Para caber, encurte a redação. Nunca corte a fórmula nem o conteúdo técnico: o dono pediu a fórmula de volta (p01:130,163-167).
10. Quando o pedido vier só como captura de tela, diga em uma linha o que entendeu e aplique (p01:145,163).
11. O que o autor marcou como "NÃO TRAZER" ou "manter" vale à risca: não volte a propor o corte, mesmo que um revisor sugira (p01:118; PED:26-29).
12. Se a estrutura mudou (número de slides ou de passos), atualize junto o `docs/STORYLINE.md` (a checagem 3 compara os passos) e os testes que fixam essas contagens (DEC:169,189).
13. Quando o autor indicar decks de referência (colegas, banca), copie deles o formato institucional e registre de qual deck veio cada elemento (DEC:95-99,121).

## Registro e relatório
14. Cada decisão de julgamento entra no DECISIONS.md com um id ([tabelas-melhor]). As recusas entram como NÃO ENTROU, e uma decisão substituída é marcada, não apagada (p01:103-106; DEC:188,191).
15. O relatório vai em PT-BR, com a frase de resultado primeiro e depois as seções Onde está, O que entrou, Verificação e Precisa de você. Traz caminhos completos, números concretos, o que mudou além do pedido e o que olhar primeiro, e fecha com as decisões abertas numeradas, de sim ou não (p01:140-143,294-319; wf681:17).

Evidência: as regras foram mineradas das falas do autor do kit NEXUS-GO nas sessões do deck, das rodadas de crítica e dos documentos do kit; os códigos entre parênteses (p01, wfXXX, DEC, DES, INT, QA, COMP, STO, FIG, PED) apontam para essas fontes, que ficam fora do projeto. O NEXUS-GO aparece só como exemplo.
