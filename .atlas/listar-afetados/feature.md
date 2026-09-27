# Feature: listar-afetados

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → listar-afetados

## Domain

curadoria-base

## Summary

After an amendment, list links in other normas that point at revoked or rewritten provisions of the amended norma. It collects IDs on lines tagged `#revogado` or `#redacao-alterada`, then scans every other norma for `[[<norma>#<id>]]` links to them or their children. The amending normas themselves are skipped, since they point there on purpose.

## Triggers

- CLI: `python scripts/validar.py --afetados <norma>` — scripts/validar.py:136

## Public Interface

`scripts/validar.py:100`

```python
def afetados(normas, alvo):
    corpo = normas[alvo]["corpo"]
    mudou = set()
    for linha in corpo.splitlines():
        if re.search(r"#revogado\b|#redacao-alterada\b", linha):
            mudou.update(re.findall(r"\{#([\w-]+)\}", linha))
```

## Models

- [norma-frontmatter](../_models/norma-frontmatter.md) — `alterado_por` / `revogado_por` exclude the authors

## Code Paths

- scripts/validar.py:104 — detects changed provisions by control tag
- scripts/validar.py:107 — skips amending normas
- scripts/validar.py:112 — scans other normas for links to the target
- scripts/validar.py:113 — matches the ID or any child ID (`<id>_...`)
- scripts/validar.py:117 — "nothing affected" message
- README.md:135 — documented usage

## External References

_None._

## See Also

- [texto-compilado-alteracoes](../texto-compilado-alteracoes/feature.md) — produces the control tags scanned here
- [validar-base](../validar-base/feature.md) — same script, default mode

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
