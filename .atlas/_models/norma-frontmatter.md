# Model: norma-frontmatter

> Cross-feature shared-model leaf. ≤80 lines. Created ONLY when ≥3 features reference this model.

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Shared Models](../../ATLAS.md#shared-models) → norma-frontmatter

## Defined In

README.md:21 — documented schema; enforced by scripts/validar.py:25 (`OBRIGATORIOS`) and scripts/validar.py:27 (`OBRIGATORIOS_ANEXO`)

## Shape

`scripts/validar.py:25`

```python
OBRIGATORIOS = ["norma", "arquivo", "tipo", "esfera", "numero", "ano", "ementa", "situacao",
                "regulamenta", "altera", "alterado_por", "revoga", "revogado_por", "cita", "tags", "fonte"]
OBRIGATORIOS_ANEXO = ["anexo", "norma_mae", "arquivo", "tipo_anexo", "estudo", "atividades", "modalidades", "tags"]
SITUACOES = {"vigente", "revogada"}
```

Relation fields (`regulamenta`/`regulamentado_por`, `altera`/`alterado_por`, `revoga`/`revogado_por`) hold wiki-link lists and must be reciprocal. Optional fields seen in practice: `uf`, `data_assinatura`, `orgao`, `texto: compilado (...)`, `anexos`.

## Used By

- [cadeia-regulamentar](../cadeia-regulamentar/feature.md) — reads (relation fields)
- [converter-norma](../converter-norma/feature.md) — writes
- [diretrizes-estudo-anexos](../diretrizes-estudo-anexos/feature.md) — writes (annex variant)
- [listar-afetados](../listar-afetados/feature.md) — reads (`alterado_por`, `revogado_por`)
- [texto-compilado-alteracoes](../texto-compilado-alteracoes/feature.md) — writes (`alterado_por`, `texto`)
- [validar-base](../validar-base/feature.md) — reads

## Persistence

Stored as the YAML block between the first two `---` lines of each `.md` file in `normas/` and `normas/anexos/`. Parsed line by line with a regex (scripts/validar.py:31), not a YAML library, so each field must stay on one line.

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
