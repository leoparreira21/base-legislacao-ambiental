# Feature: gerar-tags

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → gerar-tags

## Domain

curadoria-base

## Summary

Regenerate `tags.md`, the registry of every thematic tag in use and how many normas use it. Converters consult it to reuse existing tags instead of inventing synonyms. The scan ignores IDs, wiki links and inline code so anchors are not counted as tags.

## Triggers

- CLI: `python scripts/validar.py --tags` — scripts/validar.py:134

## Public Interface

`scripts/validar.py:120`

```python
def gerar_tags(normas):
    uso = collections.Counter()
    for d in normas.values():
        limpo = re.sub(r"\{#[^}]+\}|\[\[[^\]]*\]\]|`[^`]*`", "", d["corpo"])
        uso.update(set(re.findall(r"(?<![\w/])#([a-z][a-z0-9-]*)", limpo)))
```

## Models

- Tag — `#` + lowercase, no accents, singular, hyphen-separated
- tags.md row — `| \`#tag\` | <count of normas> |`

## Code Paths

- scripts/validar.py:123 — strips IDs, links and code before scanning
- scripts/validar.py:124 — counts each tag once per norma
- scripts/validar.py:128 — writes `tags.md` at repo root
- tags.md:1 — generated registry
- README.md:68 — rule: reuse tags from `tags.md`
- README.md:69 — control tags `#revogado`, `#redacao-alterada`, `#incluido`

## External References

_None._

## See Also

- [converter-norma](../converter-norma/feature.md) — consumer of the registry
- [validar-base](../validar-base/feature.md) — same script, default mode

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
