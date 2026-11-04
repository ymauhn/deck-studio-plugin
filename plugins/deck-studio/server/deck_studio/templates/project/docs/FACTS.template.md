# FACTS: todo número que o deck pode mostrar

Copie para `docs/FACTS.md` e preencha na fase B, ANTES de escrever os slides. Regra: um número só entra num slide se
estiver na fonte (o `texto.md` extraído, ou um .md/.tex da pasta `context/`) ou nesta tabela com a origem dele.
`qa/audit_numbers.py` confere isso em cada slide.

- **Da fonte:** copie o número como a fonte o imprime (no deck em português, só a vírgula decimal muda).
- **Derivado** (uma diferença, uma razão): escreva a conta e a origem dos dois números. O auditor aceita os números
  desta tabela.
- **Externo** (fora da fonte): só se o briefing autorizou (`fatos: "fonte+externos"`), com a referência completa.

## 1. Pessoas, evento, datas

- Autor(es): [como a fonte escreve] (p. 1)
- Instituição: [...] (p. 1)
- Evento e data: [do briefing, ou "[evento e data]" se ninguém disse]

## 2. Números

| Número | O que é | Origem | Trecho |
|---|---|---|---|
| [73,18] | [métrica do método X no conjunto Y] | p. [12], Tab. [3] | "[o trecho da fonte]" |
| [+2,15] | [ganho de X sobre Y] | derivado: 73,18 - 71,03 (p. 12, Tab. 3) | |
