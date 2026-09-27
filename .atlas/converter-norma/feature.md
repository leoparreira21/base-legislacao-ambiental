# Feature: converter-norma

## Breadcrumb

[base-legislacao-ambiental](../../ATLAS.md) → [Features](../INDEX.md) → converter-norma

## Domain

curadoria-base

## Summary

Convert a newly published norma into a Markdown file that follows the base's standard. The README fixes file naming, frontmatter, LexML IDs, links, tags, faithful transcription and annex handling; CLAUDE.md turns it into agent rules (validate with 0 errors, show changes before commit, commit message format). Transcription errors in the original go to `## Notas de transcrição`, not into the text.

## Triggers

- CLI (agent workflow): "converter ou atualizar qualquer norma" — CLAUDE.md:3
- Commit convention: `norma: <arquivo> (nova | altera <arquivo> | revoga <arquivo>)` — CLAUDE.md:11

## Public Interface

`CLAUDE.md:5`

```markdown
Regras principais:
- Nunca apague o arquivo de uma norma alterada ou revogada. Atualize-o como texto compilado.
- Transcreva o texto exatamente como publicado e registre os erros do original em "Notas de transcrição".
- Anexos: siga a seção "Anexos" do README (tipo 1 ...; tipo 2 ...; tipo 3 ...). Consulte glossario.md antes de pesquisar termos na web.
- Rode `python scripts/validar.py` e só faça commit com 0 erros.
- Mostre as mudanças ao usuário antes do commit e sinalize revogação tácita, remissões erradas e vigência diferida.
- Mensagem de commit: `norma: <arquivo> (nova | altera <arquivo> | revoga <arquivo>)`.
```

## Models

- [norma-frontmatter](../_models/norma-frontmatter.md) — header the conversion writes
- File name — `tipo-orgao/esfera-numero-ano.md`, lowercase, no accents

## Code Paths

- README.md:18 — file-naming rule
- README.md:21 — frontmatter schema
- README.md:48 — LexML ID table
- README.md:68 — reuse tags from `tags.md`
- README.md:72 — faithful transcription rule
- README.md:76 — annex handling (types 1/2/3)
- normas/instrucao-normativa-iat-65-2025.md:1572 — example `## Notas de transcrição`

## External References

_None._

## See Also

- [consultar-dispositivo](../consultar-dispositivo/feature.md) — IDs produced by conversion
- [gerar-tags](../gerar-tags/feature.md) — tag registry to reuse
- [glossario-termos](../glossario-termos/feature.md) — consult before web research
- [texto-compilado-alteracoes](../texto-compilado-alteracoes/feature.md) — rules when the new norma amends another
- [validar-base](../validar-base/feature.md) — mandatory gate before commit

## Last Verified

58febea59faa7f4c0e10c4dd41e0ba3eac428aa1 (2026-09-27)
