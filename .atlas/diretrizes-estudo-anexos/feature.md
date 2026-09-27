# Feature: diretrizes-estudo-anexos

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → diretrizes-estudo-anexos

## Domain

licenciamento-industrial

## Summary

Find which technical study an industrial license modality requires and what that study must contain. The type 2 annexes of IN IAT 65/2025 (IV MCE, VIII PBCA, IX PCPA, X noise, XI PGRS, XIII diagnosis) each live in their own file under `normas/anexos/`, filterable by `estudo`, `atividades` and `modalidades`. Each file holds the faithful annex text plus a separate, sourced "Síntese do conversor" that is not normative.

## Triggers

- Library entrypoint: IN body requires PBCA per Anexo VIII — normas/instrucao-normativa-iat-65-2025.md:411
- Library entrypoint: annex section in the parent norma links to the annex file — normas/instrucao-normativa-iat-65-2025.md:1347
- Library entrypoint: frontmatter filter `modalidades` — normas/anexos/instrucao-normativa-iat-65-2025-anexo8.md:9

## Public Interface

`README.md:86`

```yaml
anexo: ANEXO VIII
norma_mae: "[[instrucao-normativa-iat-65-2025]]"
arquivo: instrucao-normativa-iat-65-2025-anexo8
tipo_anexo: diretriz-estudo            # diretriz-estudo | termo-referencia
estudo: PBCA                           # sigla do estudo
atividades: [industria]                # atividades às quais o anexo se aplica
modalidades: [las, lasa, lasr]         # licenças em que o estudo é exigido
tags: [...]
```

## Models

- [norma-frontmatter](../_models/norma-frontmatter.md) — annex variant (`OBRIGATORIOS_ANEXO`)
- Annex line — `- **Anexo VIII, linha N** {#anexo8_linN} text`

## Code Paths

- normas/instrucao-normativa-iat-65-2025.md:1364 — ANEXO VIII stub section in the parent norma
- normas/anexos/instrucao-normativa-iat-65-2025-anexo8.md:4 — `norma_mae` back-link
- normas/anexos/instrucao-normativa-iat-65-2025-anexo8.md:20 — `## Texto do anexo` (faithful text)
- normas/anexos/instrucao-normativa-iat-65-2025-anexo8.md:216 — `## Síntese do conversor` (non-normative)
- normas/anexos/instrucao-normativa-iat-65-2025-anexo9.md:350 — largest synthesis (PCPA + terraplanagem)
- README.md:99 — subagent procedure: activity, interpretation, web research, formatting
- scripts/validar.py:69 — validator requires `norma_mae` in base and a Síntese section

## External References

_None._

## See Also

- [enquadramento-industrial](../enquadramento-industrial/feature.md) — classification decides the modality
- [glossario-termos](../glossario-termos/feature.md) — terms researched for the Síntese
- [modelos-anexos](../modelos-anexos/feature.md) — sibling annex handling (type 1)

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
