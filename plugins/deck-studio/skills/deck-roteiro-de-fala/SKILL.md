---
name: deck-roteiro-de-fala
description: "Use ao escrever o roteiro.md, os cards de fala ou a narração de um deck do Deck Studio: um segmento por passo, orçamento de palavras, forma falada dos números e, se houver TTS, legendas e pronúncia."
---

# Roteiro de fala e narração

A criar-apresentacao define o `roteiro.md` (fase F), com uma entrada por estado de passo. Aqui ficam as regras de conteúdo.

## Roteiro
1. Cada segmento fala só do que o seu clique revela (wf681:9).
2. O orçamento de palavras usa a taxa MEDIDA da voz e da língua, e não um valor de fórmula: sintetize ou leia um trecho e cronometre. No NEXUS-GO (PT, Kokoro) deu cerca de 159 palavras por minuto contra os 150 da fórmula. A duração vem do briefing (wf681:9,15).
3. Antes de entregar, confira cada número e cada afirmação qualitativa do roteiro contra a fonte: "diminui" ou "cresce" só se a série fizer isso (p01:466-489; wf681:14).
4. O número falado leva o substantivo, para a concordância ("9.221 proteínas"). Não use primeira pessoa com gênero ("agradeço", e não "obrigado/a"). Contorne o termo sem pronúncia segura (wf681:9).

## Cards de fala (opcional)
5. Um card por slide, com 3 a 5 pontos, o tempo sugerido, o relógio acumulado e a frase de transição. Os cards vão na língua do autor, com um botão para a língua dos slides (p01:659,689-696,717-738).
6. Valem as mesmas regras de texto do deck: sem travessão e sem metacomentário (p01:728).

## Se houver vídeo ou TTS (fora da v1)
7. A tecla é pressionada no início do segmento e a voz entra depois (0,9 s em slide novo, 0,35 s em fragmento). As ações nos interativos usam os ids estáveis. O volume fica em −16 LUFS, e a sincronia é conferida contra deck.go(n, f) (DEC:73-92).
8. Pronúncia: confira com o Whisper sobre o MP4 final, não sobre o WAV, e ajuste o léxico até o termo voltar certo. Pergunte ao autor como se pronunciam os nomes de pessoas e ofereça amostras de voz (wf681:14,15; p01:460-462,481-488).
9. Legendas: não quebre a linha depois de artigo, preposição ou conjunção. Divida o tempo pelo comprimento falado e gere uma cópia com faixa abaixo do slide, para a legenda não cobrir as tabelas (wf681:15,17).

Evidência: as regras foram mineradas das falas do autor do kit NEXUS-GO nas sessões do deck, das rodadas de crítica e dos documentos do kit; os códigos entre parênteses (p01, wfXXX, DEC, DES, INT, QA, COMP, STO, FIG, PED) apontam para essas fontes, que ficam fora do projeto. O NEXUS-GO aparece só como exemplo.
