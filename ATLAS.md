# base-legislacao-ambiental

> One-screen home for `base-legislacao-ambiental`. ≤80 lines. Cover-only — chapter detail lives in `.atlas/`.

## Summary

A Markdown corpus of Paraná (PR) state environmental-licensing law, one norma per file. Each provision carries a LexML-style ID, cross-norma wiki links and thematic tags. The base is built for RAG retrieval by AI agents and for reading in Obsidian. A small Python script validates the corpus before every commit.

## Domain & Purpose

The repo owns the transcription and curation of environmental-licensing normas: the general state framework (Lei 22.252/2024, Decreto 9.541/2025 and its amendment Decreto 12.799/2026) and the industrial-licensing rules of IN IAT 65/2025 with its annexes. Amended normas are kept as compiled text, never deleted. Out of scope: legal interpretation beyond the converter's clearly separated "Síntese" sections, federal/municipal normas not yet added (their links stay pending), and any runtime application.

## Tech Stack

- Language(s): Markdown (Obsidian-flavoured wiki links, YAML frontmatter); Python 3 (stdlib only) for validation
- Framework(s): none
- Datastores: flat files under `normas/` and `normas/anexos/`
- Build / runtime: `python scripts/validar.py`; no CI

## Owners

- @leoparreira21 — whole repo (no CODEOWNERS file)

## Domains

- curadoria-base — conversion standard, validation CLI, tag registry and glossary that keep the corpus consistent
- licenciamento-geral — general PR licensing framework: Lei 22.252/2024, Decreto 9.541/2025, Decreto 12.799/2026
- licenciamento-industrial — IN IAT 65/2025 for industrial enterprises, including its type 1/2/3 annexes

## Shared Models

- [norma-frontmatter](.atlas/_models/norma-frontmatter.md) — YAML header every norma and annex file carries

## Index

- [Feature index](.atlas/INDEX.md)
- [Glossary](.atlas/glossary.md)

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
