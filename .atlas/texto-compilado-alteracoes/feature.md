# Feature: texto-compilado-alteracoes

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → texto-compilado-alteracoes

## Domain

licenciamento-geral

## Summary

Keep an amended norma as compiled text instead of deleting or replacing it. Decreto 12.799/2026 revokes and rewrites provisions of Decreto 9.541/2025; the affected file shows current wording normally and old wording struck through, with control tags and an amendment history table. The old text still governs procedures filed before the change (Art. 173 of Decreto 9.541).

## Triggers

- Library entrypoint: amending provision quoted with its own ID — normas/decreto-estadual-12799-2026.md:40
- Library entrypoint: `#redacao-alterada` provision in the amended norma — normas/decreto-estadual-9541-2025.md:208

## Public Interface

`README.md:118`

```markdown
| Nova redação | O texto novo fica no lugar, seguido de `*(Redação dada pelo [[norma-nova#artN\|Decreto nº X/AAAA]])*`. A redação original fica logo abaixo, tachada: `> Redação original: ~~...~~`. O dispositivo recebe `#redacao-alterada`. |
| Dispositivo acrescentado | É inserido na posição correta, com ID novo, `#incluido` e `*(Incluído pelo [[...]])*`. |
| Revogação de dispositivo | O texto fica tachado `~~...~~`, com `#revogado` e `*(Revogado pelo [[...]])*`. O ID não muda. |
```

## Models

- Amendment history row — `| Norma | Dispositivo | Alteração |`
- Control tags — `#revogado`, `#redacao-alterada`, `#incluido`
- [norma-frontmatter](../_models/norma-frontmatter.md) — `alterado_por` and `texto: compilado (...)`

## Code Paths

- normas/decreto-estadual-9541-2025.md:17 — `texto: compilado (atualizado até o Decreto nº 12.799/2026)`
- normas/decreto-estadual-9541-2025.md:183 — article `Alterações:` summary line
- normas/decreto-estadual-9541-2025.md:210 — original wording kept struck through
- normas/decreto-estadual-9541-2025.md:537 — revocation plus inclusion summary (Art. 56)
- normas/decreto-estadual-9541-2025.md:1516 — `## Histórico de alterações` table
- normas/decreto-estadual-9541-2025.md:1449 — Art. 173: old text governs earlier procedures
- CLAUDE.md:6 — rule: never delete an amended or revoked norma file

## External References

_None._

## See Also

- [cadeia-regulamentar](../cadeia-regulamentar/feature.md) — `altera` / `alterado_por` edge
- [consultar-dispositivo](../consultar-dispositivo/feature.md) — IDs stay stable after amendment
- [converter-norma](../converter-norma/feature.md) — conversion workflow applies these rules
- [listar-afetados](../listar-afetados/feature.md) — finds links to amended provisions

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
