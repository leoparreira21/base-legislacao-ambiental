# Feature: enquadramento-industrial

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → enquadramento-industrial

## Domain

licenciamento-industrial

## Summary

Classify an industrial enterprise under IN IAT 65/2025: size (porte), eligibility for simplified licensing (LAS), license validity and effluent discharge standards. The deciding tables are type 3 annexes (I, II, XII, XIV) transcribed inline, one self-contained list entry per table row with IDs like `anexo2_tab1_lin6`. Articles in the IN body link to these rows.

## Triggers

- Library entrypoint: porte definition linking Anexo I — normas/instrucao-normativa-iat-65-2025.md:142
- Library entrypoint: LAS eligibility linking Anexo II — normas/instrucao-normativa-iat-65-2025.md:260
- Library entrypoint: LO validity linking Anexo XII — normas/instrucao-normativa-iat-65-2025.md:562
- Library entrypoint: effluent standards linking Anexo XIV — normas/instrucao-normativa-iat-65-2025.md:1060

## Public Interface

`README.md:106`

```markdown
Cada entrada é autossuficiente: células mescladas são desfeitas repetindo o valor em cada linha, linhas partidas entre páginas são unidas e cabeçalhos repetidos por página são removidos (registrar isso nas Notas de transcrição). Formato de uma linha de tabela:
- **Anexo II, Tabela 1, linha 6** {#anexo2_tab1_lin6} #industria-madeira Tipologia: ... | Atividade: ... | Limite: ...
```

## Models

- Type 3 table row — `- **Anexo N, Tabela T, linha M** {#anexoN_tabT_linM} #tags Col: val | Col: val`
- Type 3 provision — `- **Anexo N, linha M** {#anexoN_linM} text`

## Code Paths

- normas/instrucao-normativa-iat-65-2025.md:1212 — ANEXO I section (porte)
- normas/instrucao-normativa-iat-65-2025.md:1218 — first porte table row
- normas/instrucao-normativa-iat-65-2025.md:1230 — first LAS activity row (Anexo II)
- normas/instrucao-normativa-iat-65-2025.md:1391 — first validity row (Anexo XII)
- normas/instrucao-normativa-iat-65-2025.md:1440 — first discharge-standard provision (Anexo XIV)
- normas/instrucao-normativa-iat-65-2025.md:1572 — Notas de transcrição (table merges recorded)

## External References

_None._

## See Also

- [diretrizes-estudo-anexos](../diretrizes-estudo-anexos/feature.md) — studies required once the activity is classified
- [modelos-anexos](../modelos-anexos/feature.md) — sibling annex handling (type 1)

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
