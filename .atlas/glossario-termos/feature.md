# Feature: glossario-termos

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → glossario-termos

## Domain

curadoria-base

## Summary

Reuse technical terms already researched while interpreting type 2 annexes. `glossario.md` is a table of term, short definition, source and where it is used. Agents consult it before searching the web and append new terms after research.

## Triggers

- Agent workflow: consult glossary before web research — CLAUDE.md:8
- Agent workflow: researched terms also go into the glossary — README.md:97

## Public Interface

`glossario.md:5`

```markdown
| Termo | Definição (resumo) | Fonte | Usado em |
|---|---|---|---|
```

## Models

- Glossary row — `| Termo | Definição (resumo) | Fonte | Usado em |`

## Code Paths

- glossario.md:3 — purpose: consult before web research, append after
- glossario.md:5 — table header
- glossario.md:7 — example row (ABNT waste standards)
- README.md:12 — glossary listed in repo structure
- README.md:99 — subagent procedure step (c) uses the glossary

## External References

_None._

## See Also

- [converter-norma](../converter-norma/feature.md) — conversion rules reference the glossary
- [diretrizes-estudo-anexos](../diretrizes-estudo-anexos/feature.md) — Síntese sections cite glossary terms

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
