# Feature: consultar-dispositivo

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → consultar-dispositivo

## Domain

licenciamento-geral

## Summary

Look up any provision of the general PR licensing framework (Lei 22.252/2024, Decreto 9.541/2025, Decreto 12.799/2026) by its LexML ID. Each article, caput, paragraph, inciso and alínea has a `{#id}` anchor and a bold label, so a RAG agent or an Obsidian reader can land on exactly one provision. Links of the form `[[norma#id]]` resolve to these anchors.

## Triggers

- Library entrypoint: wiki link `[[<norma>#<id>|label]]` resolved by Obsidian or a RAG retriever — README.md:61
- Library entrypoint: in-norma link `[[#<id>|label]]` — normas/decreto-estadual-9541-2025.md:210

## Public Interface

`README.md:48`

```markdown
| Artigo | `art5` | `###### Art. 5º {#art5}` |
| Caput | `art5_cpt` | `**Art. 5º, caput** {#art5_cpt}` |
| Parágrafo | `art5_par2` | `**Art. 5º, § 2º** {#art5_par2}` |
| Parágrafo único | `art5_par1u` | `**Art. 5º, parágrafo único** {#art5_par1u}` |
| Inciso do caput | `art5_cpt_inc3` | `- **Art. 5º, caput, inciso III** {#art5_cpt_inc3}` |
| Inciso de parágrafo | `art5_par2_inc3` | `- **Art. 5º, § 2º, inciso III** {#art5_par2_inc3}` |
| Alínea | `art5_cpt_inc3_alia` | `  - **Art. 5º, caput, inciso III, alínea "a"** {#art5_cpt_inc3_alia}` |
```

## Models

- LexML ID — string `art<N>[-<L>][_cpt|_par<N>|_par1u][_inc<N>][_ali<x>][_ite<N>]`
- Tags line — `Tags: #tag ...` under each article header
- [norma-frontmatter](../_models/norma-frontmatter.md) — identifies the norma being consulted

## Code Paths

- normas/lei-estadual-22252-2024.md:33 — first article anchor of the Lei
- normas/decreto-estadual-9541-2025.md:34 — first article anchor of the Decreto
- normas/decreto-estadual-9541-2025.md:182 — article-level `Tags:` line
- normas/decreto-estadual-9541-2025.md:208 — paragraph label with inline tags
- normas/decreto-estadual-9541-2025.md:1449 — Art. 173 caput (transition rule for pending procedures)
- scripts/validar.py:80 — checks label `Art. N` matches ID `artN`
- scripts/validar.py:83 — checks in-norma links resolve

## External References

_None._

## See Also

- [cadeia-regulamentar](../cadeia-regulamentar/feature.md) — cross-norma links between Lei and Decreto
- [converter-norma](../converter-norma/feature.md) — standard that creates the IDs
- [texto-compilado-alteracoes](../texto-compilado-alteracoes/feature.md) — amended provisions keep their IDs
- [validar-base](../validar-base/feature.md) — checks ID uniqueness and link targets

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
