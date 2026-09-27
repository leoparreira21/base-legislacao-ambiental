# Feature: modelos-anexos

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → modelos-anexos

## Domain

licenciamento-industrial

## Summary

Identify which declaration or certificate model an industrial licensing request must attach. Type 1 annexes of IN IAT 65/2025 (III, V, VI, VII, XV) are not transcribed; each annex section holds one line naming the model and a link to the article that requires it.

## Triggers

- Library entrypoint: annex section with model name and requiring article — normas/instrucao-normativa-iat-65-2025.md:1342

## Public Interface

`README.md:78`

```markdown
### Tipo 1: modelos (declarações, certidões, formulários, ART)
O conteúdo não é transcrito. A seção traz só uma linha: `Modelo de declaração de <nome da declaração>` (ou `Modelo de certidão de ...`, `Modelo de ...`), usando o nome dado pelo próprio texto da norma.
```

## Models

- Type 1 annex section — `### ANEXO N {#anexoN}` + `Tags: #anexo #modelo` + one `Modelo de ...` line

## Code Paths

- normas/instrucao-normativa-iat-65-2025.md:1339 — ANEXO III (municipal land-use certificate)
- normas/instrucao-normativa-iat-65-2025.md:1352 — ANEXO V (declaration of accuracy)
- normas/instrucao-normativa-iat-65-2025.md:1354 — ANEXO VI (LAC declaration, entrepreneur)
- normas/instrucao-normativa-iat-65-2025.md:1359 — ANEXO VII (LAC declaration, technical lead)
- normas/instrucao-normativa-iat-65-2025.md:1547 — ANEXO XV (employment-link declaration)
- normas/instrucao-normativa-iat-65-2025.md:20 — frontmatter `anexos` field classifying all annexes by type

## External References

_None._

## See Also

- [diretrizes-estudo-anexos](../diretrizes-estudo-anexos/feature.md) — type 2 annexes of the same IN
- [enquadramento-industrial](../enquadramento-industrial/feature.md) — type 3 annexes of the same IN

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
