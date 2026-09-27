# Feature: cadeia-regulamentar

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → cadeia-regulamentar

## Domain

licenciamento-geral

## Summary

Navigate the hierarchy between normas: Decreto 9.541/2025 regulates Lei 22.252/2024, and Decreto 12.799/2026 amends the Decreto. The chain is declared in reciprocal frontmatter fields and backed by provision-level links in the body. Citations to normas not yet in the base stay as pending links.

## Triggers

- Library entrypoint: frontmatter `regulamenta` / `regulamentado_por` lists — normas/decreto-estadual-9541-2025.md:13
- Library entrypoint: body link to the regulated Lei — normas/decreto-estadual-9541-2025.md:1081

## Public Interface

`normas/decreto-estadual-9541-2025.md:13`

```yaml
regulamenta: ["[[lei-estadual-22252-2024]]"]
altera: []
alterado_por: ["[[decreto-estadual-12799-2026]]"]
revogado_por: []
```

## Models

- [norma-frontmatter](../_models/norma-frontmatter.md) — relation fields `regulamenta`, `altera`, `revoga`, `cita` and their reciprocals

## Code Paths

- normas/lei-estadual-22252-2024.md:16 — `regulamentado_por` back-reference to the Decreto
- normas/decreto-estadual-9541-2025.md:13 — `regulamenta` forward reference to the Lei
- normas/decreto-estadual-12799-2026.md:18 — `altera` reference to Decreto 9.541
- README.md:43 — rule: relations are reciprocal
- README.md:63 — rule: pending links to normas outside the base
- scripts/validar.py:88 — warns on cited normas not in the base
- scripts/validar.py:91 — errors on non-reciprocal relations

## External References

_None._

## See Also

- [consultar-dispositivo](../consultar-dispositivo/feature.md) — links resolve to provision IDs
- [texto-compilado-alteracoes](../texto-compilado-alteracoes/feature.md) — the `altera` edge drives compiled text
- [validar-base](../validar-base/feature.md) — enforces reciprocity

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
