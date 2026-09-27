# Feature: validar-base

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → validar-base

## Domain

curadoria-base

## Summary

Validate the whole corpus before a commit with `python scripts/validar.py`. It checks required frontmatter fields, file name vs `arquivo`, unique IDs, label/ID coherence, internal and cross-norma link targets, reciprocal relations and annex structure. Errors exit with code 1 and block the commit; pending links to normas outside the base are only warnings.

## Triggers

- CLI: `python scripts/validar.py` — scripts/validar.py:138

## Public Interface

`scripts/validar.py:56`

```python
def validar(normas):
    erros, avisos = [], []
    ids = {n: ids_de(d["corpo"]) for n, d in normas.items()}
    for n, d in normas.items():
        fm, corpo = d["fm"], d["corpo"]
        ...
    return erros, avisos
```

## Models

- [norma-frontmatter](../_models/norma-frontmatter.md) — required fields and `situacao` values
- Loaded norma — `{fm: dict, corpo: str, erro_fm: bool}` keyed by file basename

## Code Paths

- scripts/validar.py:31 — `carregar()` reads `normas/` and `normas/anexos/`, splits frontmatter
- scripts/validar.py:52 — `ids_de()` extracts `{#id}` anchors
- scripts/validar.py:80 — label `Art. N` vs ID coherence
- scripts/validar.py:85 — cross-norma link targets must exist
- scripts/validar.py:91 — reciprocal relation check
- scripts/validar.py:143 — summary line and exit code

## External References

_None._

## See Also

- [cadeia-regulamentar](../cadeia-regulamentar/feature.md) — reciprocity rules checked here
- [consultar-dispositivo](../consultar-dispositivo/feature.md) — ID and link integrity
- [converter-norma](../converter-norma/feature.md) — commit gate in the conversion workflow
- [gerar-tags](../gerar-tags/feature.md) — same script, `--tags` mode
- [listar-afetados](../listar-afetados/feature.md) — same script, `--afetados` mode

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
