# Feature Index — base-legislacao-ambiental

> Single index for the whole repo. Features grouped by `## Domains` tag from the cover. ≤200 lines. Alphabetical within each domain.

## Features by Domain

### Domain: curadoria-base

- [converter-norma](converter-norma/feature.md) — Convert a newly published norma into a Markdown file that follows the base's standard.
- [gerar-tags](gerar-tags/feature.md) — Regenerate `tags.md`, the registry of every thematic tag in use and how many normas use it.
- [glossario-termos](glossario-termos/feature.md) — Reuse technical terms already researched while interpreting type 2 annexes.
- [listar-afetados](listar-afetados/feature.md) — After an amendment, list links in other normas that point at revoked or rewritten provisions of the amended norma.
- [validar-base](validar-base/feature.md) — Validate the whole corpus before a commit with `python scripts/validar.py`.

### Domain: licenciamento-geral

- [cadeia-regulamentar](cadeia-regulamentar/feature.md) — Navigate the hierarchy between normas: Decreto 9.541/2025 regulates Lei 22.252/2024, and Decreto 12.799/2026 amends the Decreto.
- [consultar-dispositivo](consultar-dispositivo/feature.md) — Look up any provision of the general PR licensing framework (Lei 22.252/2024, Decreto 9.541/2025, Decreto 12.799/2026) by its LexML ID.
- [texto-compilado-alteracoes](texto-compilado-alteracoes/feature.md) — Keep an amended norma as compiled text instead of deleting or replacing it.

### Domain: licenciamento-industrial

- [diretrizes-estudo-anexos](diretrizes-estudo-anexos/feature.md) — Find which technical study an industrial license modality requires and what that study must contain.
- [enquadramento-industrial](enquadramento-industrial/feature.md) — Classify an industrial enterprise under IN IAT 65/2025: size (porte), eligibility for simplified licensing (LAS), license validity and effluent discharge standards.
- [modelos-anexos](modelos-anexos/feature.md) — Identify which declaration or certificate model an industrial licensing request must attach.

## Cross-References

- [Glossary](glossary.md)
- [Shared model: norma-frontmatter](_models/norma-frontmatter.md)
