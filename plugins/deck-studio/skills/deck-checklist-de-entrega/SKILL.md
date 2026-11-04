---
name: deck-checklist-de-entrega
description: "Use antes de entregar qualquer versão de um deck do Deck Studio, depois do `mcp__plugin_deck-studio_deck__run_qa` (qa/check_deck.py e qa/audit_numbers.py): as checagens que os revisores pegaram e os scripts não pegam, e os anti-padrões."
---

# Checklist de entrega (complementa a RUBRICA e os scripts de QA)

## Fidelidade
1. Leia o artigo inteiro e confira o storyline contra ele. Quando o artigo tem splits, marque o que é validação e o que é teste (p01:259,265).
2. Além dos números, confira as afirmações qualitativas (tendência, "monotônico", "diminui") contra a série real (wf681:9,14).
3. Confira a aritmética das diferenças derivadas (a − b = margem) (wf681:4).
4. Quando uma figura contradiz o texto, recorte-a ou desenhe um diagrama novo, registre o porquê e avise o autor. Não corrija a fonte em silêncio (p01:686; QA:7-21; FIG:46-58).
5. No slide, cite como "Autor (ano)" e ponha a lista no backup; nunca deixe "[20]" solto. As notas citam a página da fonte (wf7a4:16,22; wf13f:3).

## Visual
6. As figuras são reais: nenhum retângulo preto, nenhuma máscara solta, nenhuma figura vetorial perdida. Recorte a região a partir da legenda "Fig. N" (wf7a4:16).
7. Um título longo (mais de 100 caracteres) usa o padrão de título longo, e o evento e a data não saem do slide (wf7a4:16,22).
8. Renderize tudo, monte as folhas de contato e olhe uma a uma as páginas que mudaram. Confira:
   - nada fora do quadro e nenhum rótulo cortado;
   - nenhuma quebra feia (parêntese sozinho no fim da linha, hifenização);
   - o slide não "pula" entre cliques (o diff de pixels fica só na área revelada).

   (wf681:6; wf772:15,17)
9. O Beamer compila a partir de uma pasta vazia com 0 erros, 0 Overfull e 0 referências indefinidas, e o texto é idêntico ao do PDF local (wf681:4; wf13f:3).
10. Zero travessões como pontuação nos slides, nas notas, no roteiro e na bibliografia. O en dash só aparece em intervalo numérico (wf681:4,6,14).

## Anti-padrões que os juízes pegaram
11. Placeholder que parece conteúdo ("Dissertação de mestrado" no campo do autor) (wf13f:3).
12. Callout que vale numa métrica e é falso noutra coluna do mesmo slide (wf681:14).
13. "Empate" acima do limiar que o próprio deck define (wf681:14).
14. Só o primeiro dos empatados em negrito (wf681:14).
15. Suíte que falha por uma contagem fixa depois de uma mudança de estrutura (DEC:189).
16. Cara de "slide de IA": gradiente roxo-azul, emoji, ícone como marcador, card com sombra em tudo, corpo centralizado, ilustração de IA, texto na cor da série (DES:108-109,150-154).

## Relatório honesto
17. Diga o que a captura parada não prova (a velocidade e a sequência da animação) e o que não foi rodado (p01:11,19,71).

Evidência: as regras foram mineradas das falas do autor do kit NEXUS-GO nas sessões do deck, das rodadas de crítica e dos documentos do kit; os códigos entre parênteses (p01, wfXXX, DEC, DES, INT, QA, COMP, STO, FIG, PED) apontam para essas fontes, que ficam fora do projeto. O NEXUS-GO aparece só como exemplo.
