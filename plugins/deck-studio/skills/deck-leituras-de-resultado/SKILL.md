---
name: deck-leituras-de-resultado
description: "Use ao montar ou revisar slides de resultado (tabela, gráfico, frase de leitura) num deck do Deck Studio: marcação do melhor valor, forma do gráfico e leitura presa à métrica."
---

# Slides de resultado: tabela, gráfico e leitura

Complementa o ESTILO.md e os exemplos de tabela e gráfico da criar-apresentacao (06, 14 a 17). Aqui fica o critério de conteúdo.

## Tabela
1. Um resultado que compara várias rotas, modelos ou métodos vira tabela com TODAS as variantes, inclusive a que o artigo trata à parte (p01:133; p01:639).
2. O melhor valor vai em **negrito** e o segundo, sublinhado. Num empate, todos os empatados recebem a marca. Respeite o sentido da métrica (onde menor é melhor, o menor vence) e a orientação da tabela (por linha ou por coluna). O baseline ingênuo fica fora da disputa. Tabela sem "melhor" (corpus, custo, hiperparâmetros) fica sem marca (p01:145-161; wf681:14,17).
3. Aplique a marcação pelo mesmo critério em todas as tabelas, e registre o critério de cada uma no `docs/DECISIONS.md` (DEC:190).
4. Quando há uma tabela por categoria (dataset, ontologia, tarefa) e ela responde à pergunta de pesquisa, cada categoria ganha o próprio slide, com o mesmo layout, no corpo do deck e não no backup (wf681:4).

## Leituras (callouts)
5. O slide de resultado começa com a tabela sozinha. Depois vêm até 3 leituras, uma por clique, na coluna ao lado, e cada uma traz uma informação nova: a margem sobre o concorrente mais forte, de onde vem o ganho e a exceção. Não repita uma leitura em slides irmãos (wf681:4).
6. Toda leitura diz em qual métrica ela vale. Antes de escrever "melhor", "por pouco" ou "modestamente", confira a frase contra TODAS as colunas do slide. Se ela só vale numa coluna, nomeie a coluna ("Em wFmax, só...") (wf681:14,17).
7. Dê nome ao concorrente ("o baseline mais forte, X") e acompanhe a margem com a métrica secundária que concorda, como a fonte faz (wf681:4).
8. Os rótulos qualitativos obedecem aos limiares que o próprio deck declara. Se abaixo de X é empate, nada acima de X vira "empate"; use a forma da fonte ("no limite do piso de X") (wf681:14; STO:18-22).
9. Mantenha a precisão da fonte e o rótulo do split. Validação e teste nunca entram no mesmo gráfico; quando um slide mistura os dois, cada número diz de qual é (STO:18-22; DES:134-147).

## Gráfico
10. A forma segue o dado e a pergunta:
    - uma escada para a trajetória das médias;
    - um dumbbell para duas variantes em várias etapas;
    - um dot plot com eixo não-zero rotulado para diferenças pequenas, nunca barras truncadas;
    - anéis, um por termo, quando os escores não somam 1, nunca um donut dividido.

    A troca de forma vai para o DECISIONS (DEC:46,53; INT:192-206).
11. Barras com números ficam em escala, com valores reais e a fonte citada (base e versão). O rótulo diz o que o número mede de fato. Um número de fora do artigo só entra com o sim do autor (p01:45,77-80; PED:29).
12. Padrão de gráfico: um eixo; legenda com 2 ou mais séries e rótulo direto até 4; texto nunca na cor da série; tooltip; botão "tabela"; subtítulo com o split; métrica "menor é melhor" com eixo invertido e rotulado (DES:134-147).
13. Todo número de gráfico ou tabela vem do `docs/FACTS.md`, copiado exato no data-opts ou na célula, e a auditoria de números confere. Uma constante manual vai para o DECISIONS com a fonte (COMP:60-62; DEC:37-38,53).

Evidência: as regras foram mineradas das falas do autor do kit NEXUS-GO nas sessões do deck, das rodadas de crítica e dos documentos do kit; os códigos entre parênteses (p01, wfXXX, DEC, DES, INT, QA, COMP, STO, FIG, PED) apontam para essas fontes, que ficam fora do projeto. O NEXUS-GO aparece só como exemplo.
